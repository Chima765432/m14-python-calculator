import uuid

import pytest
from playwright.sync_api import expect


def unique_email():
    return f"user{uuid.uuid4().hex[:8]}@example.com"


def register_and_login(page, live_server):
    email = unique_email()
    page.goto(f"{live_server}/register")
    page.fill("#username", email.split("@")[0])
    page.fill("#email", email)
    page.fill("#password", "longenough1")
    page.fill("#confirm", "longenough1")
    page.click("#submit")
    page.wait_for_selector("#success:not(:empty)")

    page.goto(f"{live_server}/login")
    page.fill("#email", email)
    page.fill("#password", "longenough1")
    page.click("#submit")
    page.wait_for_url("**/dashboard")


def add(page, a, b, type):
    page.fill("#a", str(a))
    page.fill("#b", str(b))
    page.select_option("#type", type)
    page.click("#add-submit")


@pytest.mark.e2e
def test_add_and_browse_calculations(page, live_server):
    register_and_login(page, live_server)
    add(page, 2, 3, "Add")
    expect(page.locator("#success")).to_have_text("Calculation added")
    add(page, 4, 5, "Multiply")
    expect(page.locator("#calculations tr")).to_have_count(2)
    expect(page.locator("#calculations tr").first.locator(".cell-result")).to_have_text("5")


@pytest.mark.e2e
def test_edit_updates_row(page, live_server):
    register_and_login(page, live_server)
    add(page, 2, 3, "Add")
    expect(page.locator("#calculations tr")).to_have_count(1)

    answers = ["10", "2", "Divide"]

    def answer(dialog):
        dialog.accept(answers.pop(0) if answers else "")

    page.on("dialog", answer)
    page.click(".edit")

    expect(page.locator("#success")).to_have_text("Calculation updated")
    expect(page.locator("#calculations tr").first.locator(".cell-result")).to_have_text("5")


@pytest.mark.e2e
def test_delete_removes_row(page, live_server):
    register_and_login(page, live_server)
    add(page, 2, 3, "Add")
    expect(page.locator("#calculations tr")).to_have_count(1)
    page.click(".delete")
    expect(page.locator("#success")).to_have_text("Calculation deleted")
    expect(page.locator("#calculations tr")).to_have_count(0)


@pytest.mark.e2e
def test_non_numeric_operand_is_rejected_in_browser(page, live_server):
    register_and_login(page, live_server)
    add(page, "abc", 3, "Add")
    expect(page.locator("#error")).to_have_text("Both operands must be numbers")
    expect(page.locator("#calculations tr")).to_have_count(0)


@pytest.mark.e2e
def test_divide_by_zero_is_rejected_in_browser(page, live_server):
    register_and_login(page, live_server)
    add(page, 10, 0, "Divide")
    expect(page.locator("#error")).to_have_text("Cannot divide by zero")
    expect(page.locator("#calculations tr")).to_have_count(0)


@pytest.mark.e2e
def test_dashboard_without_token_shows_not_authenticated(page, live_server):
    page.goto(f"{live_server}/dashboard")
    page.evaluate("localStorage.removeItem('access_token')")
    page.reload()
    expect(page.locator("#auth-error")).to_have_text("Not authenticated. Please log in.")
    expect(page.locator("#calculations tr")).to_have_count(0)
