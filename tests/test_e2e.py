# tests/test_e2e.py

import os
import sys
import random
import threading
import time

import pytest
from playwright.sync_api import sync_playwright


project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Import your factory function from app.py
from app import create_app


def _run_app():
    """
    Start the Flask app on port 5000 (no reloader, no debug).
    Uses the factory pattern defined in app.py
    """
    flask_app = create_app()
    flask_app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False
    )


@pytest.fixture(scope="session", autouse=True)
def flask_server():
    """Launch Flask server once for all E2E tests."""
    thread = threading.Thread(target=_run_app, daemon=True)
    thread.start()
    time.sleep(1)  # wait briefly for server startup


#constants
BASE_URL = "http://127.0.0.1:5000"


# -------------------------------------------------------------
#  HELPER FUNCTIONS
# -------------------------------------------------------------
def add_book_via_ui(page, title, author, isbn, copies):
    """Navigate to Add Book page and add a new book."""
    page.goto(f"{BASE_URL}/add_book")

    page.fill("#title", title)
    page.fill("#author", author)
    page.fill("#isbn", isbn)
    page.fill("#total_copies", copies)

    page.click("text=Add Book to Catalog")

    page.wait_for_timeout(800)
    body = page.inner_text("body").lower()

    assert "success" in body or "successfully" in body


def borrow_book_via_ui(page, title, patron_id):
    """Borrow a specific book identified by its title."""
    page.goto(f"{BASE_URL}/catalog")
    page.wait_for_timeout(500)

    row = page.locator("tr", has_text=title)
    row.locator("input[name='patron_id']").fill(patron_id)
    row.locator("button.btn-success").click()

    page.wait_for_timeout(1200)
    body = page.inner_text("body").lower()

    assert "successfully borrowed" in body


# -------------------------------------------------------------
#  MAIN E2E TEST
# -------------------------------------------------------------
def test_add_and_borrow_flow():
    """Full E2E test flow for adding and borrowing a book."""

    unique_isbn = "9" + "".join(str(random.randint(0, 9)) for _ in range(12))
    title = "PW E2E Book"
    author = "Automation Tester"
    copies = "5"

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()

        # Check catalog loads
        page.goto(f"{BASE_URL}/catalog")
        assert "catalog" in page.inner_text("body").lower()

        # Add a book
        add_book_via_ui(page, title, author, unique_isbn, copies)

        # Verify it's in the catalog
        page.goto(f"{BASE_URL}/catalog")
        body = page.inner_text("body").lower()
        assert title.lower() in body
        assert author.lower() in body

        # Borrow it
        borrow_book_via_ui(page, title, patron_id="123456")

        browser.close()
