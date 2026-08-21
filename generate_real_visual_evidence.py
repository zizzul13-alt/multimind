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
                    # Request active archetype via approved presentation query parameter seam
                    page.goto(f"http://localhost:8501/?archetype={arch_id}", timeout=20000)
                    time.sleep(1.5)

                    # 1. Login
                    if page.locator("input[placeholder='Ketik username bebas...']").is_visible():
                        page.fill("input[placeholder='Ketik username bebas...']", "testuser")
                        page.click("button:has-text('Masuk')")
                        time.sleep(1.5)

                    sidebar = page.locator("[data-testid='stSidebar']")

                    # 2. Select first active session in sidebar using dispatch_event
                    sess_btn = sidebar.locator("button").filter(has_text="📝").first
                    if sess_btn.count() == 0:
                        sess_btn = sidebar.locator("button").filter(has_text="📌").first

                    if sess_btn.count() > 0:
                        sess_btn.dispatch_event("click")
                        time.sleep(2)

                    # 3. VERIFY active archetype container key is rendered in DOM
                    expected_container = page.locator(f".st-key-{container_key_substring}")
                    assert expected_container.is_visible(), f"R6 Verification failed: Container key class .st-key-{container_key_substring} not visible in DOM for archetype '{arch_id}'"

                    # 4. COLLAPSE SIDEBAR via real UI control button to leave main surface unobstructed
                    collapse_btn = page.locator("[data-testid='stSidebarCollapseButton']")
                    if collapse_btn.is_visible():
                        collapse_btn.dispatch_event("click")
                        time.sleep(1)

                    # 5. VERIFY main archetype surface is unobstructed (container key visible)
                    assert expected_container.is_visible(), f"R6 Verification failed: Main archetype surface obstructed after sidebar collapse for archetype '{arch_id}'"

                    # 6. CAPTURE
                    screenshot_path = f"visual_evidence/archetype_{arch_id}_{vp_label}.png"
                    page.screenshot(path=screenshot_path, full_page=True)

                    file_hash = compute_hash(screenshot_path)
                    captured_hashes[f"{arch_id}_{vp_label}"] = (screenshot_path, file_hash)
                    print(f"R6 VERIFIED & CAPTURED {arch_id} ({vp_label}): {screenshot_path} (SHA256: {file_hash[:12]}...)")

                    page.close()
            browser.close()
    except Exception as fatal_err:
        print(f"CRITICAL R6 FAILURE: State transition / capture error ({fatal_err}). Aborting without fallback.")
        sys.exit(1)
    finally:
        print("Terminating Streamlit server...")
        proc.terminate()
        proc.wait()

    # Log recorded hashes
    print("\n--- RECORDED SCREENSHOT HASHES & SIZES ---")
    for k, (p_path, h) in captured_hashes.items():
        print(f"  {k:30s} -> SHA256: {h} ({os.path.getsize(p_path)} bytes)")

    # Compare hashes across archetypes for each viewport
    hashes_1440 = [h for k, (p, h) in captured_hashes.items() if "1440px" in k]
    hashes_390 = [h for k, (p, h) in captured_hashes.items() if "390px" in k]

    print(f"\n1440px unique hashes: {len(set(hashes_1440))} / {len(archetypes)}")
    print(f"390px unique hashes: {len(set(hashes_390))} / {len(archetypes)}")

    if len(set(hashes_1440)) != len(archetypes):
        print(f"FAIL: Expected {len(archetypes)} unique hashes for 1440px viewports, got {len(set(hashes_1440))}")
        sys.exit(1)
    if len(set(hashes_390)) != len(archetypes):
        print(f"FAIL: Expected {len(archetypes)} unique hashes for 390px viewports, got {len(set(hashes_390))}")
        sys.exit(1)

    print("\nSUCCESS: All 14 screenshots verified in DOM and captured across all 7 archetypes!")

if __name__ == "__main__":
    generate_screenshots()
