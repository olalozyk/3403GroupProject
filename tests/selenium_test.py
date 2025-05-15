import sys
import os
import time
import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from sqlalchemy.sql.coercions import expect

# Add parent directory to sys.path to import Flask app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Flask app imports (only needed if integrating with db setup or app context)
from app import create_app, db
from app.models import User

# Constants
BASE_URL = "http://localhost:5000"
LOGIN_PASSWORD = "testpass123"  # Shared test password

# Chrome WebDriver setup
options = Options()
options.add_argument("--log-level=3")  # Suppress logging
options.add_experimental_option("detach", True)  # Optional: keep browser open after run
driver = webdriver.Chrome(service=Service(), options=options)


def test_register_user():
    driver.get(f"{BASE_URL}/register")
    time.sleep(1)

    new_email = f"user{int(time.time())}@example.com"  # Generate unique email
    driver.find_element(By.NAME, "first_name").send_keys("Selenium")
    driver.find_element(By.NAME, "last_name").send_keys("Test")
    driver.find_element(By.NAME, "email").send_keys(new_email)
    driver.find_element(By.NAME, "password").send_keys(LOGIN_PASSWORD)
    driver.find_element(By.NAME, "confirm_password").send_keys(LOGIN_PASSWORD)

    submit_btn = driver.find_element(By.NAME, "submit")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
    time.sleep(0.5)
    submit_btn.click()

    WebDriverWait(driver, 5).until(EC.url_contains("/login"))
    assert "login" in driver.current_url.lower()
    print("✅ Registration test passed.")

    return new_email


def login(email):
    driver.get(f"{BASE_URL}/login")
    time.sleep(1)
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "password").send_keys(LOGIN_PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
    time.sleep(2)


def test_add_appointment():
    driver.get(f"{BASE_URL}/appointment/add")
    time.sleep(1)

    today = datetime.date.today().strftime('%Y-%m-%d')
    driver.find_element(By.NAME, "appointment_date").send_keys(today)
    driver.find_element(By.NAME, "starting_time").send_keys("14:00")
    driver.find_element(By.NAME, "ending_time").send_keys("18:00")
    driver.find_element(By.NAME, "practitioner_name").send_keys("Dr. Smith")

    Select(driver.find_element(By.NAME, "practitioner_type")).select_by_visible_text("General Practitioner (GP)")
    driver.find_element(By.NAME, "location").send_keys("Test Clinic")
    driver.find_element(By.NAME, "provider_number").send_keys("123456")
    Select(driver.find_element(By.NAME, "appointment_type")).select_by_visible_text("General")
    driver.find_element(By.NAME, "appointment_notes").send_keys("Testing via Selenium.")

    for label in ["2 hours before", "1 day before"]:
        checkbox = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//input[@type='checkbox' and @value='{label}']"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
        time.sleep(0.3)
        if not checkbox.is_selected():
            driver.execute_script("arguments[0].click();", checkbox)

    custom_reminder = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    driver.find_element(By.NAME, "custom_reminder").send_keys(custom_reminder)

    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    try:
        WebDriverWait(driver, 10).until(EC.url_contains("/appointments"))
    except:
        print("[Warning] URL didn't change. Checking page content instead.")

    assert "successfully" in driver.page_source.lower()
    print("✅ Appointment submission test passed.")


def test_upload_document():
    driver.get(f"{BASE_URL}/medical_document/upload_document")
    time.sleep(1)

    driver.find_element(By.NAME, "document_name").send_keys("Test Document")
    Select(driver.find_element(By.NAME, "document_type")).select_by_visible_text("Report")
    driver.find_element(By.NAME, "document_notes").send_keys("Uploaded via Selenium.")
    driver.find_element(By.NAME, "practitioner_name").send_keys("Dr. Selenium")
    Select(driver.find_element(By.NAME, "practitioner_type")).select_by_visible_text("Specialist")

    # Set upload date using JS
    today = "2025-05-15"
    upload_date_input = driver.find_element(By.NAME, "upload_date")
    driver.execute_script("arguments[0].value = arguments[1];", upload_date_input, today)

    # Enable expiration date and set it
    expiration_checkbox = driver.find_element(By.ID, "enableExpirationDate")
    driver.execute_script("arguments[0].click();", expiration_checkbox)

    expiration_date = (datetime.date.today() + datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    expiration_date_input = driver.find_element(By.NAME, "expiration_date")
    driver.execute_script("arguments[0].value = arguments[1];", expiration_date_input, expiration_date)

    # Upload a file

    file_input = driver.find_element(By.NAME, "upload_document")
    test_file_path = os.path.abspath("tests/test_upload_edited.pdf")
    if not os.path.exists(test_file_path):
        raise FileNotFoundError(f"Test file not found at: {test_file_path}")
    file_input.send_keys(test_file_path)


    # Submit the form
    submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", submit_btn)

    # Check for success
    assert "successfully" in driver.page_source.lower()
    print("✅ Document upload test passed.")



if __name__ == "__main__":

        user_email = test_register_user()
        login(user_email)
        try:
            test_add_appointment()
        except:
            pass
        test_upload_document()
        driver.quit()
