import time
import subprocess
import os
from playwright.sync_api import sync_playwright

proc = subprocess.Popen(
    ["python3", "-m", "streamlit", "run", "app.py", "--server.port", "8501", "--server.headless", "true"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    env={"PYTHONPATH": ".", "PATH": os.environ["PATH"]}
)
time.sleep(4)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("http://localhost:8501/?archetype=chat_first")
    time.sleep(2)
    page.fill("input[placeholder='Ketik username bebas...']", "testuser")
    page.click("button:has-text('Masuk')")
    time.sleep(2)

    sidebar = page.locator("[data-testid='stSidebar']")

    # Check if 'Demo Evidence Session' exists in sidebar text
    has_demo = "Demo Evidence Session" in sidebar.inner_text()
    print("Does sidebar contain Demo Evidence Session?", has_demo)

    if not has_demo:
        print("Creating session 'Demo Evidence Session'...")
        sidebar.locator("details").filter(has_text="New Session").locator("summary").click()
        time.sleep(1)
        sidebar.locator("input[placeholder='Project API...']").fill("Demo Evidence Session")
        sidebar.locator("button:has-text('Create')").click()
        time.sleep(3)

    # Now click session button
    sess_btn = sidebar.locator("button:has-text('Demo Evidence Session')").first
    print("Is sess_btn visible?", sess_btn.is_visible())
    sess_btn.click()
    time.sleep(2)

    print("Is chat_first_feed_container visible?", page.locator(".st-key-chat_first_feed_container").is_visible())

    browser.close()

proc.terminate()
proc.wait()
