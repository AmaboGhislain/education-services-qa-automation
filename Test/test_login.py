import pytest
from pages.login_page import LoginPage


def test_successful_login(driver):
    driver.get("https://www.saucedemo.com/")

    login_page = LoginPage(driver)

    login_page.login(
        "standard_user",
        "secret_sauce"
    )

    assert "inventory" in driver.current_url


@pytest.mark.parametrize(
    "username, password",
    [
        ("wrong_user", "wrong_password"),
        ("standard_user", "wrong_password"),
        ("wrong_user", "secret_sauce"),
    ]
)
def test_invalid_login(driver, username, password):
    driver.get("https://www.saucedemo.com/")

    login_page = LoginPage(driver)

    login_page.login(
        "wrong_user",
        "wrong_password"
    )

    assert login_page.is_error_message_displayed()

    error_message = login_page.get_error_message()

    assert "Username and password do not match" in error_message