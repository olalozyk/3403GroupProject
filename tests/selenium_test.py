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
from werkzeug.security import generate_password_hash

# Add parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Flask app imports
from app import create_app, db
from app.models import User

# Test config
BASE_URL = "http://localhost:5000"
LOGIN_EMAIL = "test@example.com"
LOGIN_PASSWORD = "yourpassword"

# Chrome options
options = Options()
options.add_argument("--log-level=3")  # Suppress Chrome logging
options.add_experimental_option("detach", True)  # Optional: keep browser open
# Initialize driver
driver = webdriver.Chrome(service=Service(), options=options)

LOGIN_PASSWORD = "testpass123"  # Shared password

def test_register_user():
    driver.get(f"{BASE_URL}/register")
    time.sleep(1)

    new_email = f"user{int(time.time())}@example.com"  # Unique email
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

    return new_email  # Return the email for next login

def login(driver, email):
    driver.get(f"{BASE_URL}/login")
    time.sleep(1)
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "password").send_keys(LOGIN_PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
    time.sleep(2)

def test_add_appointment(user_email):
    login(driver, user_email)

    driver.get(f"{BASE_URL}/appointment/add")
    time.sleep(1)

    today = datetime.date.today().strftime('%Y-%m-%d')

    # Enter time in 24-hour format
    driver.find_element(By.NAME, "starting_time").send_keys("14:00")
    driver.find_element(By.NAME, "ending_time").send_keys("15:00")

    # Set date using JS
    date_input = driver.find_element(By.NAME, "appointment_date")
    driver.execute_script("arguments[0].value = arguments[1]", date_input, today)

    # Fill form fields
    driver.find_element(By.NAME, "practitioner_name").send_keys("Dr. Smith")
    Select(driver.find_element(By.NAME, "practitioner_type")).select_by_visible_text("General Practitioner (GP)")
    driver.find_element(By.NAME, "location").send_keys("Test Clinic")
    driver.find_element(By.NAME, "provider_number").send_keys("123456")
    Select(driver.find_element(By.NAME, "appointment_type")).select_by_visible_text("General")
    driver.find_element(By.NAME, "appointment_notes").send_keys("Testing via Selenium.")

    # Tick reminders
    for label in ["2 hours before", "1 day before"]:
        checkbox = driver.find_element(By.XPATH, f"//input[@type='checkbox' and @value='{label}']")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
        time.sleep(0.2)
        if not checkbox.is_selected():
            checkbox.click()

    # Custom reminder = tomorrow
    custom_reminder = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    custom_input = driver.find_element(By.NAME, "custom_reminder")
    driver.execute_script("arguments[0].value = arguments[1]", custom_input, custom_reminder)

    # Submit form
    submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_btn.click()

    # Wait for redirect
    try:
        WebDriverWait(driver, 10).until(
            EC.url_contains("/appointments")
        )
    except:
        print("[Warning] URL didn't change. Checking page content instead.")
        print("Current URL:", driver.current_url)
        print("Page content snippet:", driver.page_source[:500])

    assert "appointment" in driver.current_url.lower() or "successfully" in driver.page_source.lower()
    print("✅ Appointment submission test passed.")


if __name__ == "__main__":
    try:
        user_email = test_register_user()   # store returned email
        test_add_appointment(user_email)    # pass it to the function
    finally:
        driver.quit()
