from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class LoginPage:

    USERNAME = (By.ID, "user-name")
    PASSWORD = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "[data-test='error']")

    def __init__(self, driver):
        self.driver = driver

    def wait_for_element(self, locator):
        return WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(locator)
        )

    def enter_username(self, username):
        self.wait_for_element(self.USERNAME).send_keys(username)

    def enter_password(self, password):
        self.wait_for_element(self.PASSWORD).send_keys(password)

    def click_login(self):
        self.wait_for_element(self.LOGIN_BUTTON).click()

    def login(self, username, password):
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()

    def is_error_message_displayed(self):
        return self.wait_for_element(self.ERROR_MESSAGE).is_displayed()

    def get_error_message(self):
        return self.wait_for_element(self.ERROR_MESSAGE).text