import sys
import os
import threading
import time
import socket
import subprocess
import signal
import atexit

SERVER_PORT = 8501
_browser_proc = None
_stop = threading.Event()


def get_base_path():
    if getattr(sys, '_MEIPASS', None):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def _setup_streamlit_config(base):
    st_dir = os.path.join(base, ".streamlit")
    os.makedirs(st_dir, exist_ok=True)

    cred = os.path.join(st_dir, "credentials.toml")
    if not os.path.exists(cred):
        with open(cred, "w", encoding="utf-8") as f:
            f.write('[general]\nemail = ""\n')

    cfg = os.path.join(st_dir, "config.toml")
    if not os.path.exists(cfg):
        with open(cfg, "w", encoding="utf-8") as f:
            f.write(
                "[server]\n"
                "headless = true\n"
                f"port = {SERVER_PORT}\n"
                "enableCORS = false\n"
                "enableXsrfProtection = false\n\n"
                "[browser]\n"
                "gatherUsageStats = false\n"
                "serverAddress = \"localhost\"\n"
                f"serverPort = {SERVER_PORT}\n\n"
                "[global]\n"
                "developmentMode = false\n"
            )

    os.environ["STREAMLIT_CONFIG_DIR"] = st_dir


def _port_ready(port, timeout=30):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                return True
        except OSError:
            time.sleep(0.3)
    return False


def _run_streamlit(dashboard_path):
    sys.argv = [
        "streamlit", "run", dashboard_path,
        "--global.developmentMode", "false",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
        "--server.port", str(SERVER_PORT),
    ]
    from streamlit.web.cli import main as st_main
    st_main()


_BROWSER_SEARCH = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]


def _find_browser():
    for p in _BROWSER_SEARCH:
        if os.path.isfile(p):
            return p
    return None


def _launch_app_window(url):
    global _browser_proc
    browser = _find_browser()
    if browser is None:
        import webbrowser
        webbrowser.open(url)
        return

    _browser_proc = subprocess.Popen([
        browser,
        f"--app={url}",
        "--window-size=1600,900",
        "--disable-extensions",
        "--new-window",
    ])


def _cleanup():
    _stop.set()
    if _browser_proc and _browser_proc.poll() is None:
        _browser_proc.terminate()


def main():
    base = get_base_path()
    os.chdir(base)
    _setup_streamlit_config(base)

    dashboard = os.path.join(base, "gdp_dashboard_streamlit.py")

    server_thread = threading.Thread(target=_run_streamlit, args=(dashboard,), daemon=True)
    server_thread.start()

    if not _port_ready(SERVER_PORT):
        print("ERROR: Streamlit server did not start in time.")
        sys.exit(1)

    url = f"http://localhost:{SERVER_PORT}"
    _launch_app_window(url)

    atexit.register(_cleanup)

    if _browser_proc:
        _browser_proc.wait()
    else:
        try:
            while not _stop.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    _cleanup()


if __name__ == "__main__":
    main()

