from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

class WebDriverManager:
    def __init__(self):
        self.drivers = {}

    def create_driver(self, session_id):
        options = webdriver.FirefoxOptions()
        options.add_argument("--start-maximized")
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
        self.drivers[session_id] = driver
        return driver

    def get_driver(self, session_id):
        return self.drivers.get(session_id)

    def remove_driver(self, session_id):
        driver = self.drivers.pop(session_id, None)
        if driver:
            driver.quit()
