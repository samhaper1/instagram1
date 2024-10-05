## Overview main.py

This script is a Flask application that automates the Instagram login process using Selenium WebDriver. It includes handling for cookies, 2FA (Two-Factor Authentication), and saving session cookies for future use.

Disclaimer: This script was tailored for the German Instagram page. To use it in other languages, change the button text within the script.

Disclaimer: This project is intended for educational purposes only. It must not be used for any illegal or malicious activities. The authors of this project are not responsible for any misuse of the code. Use responsibly.


### Key Features

1. **Flask Web Server**:
   - Sets up a Flask web server with session management and endpoints to handle login and 2FA processes.
   - Utilizes `waitress` to serve the application.

2. **Session Management**:
   - Uses Flask's session management to store user credentials and session identifiers securely.

3. **WebDriver Management**:
   - Manages WebDriver instances using a custom `WebDriverManager`.
   - Handles the creation, retrieval, and removal of WebDriver instances.

4. **Instagram Login Automation**:
   - Automates the login process to Instagram, including handling cookies, entering credentials, and clicking the login button.
   - Implements methods to determine and handle login problems, such as requiring 2FA or handling unexpected URL redirects.

5. **2FA Handling**:
   - Provides mechanisms to handle 2FA, including sending and entering verification codes.
   - Supports finding and clicking elements related to 2FA choices.

6. **Cookie Management**:
   - Saves session cookies to a file for later use.
   - Updates an `input.txt` file with the details of the login sessions.

7. **Error Handling and Logging**:
   - Comprehensive error handling and logging to capture and report issues during the login and 2FA processes.

### Endpoints

- `/` : Renders the login form.
- `/submit` : Handles login form submission and initiates the login process.
- `/2fa` : Handles submission of 2FA codes.
- `/get-2fa-choices` : Retrieves and sends back available 2FA choices.
- `/verify-code` : Verifies the entered 2FA code.


## Overview cookie_user.py

This script automates the process of loading cookies into a Selenium WebDriver session for Instagram. It allows for seamless login by using previously saved cookies, eliminating the need to re-enter login credentials. The script also provides a simple way to close the browser based on user input.

### Key Features

1. **Load Cookies**:
   - Loads cookies from a specified file and adds them to the Selenium WebDriver session.
   - This enables the browser to recognize the user without requiring a login.

2. **Browser Initialization**:
   - Initializes a Selenium WebDriver instance using Chrome.

3. **Navigation**:
   - Navigates to Instagram and loads the webpage.

4. **Apply Cookies**:
   - Applies the loaded cookies to the current WebDriver session and refreshes the page to authenticate the user.

5. **User-Controlled Browser Session**:
   - Keeps the browser session open and allows the user to close it by typing "JA".

### Usage

1. **Loading Cookies**:
   - Cookies are loaded from a file named `cookies_<file_number>.json` located in the `../cookies` directory.
   - The `file_number` variable should be set to the desired cookie file number to load.

2. **Running the Script**:
   - The script initializes the browser, loads cookies, refreshes the page to apply them, and then waits for user input to close the browser.

3. **Exiting the Script**:
   - The browser can be closed by entering "JA" when prompted.

### Example

To use this script:
1. Ensure you have a cookies file (e.g., `cookies_14.json`) in the `../cookies` directory.
2. Set the `file_number` variable to the desired file number.
3. Run the script and it will load the cookies, navigate to Instagram, and wait for you to decide when to close the browser.
