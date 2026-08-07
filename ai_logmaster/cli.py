#!/usr/bin/env python3
"""
Standalone Smart Log Analyzer
Wraps any command, captures output, detects errors, and provides AI-powered solutions.
"""
import sys
import subprocess
import argparse
import json
import io
import time
import threading
import queue
from collections import deque

# Fix Unicode encoding on Windows terminals (cp1252 can't handle emojis)
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Load .env file so GROQ_API_KEY etc. are available before any imports
from dotenv import load_dotenv
load_dotenv()


# Error detection patterns
ERROR_KEYWORDS = [
    "ERROR", "CRITICAL", "EXCEPTION", "TRACEBACK", 
    "FAILED", "FATAL", "PANIC", "CRASH", "ERRNO",
    "NO SUCH FILE", "NOT FOUND", "CAN'T OPEN FILE"
]

class _SilentStream(io.StringIO):
    """A /dev/null stream for suppressing prints in JSON mode."""
    def write(self, s): return len(s) if s else 0
    def flush(self): pass


class TriageWrapper:
    def __init__(self, buffer_size=100, auto_fix=False, independent=False, auto_recover=False, json_mode=False):
        self.buffer = deque(maxlen=buffer_size)
        self.error_detected = False
        self.error_lines = []
        self.auto_fix = auto_fix
        self.independent = independent
        self.auto_recover = auto_recover
        self.json_mode = json_mode
        self.fixed_applied = False
        
    def detect_error(self, line):
        """Check if line contains error indicators"""
        line_upper = line.upper()
        return any(keyword in line_upper for keyword in ERROR_KEYWORDS)
    
    def run_command(self, command):
        """Execute command and capture output in real-time"""
        if not self.json_mode:
            print(f"\n[TRIAGE] Executing: {command}")
            print("=" * 60)
        
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            def enqueue_output(out, q):
                for line in iter(out.readline, ''):
                    q.put(line)
                out.close()
                
            q = queue.Queue()
            t = threading.Thread(target=enqueue_output, args=(process.stdout, q))
            t.daemon = True
            t.start()
            
            last_error_time = 0
            
            while True:
                ret_code = process.poll()
                if ret_code is not None and q.empty():
                    break
                    
                try:
                    line = q.get(timeout=0.1)
                except queue.Empty:
                    if self.error_detected and time.time() - last_error_time > 1.0:
                        if not self.json_mode:
                            print(f"\n[TRIAGE] Traceback silence detected, analyzing live error...")
                        
                        result = self.analyze_errors()
                        
                        if self.json_mode:
                            result["exit_code"] = None
                            result["error_detected"] = True
                            result["success"] = True
                            print(json.dumps(result))
                            
                        if self.fixed_applied and self.auto_recover:
                            if not self.json_mode:
                                print(f"\n[TRIAGE] Killing running process to trigger restart...")
                            process.terminate()
                            process.wait()
                            return 1
                            
                        self.error_detected = False
                        self.error_lines = []
                        last_error_time = 0
                    continue
                else:
                    line = line.rstrip()
                    self.buffer.append(line)
                    
                    if self.detect_error(line):
                        self.error_detected = True
                        self.error_lines.append(line)
                        last_error_time = time.time()
                        if not self.json_mode:
                            print(f"[ERROR]  {line}")
                    else:
                        if self.error_detected:
                            last_error_time = time.time()
                        if not self.json_mode:
                            print(f"[OUTPUT] {line}")
            
            process.wait()
            return_code = process.returncode
            
            if not self.json_mode:
                print("=" * 60)
            
            if self.error_detected or return_code != 0:
                if not self.json_mode and not self.error_detected and return_code != 0:
                    print(f"\n[TRIAGE] Command failed with exit code {return_code}")
                result = self.analyze_errors()
                if self.json_mode:
                    result["exit_code"] = return_code
                    result["error_detected"] = True
                    result["success"] = True
                    _real_stdout = sys.stdout
                    sys.stdout = _SilentStream()
                    sys.stdout = _real_stdout
                    print(json.dumps(result))
            else:
                if not self.json_mode:
                    print(f"\n[TRIAGE] Command completed successfully (exit code: {return_code})")
                elif self.json_mode:
                    print(json.dumps({"success": True, "error_detected": False, "exit_code": return_code}))
            
            return return_code
            
        except Exception as e:
            if self.json_mode:
                print(json.dumps({"success": False, "error_detected": False, "exit_code": 1, "error": str(e)}))
            else:
                print(f"\n[TRIAGE] Failed to execute command: {e}")
            return 1
    
    def analyze_errors(self):
        """Analyze detected errors and provide solutions. Returns result dict."""
        if not self.json_mode:
            print(f"\n[TRIAGE] Error detected! Analyzing...")
            print()
        
        context = list(self.buffer)[-20:]
        context_str = "\n".join(context)
        
        try:
            from ai_logmaster.core.analyzer import ErrorAnalyzer

            if self.json_mode:
                # Silence all internal prints during analysis
                _orig_stdout = sys.stdout
                sys.stdout = _SilentStream()
                try:
                    analyzer = ErrorAnalyzer()
                    result = analyzer.analyze(context_str)
                finally:
                    sys.stdout = _orig_stdout
            else:
                analyzer = ErrorAnalyzer()
                result = analyzer.analyze(context_str)
                self.display_analysis(result)

                # Auto-fix: Trigger if flag is set OR prompt the user
                if self.auto_fix or self.independent:
                    if self.independent:
                        self.fixed_applied = analyzer.attempt_auto_fix(context_str, result, auto_confirm=True)
                    else:
                        self.fixed_applied = analyzer.attempt_auto_fix(context_str, result)
                else:
                    print("\n[TRIAGE] AI found a possible fix for your code.")
                    choice = input("[TRIAGE] Would you like to see the proposed fix? [y/N] ").strip().lower()
                    if choice in ('y', 'yes'):
                        self.fixed_applied = analyzer.attempt_auto_fix(context_str, result)

            return result

        except ImportError:
            if not self.json_mode:
                self.display_basic_analysis(context_str)
            return {"type": "Unknown Error", "cause": "", "fixes": [], "confidence": 0.0, "method": "Basic"}
    
    def display_analysis(self, result):
        """Display AI-powered analysis results"""
        method = result.get('method', 'Unknown')
        
        print("╔" + "═" * 58 + "╗")
        print("║ 🔍 DIAGNOSIS" + " " * 45 + "║")
        print("╠" + "═" * 58 + "╣")
        print(f"║ Type: {result.get('type', 'Unknown'):<50} ║")
        print(f"║ Confidence: {result.get('confidence', 0):.0%}" + " " * 44 + "║")
        print(f"║ Method: {method:<49} ║")
        print("╠" + "═" * 58 + "╣")
        
        cause = result.get('cause')
        if cause:
            print("║ 📋 ROOT CAUSE" + " " * 44 + "║")
            print("╠" + "═" * 58 + "╣")
            words = cause.split()
            line = "║ "
            for word in words:
                if len(line) + len(word) + 1 > 57:
                    print(line + " " * (59 - len(line)) + "║")
                    line = "║ " + word
                else:
                    line += (" " if len(line) > 2 else "") + word
            if len(line) > 2:
                print(line + " " * (59 - len(line)) + "║")
            print("╠" + "═" * 58 + "╣")
        
        print("║ 💡 RECOMMENDED FIXES" + " " * 37 + "║")
        print("╠" + "═" * 58 + "╣")
        
        for i, fix in enumerate(result.get('fixes', []), 1):
            if len(fix) > 52:
                words = fix.split()
                line = f"║ {i}. "
                for word in words:
                    if len(line) + len(word) + 1 > 57:
                        print(line + " " * (59 - len(line)) + "║")
                        line = "║    " + word
                    else:
                        line += (" " if len(line) > 5 else "") + word
                if len(line) > 5:
                    print(line + " " * (59 - len(line)) + "║")
            else:
                print(f"║ {i}. {fix:<54} ║")
        
        sources = result.get('sources', [])
        if sources:
            print("╠" + "═" * 58 + "╣")
            print("║ 📚 DOCUMENTATION SOURCES" + " " * 33 + "║")
            print("╠" + "═" * 58 + "╣")
            for source in sources[:3]:
                if len(source) > 54:
                    source = source[:51] + "..."
                print(f"║ • {source:<55} ║")
        
        print("╚" + "═" * 58 + "╝")
    
    def display_basic_analysis(self, context):
        """Display basic analysis without AI"""
        print("╔" + "═" * 58 + "╗")
        print("║ 🔍 BASIC ANALYSIS" + " " * 40 + "║")
        print("╠" + "═" * 58 + "╣")
        
        error_type = "Unknown Error"
        for line in context.split('\n'):
            if 'Error:' in line or 'Exception:' in line:
                error_type = line.split(':')[0].strip()
                break
        
        print(f"║ Type: {error_type:<50} ║")
        print("╠" + "═" * 58 + "╣")
        print("║ 💡 GENERAL RECOMMENDATIONS" + " " * 31 + "║")
        print("╠" + "═" * 58 + "╣")
        print("║ 1. Check the error message above" + " " * 25 + "║")
        print("║ 2. Review recent code changes" + " " * 28 + "║")
        print("║ 3. Search for the error online" + " " * 27 + "║")
        print("║ 4. Check logs for more details" + " " * 27 + "║")
        print("╚" + "═" * 58 + "╝")
        
        print("\n[TRIAGE] 💡 Tip: Install AI analyzer for smarter suggestions!")
        print("[TRIAGE]     pip install langchain langchain-openai")

def init_config(port: int = 5894, open_browser: bool = True):
    """Initialize configuration via web dashboard"""
    from ai_logmaster.dashboard.server import start_dashboard
    start_dashboard(port=port, open_browser=open_browser)

def main():
    parser = argparse.ArgumentParser(
        description="Smart Log Analyzer - Wrap commands and get AI-powered error analysis"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize configuration")
    init_parser.add_argument("--port", type=int, default=5894, help="Port for dashboard server")
    init_parser.add_argument("--no-browser", action="store_true", help="Do not open browser automatically")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run a command with analysis")
    run_parser.add_argument("cmd", help="Command to execute (use quotes)")
    run_parser.add_argument("--buffer", type=int, default=100,
                           help="Number of lines to buffer (default: 100)")
    run_parser.add_argument("--auto-fix", action="store_true",
                           help="Attempt to automatically fix errors using AI")
    run_parser.add_argument("--independent", action="store_true",
                           help="Apply AI fixes automatically without human intervention")
    run_parser.add_argument("--auto-recover", action="store_true",
                           help="Automatically restart the command after a fix is applied")
    run_parser.add_argument("--max-retries", type=int, default=None,
                           help="Maximum number of times to attempt auto-recovery (default: 3)")
    run_parser.add_argument("--json", action="store_true",
                           help="Output result as JSON (for IDE integrations)")
    
    args = parser.parse_args()
    
    if args.command == "init":
        init_config(port=args.port, open_browser=not args.no_browser)
    elif args.command == "run":
        from ai_logmaster.config import get_config
        config = get_config()
        agent_config = config.get_agent_config()
        
        auto_fix = args.auto_fix or agent_config.get("auto_fix", False)
        independent = args.independent or agent_config.get("independent_auto_fix", False)
        auto_recover = args.auto_recover or agent_config.get("auto_recover", False)
        max_retries = args.max_retries if args.max_retries is not None else agent_config.get("max_retries", 3)
        
        if not auto_recover:
            max_retries = 0
            
        retries = 0
        
        while True:
            wrapper = TriageWrapper(
                buffer_size=args.buffer,
                auto_fix=auto_fix,
                independent=independent,
                auto_recover=auto_recover,
                json_mode=args.json,
            )
            exit_code = wrapper.run_command(args.cmd)
            
            if exit_code != 0 and wrapper.fixed_applied and retries < max_retries:
                retries += 1
                if not args.json:
                    print(f"\n[TRIAGE] Auto-recovery: Restarting command (Attempt {retries}/{max_retries})...")
                continue
                
            sys.exit(exit_code)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
