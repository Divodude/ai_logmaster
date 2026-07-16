"""
Auto Fixer - Uses the LLM to generate and apply code fixes directly to source files.
Shows a colored diff and asks for user confirmation before writing anything.
"""
import os
import re
import difflib
from typing import Dict, List, Tuple, Optional


class AutoFixer:
    """
    Generates and optionally applies AI-powered patches to local source files.
    
    Workflow:
        1. Receive the analysis result + list of (file_path, line_number) tuples.
        2. For each fixable user file, call the LLM to produce the corrected full content.
        3. Compute a unified diff and display it to the user with color coding.
        4. Ask "Apply this fix? [y/N]" (safe default = N).
        5. If accepted, write the fixed content to disk.
    """

    def __init__(self, llm=None):
        """
        Args:
            llm: An already-initialised LangChain chat model (e.g. ChatGroq instance).
        """
        if llm is None:
            from .llm_manager import GlobalLLMManager
            self.llm = GlobalLLMManager().get_llm()
        else:
            self.llm = llm

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def attempt_fix(
        self,
        error_context: str,
        analysis: Dict,
        files_and_lines: List[Tuple[str, int]],
        auto_confirm: bool = False,
    ) -> bool:
        """
        Main entry point.  Tries to auto-fix every user-owned file in the traceback.

        Args:
            error_context:  The raw error output captured from the terminal.
            analysis:       The result dict returned by ErrorAnalyzer.analyze().
            files_and_lines: List of (file_path, line_number) from CodebaseIngestor.
            auto_confirm:   If True, apply without asking (use with caution).

        Returns:
            True if at least one file was patched, False otherwise.
        """
        if not self.llm:
            print("[AUTO_FIXER] LLM not available – skipping auto-fix.")
            return False

        # Filter to user-owned files only (skip site-packages / stdlib)
        user_files = self._filter_user_files(files_and_lines)
        if not user_files:
            print("[AUTO_FIXER] No user-owned source files found in traceback.")
            return False

        any_fixed = False
        for file_path, line_num in user_files:
            print(f"\n[AUTO_FIXER] Generating fix for: {file_path}")
            fixed = self._fix_file(
                file_path, line_num, error_context, analysis, auto_confirm
            )
            if fixed:
                any_fixed = True

        return any_fixed

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _filter_user_files(
        self, files_and_lines: List[Tuple[str, int]]
    ) -> List[Tuple[str, int]]:
        """Keep only the deepest call frame per file that belongs to user code."""
        skip_patterns = ["site-packages", os.sep + "lib" + os.sep, "frozen importlib"]
        seen = set()
        result = []
        for fp, ln in reversed(files_and_lines):  # deepest first
            if any(p in fp for p in skip_patterns):
                continue
            if not os.path.isfile(fp):
                continue
            key = os.path.abspath(fp)
            if key not in seen:
                seen.add(key)
                result.append((fp, ln))
        return result

    def _fix_file(
        self,
        file_path: str,
        target_line: int,
        error_context: str,
        analysis: Dict,
        auto_confirm: bool,
    ) -> bool:
        """Ask the LLM to fix `file_path`, show a diff, and optionally apply it."""
        try:
            original_lines = open(file_path, "r", encoding="utf-8").readlines()
        except Exception as e:
            print(f"[AUTO_FIXER] Cannot read {file_path}: {e}")
            return False

        original_text = "".join(original_lines)

        # Build a focused snippet around the error (max 200 lines)
        half = 100
        start = max(0, target_line - 1 - half)
        end = min(len(original_lines), target_line - 1 + half)
        snippet = "".join(original_lines[start:end])

        fixed_text = self._ask_llm_for_fix(
            file_path, snippet, start + 1, error_context, analysis
        )

        if not fixed_text:
            print("[AUTO_FIXER] LLM returned no fix.")
            return False

        # Merge: replace only the touched region, keep the rest intact
        before = "".join(original_lines[:start])
        after = "".join(original_lines[end:])
        patched_text = before + fixed_text + after

        if patched_text.strip() == original_text.strip():
            print("[AUTO_FIXER] No changes needed – file is already correct.")
            return False

        # Show the diff
        self._print_diff(file_path, original_text, patched_text)

        # Confirm
        if auto_confirm:
            apply = True
        else:
            answer = input(
                "\n[AUTO_FIXER] Apply this fix? [y/N] "
            ).strip().lower()
            apply = answer in ("y", "yes")

        if apply:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(patched_text)
                print(f"[AUTO_FIXER] ✅ Fix applied to {file_path}")
                return True
            except Exception as e:
                print(f"[AUTO_FIXER] ❌ Failed to write fix: {e}")
                return False
        else:
            print("[AUTO_FIXER] Fix skipped.")
            return False

    def _ask_llm_for_fix(
        self,
        file_path: str,
        snippet: str,
        start_line: int,
        error_context: str,
        analysis: Dict,
    ) -> Optional[str]:
        """Call the LLM and extract the corrected code block."""
        try:
            from langchain_core.messages import HumanMessage, SystemMessage

            cause = analysis.get("cause", "")
            fixes = "\n".join(
                f"- {f}" for f in analysis.get("fixes", [])
            )

            system = SystemMessage(
                content=(
                    "You are an expert Python developer and code repair agent.\n"
                    "Your task is to output ONLY the corrected Python code snippet to replace the original snippet.\n"
                    "CRITICAL RULES:\n"
                    "1. DO NOT remove any existing comments, docstrings, or code that is not related to the error.\n"
                    "2. Preserve the exact indentation and structure of the original code.\n"
                    "3. Return ONLY the code with no markdown fences, no explanations, no extra text."
                )
            )

            human = HumanMessage(
                content=(
                    f"File: {file_path} (starting at line {start_line})\n\n"
                    f"=== ERROR ===\n{error_context[:800]}\n\n"
                    f"=== ROOT CAUSE ===\n{cause}\n\n"
                    f"=== SUGGESTED FIXES ===\n{fixes}\n\n"
                    f"=== CODE SNIPPET TO FIX ===\n{snippet}\n\n"
                    "Return ONLY the corrected code snippet preserving all comments and docstrings."
                )
            )

            response = self.llm.invoke([system, human])
            raw = response.content.strip()

            # Strip accidental markdown fences if the LLM adds them
            raw = re.sub(r"^```[a-zA-Z]*\n?", "", raw)
            raw = re.sub(r"\n?```$", "", raw)

            # Ensure the snippet ends with a newline
            if raw and not raw.endswith("\n"):
                raw += "\n"

            return raw

        except Exception as e:
            print(f"[AUTO_FIXER] LLM call failed: {e}")
            return None

    def _print_diff(self, file_path: str, original: str, patched: str):
        """Print a human-readable unified diff with ANSI colour coding."""
        diff = list(
            difflib.unified_diff(
                original.splitlines(keepends=True),
                patched.splitlines(keepends=True),
                fromfile=f"a/{os.path.basename(file_path)}",
                tofile=f"b/{os.path.basename(file_path)} (fixed)",
                lineterm="",
            )
        )

        print("\n" + "─" * 60)
        print(f"  PROPOSED CHANGES  →  {file_path}")
        print("─" * 60)

        RED = "\033[91m"
        GREEN = "\033[92m"
        CYAN = "\033[96m"
        RESET = "\033[0m"

        for line in diff:
            stripped = line.rstrip("\n")
            if stripped.startswith("---") or stripped.startswith("+++"):
                print(f"{CYAN}{stripped}{RESET}")
            elif stripped.startswith("@@"):
                print(f"{CYAN}{stripped}{RESET}")
            elif stripped.startswith("-"):
                print(f"{RED}{stripped}{RESET}")
            elif stripped.startswith("+"):
                print(f"{GREEN}{stripped}{RESET}")
            else:
                print(stripped)

        print("─" * 60)
