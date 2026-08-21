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
    page.goto("http://localhost:8501/?archetype=command_center")
    time.sleep(2)
    page.fill("input[placeholder='Ketik username bebas...']", "testuser")
    page.click("button:has-text('Masuk')")
    time.sleep(2)

    sidebar = page.locator("[data-testid='stSidebar']")
    pop_sess_btn = sidebar.locator("button").filter(has_text="Populated Archetype").first
    if not pop_sess_btn.is_visible():
        pop_sess_btn = sidebar.locator("button[help*='Populated Archetype']").first

    pop_sess_btn.dispatch_event("click")
    time.sleep(2)

    print("Main headings after selecting session in command_center:")
    print(page.locator("h1, h2, h3, h4").all_inner_texts())

    print("Is .st-key-command_center_matrix_container visible?", page.locator(".st-key-command_center_matrix_container").is_visible())

    browser.close()

proc.terminate()
proc.wait()
