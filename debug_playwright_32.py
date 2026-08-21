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
    page = browser.new_page(viewport={"width": 390, "height": 844})
    page.goto("http://localhost:8501/?archetype=chat_first")
    time.sleep(2)
    page.fill("input[placeholder='Ketik username bebas...']", "testuser")
    page.click("button:has-text('Masuk')")
    time.sleep(2)

    sidebar = page.locator("[data-testid='stSidebar']")
    print("Is sidebar visible at 390px?", sidebar.is_visible())

    sess_btn = sidebar.locator("button").filter(has_text="📝").first
    print("Is sess_btn visible at 390px?", sess_btn.is_visible())
    if not sess_btn.is_visible():
        print("Clicking sidebar toggle...")
        page.locator("[data-testid='stSidebarCollapseButton']").dispatch_event("click")
        time.sleep(1)
        print("After collapse button click, is sess_btn visible?", sess_btn.is_visible())

    sess_btn.dispatch_event("click")
    time.sleep(2)
    print("Is .st-key-chat_first_feed_container visible at 390px?", page.locator(".st-key-chat_first_feed_container").is_visible())

    browser.close()

proc.terminate()
proc.wait()
