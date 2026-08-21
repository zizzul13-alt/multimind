import time
import subprocess
import os
import sys
import hashlib
import json
import uuid
import sqlite3
from utils.config import Config
from database.manager import DatabaseManager
from playwright.sync_api import sync_playwright

EVIDENCE_USER = "multimind_visual_evidence_v2"

def compute_hash(filepath):
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def seed_populated_session():
    """Seeds a realistic session using dedicated evidence user database without touching testuser or main databases."""
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
    return sess_name

def generate_evidence_v2():
    target_sess_name = seed_populated_session()
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

    captured_hashes = {}

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            for vp_label, width, height in viewports:
                for arch_id, container_key_substring in archetypes:
                    page = browser.new_page(viewport={"width": width, "height": height})
                    # Request active archetype via presentation query parameter seam
                    page.goto(f"http://localhost:8501/?archetype={arch_id}", timeout=20000)
                    time.sleep(1.5)

                    # 1. Login as dedicated evidence user
                    if page.locator("input[placeholder='Ketik username bebas...']").is_visible():
                        page.fill("input[placeholder='Ketik username bebas...']", EVIDENCE_USER)
                        page.click("button:has-text('Masuk')")
                        time.sleep(1.5)

                    sidebar = page.locator("[data-testid='stSidebar']")

                    # On narrow viewports (390px), expand collapsed sidebar if collapsed control button is visible
                    collapsed_btn = page.locator("[data-testid='collapsedControl']")
                    if width < 768 and collapsed_btn.is_visible():
                        collapsed_btn.dispatch_event("click")
                        time.sleep(1)

                    # 2. LOCATE & SELECT exact seeded evidence session in sidebar
                    pop_sess_btn = sidebar.locator("button").filter(has_text="Populated Archetype").first
                    if pop_sess_btn.count() == 0:
                        pop_sess_btn = sidebar.locator("button[help*='Populated Archetype']").first
                    if pop_sess_btn.count() == 0:
                        pop_sess_btn = sidebar.locator("button").filter(has_text="📝").first
                    if pop_sess_btn.count() == 0:
                        pop_sess_btn = sidebar.locator("button").filter(has_text="📌").first

                    assert pop_sess_btn.count() > 0, f"R6 Failure: Seeded session button for '{target_sess_name}' not found in sidebar."

                    pop_sess_btn.dispatch_event("click")
                    time.sleep(1.5)

                    # VERIFY populated session title/header is rendered on main surface
                    heading_text = page.locator("h3, h4").all_inner_texts()
                    assert any(target_sess_name in h for h in heading_text), f"R6 Failure: Seeded session header not rendered for '{target_sess_name}' in headings: {heading_text}"

                    # 3. VERIFY active archetype container key is rendered in DOM
                    expected_container = page.locator(f".st-key-{container_key_substring}")
                    assert expected_container.is_visible(), f"R6 Verification failed: Container key class .st-key-{container_key_substring} not visible in DOM for archetype '{arch_id}'"

                    # 4. COLLAPSE SIDEBAR via real UI control button
                    collapse_btn = page.locator("[data-testid='stSidebarCollapseButton']")
                    if collapse_btn.is_visible():
                        collapse_btn.click()
                        time.sleep(1)

                    # 5. VERIFY sidebar is actually collapsed and NOT obstructing viewport
                    sidebar_box = sidebar.bounding_box()
                    if sidebar_box:
                        assert sidebar_box["x"] < 0 or sidebar_box["width"] <= 1 or not sidebar.is_visible(), \
                            f"R6 Verification failed: Sidebar remains visible/obstructing at x={sidebar_box['x']}, width={sidebar_box['width']}"

                    # 6. VERIFY main archetype surface remains unobstructed
                    assert expected_container.is_visible(), f"R6 Verification failed: Main archetype surface obstructed after sidebar collapse for archetype '{arch_id}'"

                    # 7. CAPTURE screenshot
                    screenshot_path = f"visual_evidence/archetype_{arch_id}_{vp_label}.png"
                    page.screenshot(path=screenshot_path, full_page=True)

                    file_hash = compute_hash(screenshot_path)
                    captured_hashes[f"{arch_id}_{vp_label}"] = (screenshot_path, file_hash)
                    print(f"R6 VERIFIED & CAPTURED {arch_id} ({vp_label}): {screenshot_path} (SHA256: {file_hash[:12]}...)")

                    page.close()
            browser.close()
    except Exception as fatal_err:
        print(f"CRITICAL R6 FAILURE: Capture error ({fatal_err}). Aborting without fallback.")
        sys.exit(1)
    finally:
        print("Terminating Streamlit server...")
        proc.terminate()
        proc.wait()

    # Log recorded hashes and sizes
    print("\n--- REPLACED V2 SCREENSHOT HASHES & SIZES ---")
    for k, (p_path, h) in captured_hashes.items():
        print(f"  {k:30s} -> SHA256: {h} ({os.path.getsize(p_path)} bytes)")

    hashes_1440 = [h for k, (p, h) in captured_hashes.items() if "1440px" in k]
    hashes_390 = [h for k, (p, h) in captured_hashes.items() if "390px" in k]

    print(f"\n1440px unique hashes: {len(set(hashes_1440))} / {len(archetypes)}")
    print(f"390px unique hashes: {len(set(hashes_390))} / {len(archetypes)}")

    print("\nSUCCESS: All 14 populated replacement screenshots verified in DOM and captured unobstructed across all 7 archetypes!")

if __name__ == "__main__":
    generate_evidence_v2()
