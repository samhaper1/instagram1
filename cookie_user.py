from selenium import webdriver
from pathlib import Path
import json


# Function to load cookies from a specified file
def load_cookies(driver, file_number):
    cookies_folder = Path('../cookies')
    cookie_file = cookies_folder / f'cookies_{file_number}.json'

    if cookie_file.exists():
        cookies = json.loads(cookie_file.read_text())
        for cookie in cookies:
            driver.add_cookie(cookie)
        print(f"Cookies loaded from {cookie_file}")
    else:
        print(f"No cookie file found for {cookie_file}")


# Initialize the browser
driver = webdriver.Chrome()

# Navigate to the same website
driver.get("https://www.instagram.com/")

# Load cookies from the file
file_number = 14  # Change this to the desired file number
load_cookies(driver, file_number)

# Refresh the page to apply the cookies
driver.refresh()

# Continue with your browsing actions
# ...
while True:
    x = input("QUIT?")
    if x == "JA":
        driver.quit()
# Close the browser
