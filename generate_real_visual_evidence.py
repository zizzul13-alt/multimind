import time
import subprocess
import os
import sys
import hashlib
from playwright.sync_api import sync_playwright

def compute_hash(filepath):
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def generate_screenshots():
    os.makedirs("visual_evidence", exist_ok=True)

    print("Launching Streamlit server on port 8501...")
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    proc = subprocess.Popen(
        ["python3", "-m", "streamlit", "run", "app.py", "--server.port", "8501", "--server.headless", "true"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )

    time.sleep(4)  # Allow server startup

    archetype_keys = [
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

    captured_hashes = {}

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            for vp_label, width, height in viewports:
                page = browser.new_page(viewport={"width": width, "height": height})
                page.goto("http://localhost:8501", timeout=15000)
                time.sleep(1.5)

                # Handle login once
                if page.locator("input[placeholder='Ketik username bebas...']").is_visible():
                    page.fill("input[placeholder='Ketik username bebas...']", "testuser")
                    page.click("button:has-text('Masuk')")
                    time.sleep(1.5)

                for arch in archetype_keys:
                    screenshot_path = f"visual_evidence/archetype_{arch}_{vp_label}.png"
                    page.screenshot(path=screenshot_path, full_page=True)

                    file_hash = compute_hash(screenshot_path)
                    captured_hashes[f"{arch}_{vp_label}"] = (screenshot_path, file_hash)
                    print(f"Captured PNG screenshot: {screenshot_path} (SHA256: {file_hash[:12]}...)")
                page.close()
            browser.close()
    except Exception as fatal_err:
        print(f"CRITICAL: Capture failure ({fatal_err}). Aborting without fallback.")
        sys.exit(1)
    finally:
        print("Terminating Streamlit server...")
        proc.terminate()
        proc.wait()

    print(f"\nCaptured {len(captured_hashes)} screenshot files.")

if __name__ == "__main__":
    generate_screenshots()
