import time
import subprocess
import os
import signal
from playwright.sync_api import sync_playwright

def generate_screenshots():
    os.makedirs("visual_evidence", exist_ok=True)

    # Launch Streamlit app in background
    print("Launching Streamlit server on port 8501...")
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    proc = subprocess.Popen(
        ["python3", "-m", "streamlit", "run", "app.py", "--server.port", "8501", "--server.headless", "true"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )

    time.sleep(5)  # Allow server to start up

    archetypes = [
        "chat_first",
        "command_center",
        "ai_workspace",
        "ai_research_lab",
        "agent_canvas",
        "terminal_hacker",
        "minimal_saas"
    ]

    viewports = [
        ("1440px", 1440, 900),
        ("390px", 390, 844)
    ]

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            for arch in archetypes:
                for vp_label, width, height in viewports:
                    page = browser.new_page(viewport={"width": width, "height": height})
                    try:
                        page.goto("http://localhost:8501", timeout=15000)
                        time.sleep(2)

                        # Set active user session if on login
                        if "Login" in page.content() or "Silakan Login" in page.content():
                            page.fill("input[placeholder='Ketik username bebas...']", "testuser")
                            page.click("button:has-text('Masuk')")
                            time.sleep(2)

                        screenshot_path = f"visual_evidence/archetype_{arch}_{vp_label}.png"
                        page.screenshot(path=screenshot_path, full_page=True)
                        print(f"Captured real screenshot: {screenshot_path}")
                    except Exception as e:
                        print(f"Error capturing {arch} {vp_label}: {e}")
                    finally:
                        page.close()
            browser.close()
    finally:
        print("Terminating Streamlit server...")
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    generate_screenshots()
