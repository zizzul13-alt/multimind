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

    # 1. Expand New Session and click Create
    new_sess = sidebar.locator("details").filter(has_text="New Session").first
    new_sess.locator("summary").dispatch_event("click")
    time.sleep(0.5)
    sidebar.locator("input[placeholder='Project API...']").fill("Demo Evidence Session")
    sidebar.locator("button:has-text('Create')").click()
    time.sleep(3)

    # 2. Click the newly created session button in sidebar list!
    sess_btn = sidebar.locator("button").filter(has_text="Demo Evidence Session").first
    sess_btn.dispatch_event("click")
    time.sleep(3)

    print("Main headings after selecting created session:")
    print(page.locator("h1, h2, h3, h4").all_inner_texts())

    print("Is chat_first_feed_container visible?", page.locator(".st-key-chat_first_feed_container").is_visible())

    browser.close()

proc.terminate()
proc.wait()
