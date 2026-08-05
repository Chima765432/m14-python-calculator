import uuid

import pytest
from playwright.sync_api import expect


def unique_email():
    return f"user{uuid.uuid4().hex[:8]}@example.com"


@pytest.mark.e2e
def test_register_with_valid_data_shows_success(page, live_server):
    email = unique_email()
    page.goto(f"{live_server}/register")
    page.fill("#username", email.split("@")[0])
    page.fill("#email", email)
    page.fill("#password", "longenough1")
    page.fill("#confirm", "longenough1")
    page.click("#submit")
    expect(page.locator("#success")).to_have_text("Registration successful")


@pytest.mark.e2e
def test_login_with_correct_credentials_stores_token(page, live_server):
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
    assert page.evaluate("localStorage.getItem('access_token')")


@pytest.mark.e2e
def test_register_with_short_password_shows_error(page, live_server):
    page.goto(f"{live_server}/register")
    page.fill("#username", "shorty")
    page.fill("#email", unique_email())
    page.fill("#password", "short")
    page.fill("#confirm", "short")
    page.click("#submit")
    expect(page.locator("#error")).to_contain_text("at least 8 characters")


@pytest.mark.e2e
def test_login_with_wrong_password_shows_error(page, live_server):
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
    page.fill("#password", "wrongpassword1")
    page.click("#submit")
    expect(page.locator("#error")).to_have_text("Invalid credentials")
