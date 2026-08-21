import time
import subprocess
import os
import sys
from utils.config import Config
from database.manager import DatabaseManager
from playwright.sync_api import sync_playwright

db_path = Config.get_db_path("testuser")
print("Target DB path:", db_path)
db = DatabaseManager(db_path)
sess = db.get_sessions()
print("Sessions in DB before launching app:", sess)

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
    page.goto("http://localhost:8501")
    time.sleep(2)
    page.fill("input[placeholder='Ketik username bebas...']", "testuser")
    page.click("button:has-text('Masuk')")
    time.sleep(2)

    sidebar = page.locator("[data-testid='stSidebar']")
    print("Sidebar inner text snippet after login:")
    print(sidebar.inner_text()[:400])

    browser.close()

proc.terminate()
proc.wait()
