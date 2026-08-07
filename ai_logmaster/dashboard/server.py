"""
AI LogMaster Dashboard Server
Lightweight HTTP server using Python stdlib only.
Serves the config dashboard and handles API requests.
"""
import http.server
import json
import os
import socket
import sys
import threading
import webbrowser
from pathlib import Path
from urllib.parse import urlparse

# Config paths
CONFIG_DIR = Path.home() / ".ai-logmaster"
CONFIG_FILE = CONFIG_DIR / "config.json"
PACKAGE_CONFIG = Path(__file__).parent.parent / "config" / "config.json"
DASHBOARD_DIR = Path(__file__).parent

# Provider → model suggestions mapping
PROVIDER_MODELS = {
    "groq": [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "llama-3.1-70b-versatile",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
    ],
    "openai": [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
        "o1-mini",
    ],
    "anthropic": [
        "claude-sonnet-4-20250514",
        "claude-3-5-sonnet-20241022",
        "claude-3-haiku-20240307",
        "claude-3-opus-20240229",
    ],
    "google": [
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-2.0-flash",
        "gemini-1.5-pro",
    ],
    "nvidia": [
        "meta/llama-3.1-405b-instruct",
        "meta/llama-3.1-70b-instruct",
        "nvidia/llama-3.1-nemotron-70b-instruct",
    ],
}

# Provider → API key env var name
PROVIDER_ENV_VARS = {
    "groq": "GROQ_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "google": "GOOGLE_API_KEY",
    "nvidia": "NVIDIA_API_KEY",
}


def _load_config() -> dict:
    """Load config from user dir, falling back to package default."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    elif PACKAGE_CONFIG.exists():
        with open(PACKAGE_CONFIG, "r") as f:
            return json.load(f)
    else:
        return _default_config()


def _default_config() -> dict:
    return {
        "ai": {
            "provider": "groq",
            "model": "llama-3.3-70b-versatile",
            "api_key": "",
            "temperature": 0.2,
            "max_tokens": 1000,
        },
        "agent": {
            "use_cached_solutions": True,
            "fetch_documentation": True,
            "use_ai_analysis": True,
            "auto_fix": True,
            "independent_auto_fix": False,
            "auto_recover": False,
            "max_retries": 3,
            "cached_error_types": ["connection", "import", "memory", "timeout", "permission"],
            "complex_error_types": ["syntax", "type", "value", "unknown"],
        },
        "documentation": {
            "enable_search": True,
            "search_engine": "duckduckgo",
        },
        "output": {
            "verbose": True,
            "show_api_calls": True,
        },
    }


def _save_config(config: dict) -> None:
    """Save config to user directory."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def _test_connection(config: dict) -> dict:
    """
    Test the LLM connection by making a tiny API call.
    Returns {"success": True/False, "message": "..."}.
    """
    ai = config.get("ai", {})
    provider = ai.get("provider", "").lower()
    model = ai.get("model", "")
    api_key = ai.get("api_key", "")
    base_url = ai.get("base_url", "")

    if not api_key:
        return {"success": False, "message": "API key is empty. Please enter your API key."}

    if not model:
        return {"success": False, "message": "Model name is empty. Please select or enter a model."}

    try:
        if provider == "groq":
            from langchain_groq import ChatGroq
            llm = ChatGroq(model=model, api_key=api_key, max_tokens=5)
        elif provider in ("openai", "nvidia"):
            from langchain_openai import ChatOpenAI
            kwargs = {"model": model, "api_key": api_key, "max_tokens": 5}
            if base_url:
                kwargs["base_url"] = base_url
            llm = ChatOpenAI(**kwargs)
        elif provider == "anthropic":
            from langchain_anthropic import ChatAnthropic
            llm = ChatAnthropic(model=model, api_key=api_key, max_tokens=5)
        elif provider == "google":
            from langchain_google_genai import ChatGoogleGenerativeAI
            llm = ChatGoogleGenerativeAI(model=model, api_key=api_key, max_tokens=5)
        else:
            return {"success": False, "message": f"Unknown provider: {provider}"}

        # Make a tiny call
        response = llm.invoke("Say OK")
        if response and response.content:
            return {"success": True, "message": f"Connected successfully! Model responded: \"{response.content[:60]}\""}
        else:
            return {"success": False, "message": "Model returned empty response."}

    except ImportError as e:
        pkg = provider if provider != "nvidia" else "openai"
        return {
            "success": False,
            "message": f"Missing package for '{provider}'. Run: pip install langchain-{pkg}"
        }
    except Exception as e:
        err_msg = str(e)
        # Trim long error messages
        if len(err_msg) > 200:
            err_msg = err_msg[:200] + "..."
        return {"success": False, "message": f"Connection failed: {err_msg}"}


class DashboardHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for the dashboard."""

    server_version = "LogMasterDashboard/1.0"

    def log_message(self, format, *args):
        """Suppress default request logging to keep terminal clean."""
        pass

    def _send_json(self, data: dict, status: int = 200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, filename: str, content_type: str):
        filepath = DASHBOARD_DIR / filename
        if not filepath.exists():
            self.send_error(404, f"File not found: {filename}")
            return
        with open(filepath, "rb") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/" or path == "/index.html":
            self._send_file("index.html", "text/html; charset=utf-8")
        elif path == "/style.css":
            self._send_file("style.css", "text/css; charset=utf-8")
        elif path == "/script.js":
            self._send_file("script.js", "application/javascript; charset=utf-8")
        elif path == "/api/config":
            config = _load_config()
            # Also send provider models and env var hints
            config["_meta"] = {
                "provider_models": PROVIDER_MODELS,
                "provider_env_vars": PROVIDER_ENV_VARS,
                "config_path": str(CONFIG_FILE),
            }
            self._send_json(config)
        else:
            self.send_error(404)

    def do_POST(self):
        path = urlparse(self.path).path
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length else b""

        if path == "/api/config":
            try:
                config = json.loads(body.decode("utf-8"))
                # Strip _meta before saving
                config.pop("_meta", None)
                _save_config(config)
                self._send_json({"success": True, "message": f"Config saved to {CONFIG_FILE}"})
            except Exception as e:
                self._send_json({"success": False, "message": str(e)}, 400)

        elif path == "/api/test":
            try:
                config = json.loads(body.decode("utf-8"))
                result = _test_connection(config)
                self._send_json(result)
            except Exception as e:
                self._send_json({"success": False, "message": str(e)}, 500)

        elif path == "/api/shutdown":
            self._send_json({"success": True, "message": "Server shutting down..."})
            # Shutdown in a separate thread so the response can be sent first
            threading.Thread(target=self.server.shutdown, daemon=True).start()

        else:
            self.send_error(404)


def _find_free_port(default_port: int = 5894) -> int:
    """Find specified port or a free port on localhost."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", default_port))
            return default_port
    except OSError:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]


def start_dashboard(port: int = 5894, open_browser: bool = True):
    """
    Start the dashboard server, open the browser, and block until shutdown.
    Called from the CLI `logmaster init` command.
    """
    # Ensure config dir exists and default config is present
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        if PACKAGE_CONFIG.exists():
            import shutil
            shutil.copy(PACKAGE_CONFIG, CONFIG_FILE)
        else:
            _save_config(_default_config())

    port = _find_free_port(port)
    url = f"http://127.0.0.1:{port}"

    server = http.server.HTTPServer(("127.0.0.1", port), DashboardHandler)

    print(f"\n  ╔══════════════════════════════════════════════════╗")
    print(f"  ║  🚀  AI LogMaster Configuration Dashboard       ║")
    print(f"  ╠══════════════════════════════════════════════════╣")
    print(f"  ║  Dashboard: {url:<37} ║")
    print(f"  ║  Config:    {str(CONFIG_FILE):<37} ║")
    print(f"  ╠══════════════════════════════════════════════════╣")
    print(f"  ║  Press Ctrl+C to close if browser doesn't open  ║")
    print(f"  ╚══════════════════════════════════════════════════╝\n")

    # Open browser if requested
    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print("\n  ✅ Dashboard closed. Your configuration is saved.")
        print(f"  📁 Config file: {CONFIG_FILE}")
        print(f"  ▶  Run: logmaster run \"your command\" to start analyzing!\n")
