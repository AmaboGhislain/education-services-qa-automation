from selenium import webdriver


def test_open_google():
    driver = webdriver.Chrome()

    driver.get("https://www.google.com")

    assert "Google" in driver.title

    driver.quit()