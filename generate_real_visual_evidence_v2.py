import time
import subprocess
import os
import sys
import hashlib
import json
import uuid
import sqlite3
import shutil
from utils.config import Config
from database.manager import DatabaseManager
from playwright.sync_api import sync_playwright

EVIDENCE_USER = "multimind_visual_evidence_v2"
RUN_ID = f"run-{int(time.time())}"
TEMP_EVIDENCE_DIR = f"visual_evidence_temp_{RUN_ID}"
FINAL_EVIDENCE_DIR = "visual_evidence"
MANIFEST_PATH = os.path.join(FINAL_EVIDENCE_DIR, "manifest.json")

def compute_hash(filepath):
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def seed_populated_session():
    """Seeds a realistic populated session using dedicated evidence user database."""
    db_path = Config.get_db_path(EVIDENCE_USER)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS chats")
    cursor.execute("DROP TABLE IF EXISTS sessions")
    conn.commit()
    conn.close()

    db = DatabaseManager(db_path)

    sess_id = "sess-evidence-v2-populated"
    sess_name = "Populated Archetype Evidence Session"

    db.create_session(sess_id, sess_name, "coding")

    sample_debate_1 = {
        "gate_score": 9,
        "responses": [
            {"round_index": 1, "agent": "gemini", "text": "```python\ndef fibonacci(n):\n    return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)\n```", "status": "success"},
            {"round_index": 1, "agent": "groq", "text": "```python\ndef fibonacci_iter(n):\n    a, b = 0, 1\n    for _ in range(n):\n        a, b = b, a + b\n    return a\n```", "status": "success"},
            {"round_index": 1, "agent": "deepseek", "text": "Optimal dynamic programming approach recommended for O(n) runtime.", "status": "success"}
        ],
        "total_tokens": 1850,
        "total_cost": 0.0028
    }

    sample_debate_2 = {
        "gate_score": 8,
        "responses": [
            {"round_index": 1, "agent": "gemini", "text": "Use Python dataclasses with frozen=True for immutable snapshot models.", "status": "success"},
            {"round_index": 1, "agent": "openrouter", "text": "Ensure clean UI presentation boundaries without backend DB access.", "status": "success"}
        ],
        "total_tokens": 1200,
        "total_cost": 0.0015
    }

    db.save_chat(sess_id, {
        "id": str(uuid.uuid4()),
        "prompt": "Write an efficient Fibonacci function in Python.",
        "prompt_compressed": "",
        "mode": "continue",
        "context_mode": "continue",
        "final_answer": "Here is the optimized iterative Fibonacci function in Python:\n\n```python\ndef fibonacci(n):\n    if n <= 0: return 0\n    a, b = 0, 1\n    for _ in range(1, n):\n        a, b = b, a + b\n    return b\n```\n\nThis provides linear time complexity O(n) and constant memory O(1).",
        "debate_data": json.dumps(sample_debate_1),
        "tokens_used": 1850,
        "cost": 0.0028
    })

    db.save_chat(sess_id, {
        "id": str(uuid.uuid4()),
        "prompt": "Explain immutable presentation snapshot models in Python.",
        "prompt_compressed": "",
        "mode": "continue",
        "context_mode": "continue",
        "final_answer": "Immutable presentation snapshot models use frozen dataclasses (`@dataclass(frozen=True)`) and tuple collections to guarantee that UI renderers cannot mutate underlying source state or execute side-effects during presentation rendering.",
        "debate_data": json.dumps(sample_debate_2),
        "tokens_used": 1200,
        "cost": 0.0015
    })

    print(f"Seeded dedicated evidence session database successfully at: {db_path}")
    return sess_id, sess_name

def run_atomic_evidence_capture():
    sess_id, target_sess_name = seed_populated_session()
    os.makedirs(TEMP_EVIDENCE_DIR, exist_ok=True)

    print("Launching Streamlit server on port 8501...")
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    proc = subprocess.Popen(
        ["python3", "-m", "streamlit", "run", "app.py", "--server.port", "8501", "--server.headless", "true"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )

    time.sleep(5)  # Allow server startup

    archetypes = [
        ("chat_first", "chat_first_feed_container"),
        ("command_center", "command_center_matrix_container"),
        ("ai_workspace", "ai_workspace_objects_container"),
        ("ai_research_lab", "ai_research_lab_findings_container"),
        ("agent_canvas", "agent_canvas_topology_container"),
        ("terminal_hacker", "terminal_hacker_stream_container"),
        ("minimal_saas", "minimal_saas_task_container")
    ]

    viewports = [
        ("1440px", 1440, 900),
        ("390px", 390, 844)
    ]

    manifest_entries = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            for vp_label, width, height in viewports:
                for arch_id, container_key_substring in archetypes:
                    page = browser.new_page(viewport={"width": width, "height": height})
                    page.goto(f"http://localhost:8501/?archetype={arch_id}", timeout=20000)
                    time.sleep(1.5)

                    # 1. Login & Verify EVIDENCE_USER
                    if page.locator("input[placeholder='Ketik username bebas...']").is_visible():
                        page.fill("input[placeholder='Ketik username bebas...']", EVIDENCE_USER)
                        page.click("button:has-text('Masuk')")
                        time.sleep(1.5)

                    sidebar = page.locator("[data-testid='stSidebar']")
                    user_badge = sidebar.locator(f"text='👤 {EVIDENCE_USER}'")
                    assert user_badge.is_visible(), f"ATOMIC VERIFICATION FAILED: Active user is not {EVIDENCE_USER}"

                    # 2. LOCATE & SELECT exact seeded evidence session by button text
                    pop_sess_btn = sidebar.locator("button").filter(has_text="Populated Archetype").first
                    if pop_sess_btn.count() == 0:
                        pop_sess_btn = sidebar.locator("button[help*='Populated Archetype']").first
                    assert pop_sess_btn.count() > 0, f"ATOMIC VERIFICATION FAILED: Seeded session button for '{target_sess_name}' not found in sidebar."

                    pop_sess_btn.dispatch_event("click")
                    time.sleep(1.5)

                    # VERIFY populated session content & title on main surface
                    heading_texts = page.locator("h3, h4").all_inner_texts()
                    assert any(target_sess_name in h for h in heading_texts), f"ATOMIC VERIFICATION FAILED: Seeded session heading not rendered for '{target_sess_name}' in headings: {heading_texts}"

                    # 3. VERIFY active archetype container key is rendered in DOM
                    expected_selector = f".st-key-{container_key_substring}"
                    expected_container = page.locator(expected_selector)
                    assert expected_container.is_visible(), f"ATOMIC VERIFICATION FAILED: Container selector '{expected_selector}' not visible in DOM for archetype '{arch_id}'"

                    # 4. COLLAPSE SIDEBAR via real UI control button
                    collapse_btn = page.locator("[data-testid='stSidebarCollapseButton']")
                    if collapse_btn.is_visible():
                        collapse_btn.click()
                        time.sleep(1)

                    # 5. VERIFY sidebar is actually collapsed and NOT obstructing viewport
                    sidebar_box = sidebar.bounding_box()
                    sidebar_unobstructed = True
                    if sidebar_box:
                        if sidebar_box["x"] > -100 and sidebar_box["width"] > 1 and sidebar.is_visible():
                            sidebar_unobstructed = False
                    assert sidebar_unobstructed, f"ATOMIC VERIFICATION FAILED: Sidebar remains visible/obstructing at x={sidebar_box['x'] if sidebar_box else 'N/A'}, width={sidebar_box['width'] if sidebar_box else 'N/A'}"

                    # 6. VERIFY main archetype surface remains unobstructed after collapse
                    assert expected_container.is_visible(), f"ATOMIC VERIFICATION FAILED: Main archetype surface obstructed after collapse for '{arch_id}'"

                    # 7. CAPTURE screenshot into temp directory
                    screenshot_filename = f"archetype_{arch_id}_{vp_label}.png"
                    temp_screenshot_path = os.path.join(TEMP_EVIDENCE_DIR, screenshot_filename)
                    page.screenshot(path=temp_screenshot_path, full_page=True)

                    file_hash = compute_hash(temp_screenshot_path)

                    manifest_entries.append({
                        "run_id": RUN_ID,
                        "archetype": arch_id,
                        "viewport": vp_label,
                        "screenshot_filename": screenshot_filename,
                        "sha256": file_hash,
                        "file_size_bytes": os.path.getsize(temp_screenshot_path),
                        "evidence_username": EVIDENCE_USER,
                        "evidence_session_id": sess_id,
                        "evidence_session_name": target_sess_name,
                        "populated_content_heading_verified": target_sess_name,
                        "archetype_dom_selector": expected_selector,
                        "sidebar_unobstructed_verified": True
                    })
                    print(f"VERIFIED [{len(manifest_entries)}/14] {arch_id} ({vp_label}) -> SHA256: {file_hash[:12]}...")

                    page.close()
            browser.close()
    except Exception as fatal_err:
        print(f"\nCRITICAL ATOMIC CAPTURE FAILURE: {fatal_err}. Aborting without modifying current evidence.")
        if os.path.exists(TEMP_EVIDENCE_DIR):
            shutil.rmtree(TEMP_EVIDENCE_DIR)
        sys.exit(1)
    finally:
        print("Terminating Streamlit server...")
        proc.terminate()
        proc.wait()

    assert len(manifest_entries) == 14, f"ATOMIC VERIFICATION FAILED: Expected 14 verified entries, got {len(manifest_entries)}"

    # 8. ATOMIC REPLACEMENT: Only after ALL 14 captures pass verification
    print("\nALL 14 CAPTURES PASSED ATOMIC VERIFICATION. Replacing visual_evidence/ atomically...")
    if os.path.exists(FINAL_EVIDENCE_DIR):
        shutil.rmtree(FINAL_EVIDENCE_DIR)
    shutil.move(TEMP_EVIDENCE_DIR, FINAL_EVIDENCE_DIR)

    # Write Machine-Readable Proof Manifest
    manifest_data = {
        "run_id": RUN_ID,
        "timestamp_utc": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "total_captures": len(manifest_entries),
        "captures": manifest_entries
    }
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    print(f"Machine-readable proof manifest generated at: {MANIFEST_PATH}")
    print("ATOMIC REPLACEMENT COMPLETE SUCCESS!")

if __name__ == "__main__":
    run_atomic_evidence_capture()
