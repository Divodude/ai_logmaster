import os
import re
from typing import List, Dict, Tuple

class CodebaseIngestor:
    """Ingests local codebase context based on error tracebacks."""
    
    def __init__(self, context_lines_limit: int = 200):
        """
        Initialize the ingestor.
        
        Args:
            context_lines_limit: Maximum total lines to extract per file to avoid token overflow.
        """
        self.context_lines_limit = context_lines_limit
        # Regex to match Python traceback file lines: File "/path/to/file.py", line 42, in <module>
        self.traceback_regex = re.compile(r'File\s+"([^"]+)",\s+line\s+(\d+)')
        
    def extract_files_from_traceback(self, error_context: str) -> List[Tuple[str, int]]:
        """
        Extract file paths and line numbers from the error traceback.
        
        Args:
            error_context: The raw error output from the console.
            
        Returns:
            List of tuples (file_path, line_number)
        """
        files_and_lines = []
        for line in error_context.split('\n'):
            match = self.traceback_regex.search(line)
            if match:
                file_path, line_num = match.groups()
                files_and_lines.append((file_path, int(line_num)))
        return files_and_lines
        
    def get_codebase_context(self, error_context: str) -> str:
        """
        Extract and read relevant code blocks for an error.
        
        Args:
            error_context: The raw error output from console.
            
        Returns:
            A formatted string containing the codebase context.
        """
        files_and_lines = self.extract_files_from_traceback(error_context)
        if not files_and_lines:
            return ""
            
        context_blocks = []
        processed_files = set()
        
        for file_path, line_num in reversed(files_and_lines): # Process deepest calls first
            # Skip standard library and site-packages to focus on user code
            if 'site-packages' in file_path or 'Python' in file_path and 'lib' in file_path.lower():
                continue
                
            # Keep track so we don't read the same file multiple times if it has multiple frames
            file_key = os.path.abspath(file_path)
            if file_key in processed_files:
                continue
                
            if os.path.exists(file_path) and os.path.isfile(file_path):
                content = self._read_file_snippet(file_path, line_num)
                if content:
                    context_blocks.append(content)
                    processed_files.add(file_key)
                    
        if not context_blocks:
            return ""
            
        final_context = "=== CODEBASE CONTEXT ===\n" 
        final_context += "The following are snippets from the user's project where the error occurred:\n\n"
        final_context += "\n\n".join(context_blocks)
        final_context += "\n========================\n"
        return final_context
        
    def _read_file_snippet(self, file_path: str, target_line: int) -> str:
        """Read lines from a file centered around the target line."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            total_lines = len(lines)
            if total_lines == 0:
                return ""
                
            half_limit = self.context_lines_limit // 2
            
            # 1-indexed to 0-indexed
            target_idx = target_line - 1
            
            start_idx = max(0, target_idx - half_limit)
            end_idx = min(total_lines, target_idx + half_limit)
            
            snippet = f"--- File: {file_path} (Lines {start_idx + 1}-{end_idx}) ---\n"
            for i in range(start_idx, end_idx):
                prefix = ">> " if i == target_idx else "   "
                snippet += f"{prefix}{i + 1:4d}: {lines[i].rstrip()}\n"
                
            return snippet
        except Exception as e:
            print(f"[INGESTOR] Failed to read {file_path}: {e}")
            return ""
