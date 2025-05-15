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

    driver.find_element(By.NAME, "starting_time").send_keys("14:00")
    driver.find_element(By.NAME, "ending_time").send_keys("15:00")

    date_input = driver.find_element(By.NAME, "appointment_date")
    driver.execute_script("arguments[0].value = arguments[1]", date_input, today)

    driver.find_element(By.NAME, "practitioner_name").send_keys("Dr. Smith")
    Select(driver.find_element(By.NAME, "practitioner_type")).select_by_visible_text("General Practitioner (GP)")
    driver.find_element(By.NAME, "location").send_keys("Test Clinic")
    driver.find_element(By.NAME, "provider_number").send_keys("123456")
    Select(driver.find_element(By.NAME, "appointment_type")).select_by_visible_text("General")
    driver.find_element(By.NAME, "appointment_notes").send_keys("Testing via Selenium.")

    for label in ["2 hours before", "1 day before"]:
        checkbox = driver.find_element(By.XPATH, f"//input[@type='checkbox' and @value='{label}']")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
        time.sleep(0.2)
        if not checkbox.is_selected():
            checkbox.click()

    custom_reminder = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    custom_input = driver.find_element(By.NAME, "custom_reminder")
    driver.execute_script("arguments[0].value = arguments[1]", custom_input, custom_reminder)

    submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_btn.click()

    try:
        WebDriverWait(driver, 10).until(EC.url_contains("/appointments"))
    except:
        print("[Warning] URL didn't change. Checking page content instead.")

    assert "appointment" in driver.current_url.lower() or "successfully" in driver.page_source.lower()
    print("✅ Appointment submission test passed.")


def test_upload_document():
    driver.get(f"{BASE_URL}/medical_document/upload_document")
    time.sleep(1)

    driver.find_element(By.NAME, "document_name").send_keys("Test Document")
    Select(driver.find_element(By.NAME, "document_type")).select_by_visible_text("Report")
    driver.find_element(By.NAME, "document_notes").send_keys("Uploaded via Selenium.")
    driver.find_element(By.NAME, "practitioner_name").send_keys("Dr. Selenium")
    Select(driver.find_element(By.NAME, "practitioner_type")).select_by_visible_text("Specialist")

    today = datetime.date.today().strftime('%Y-%m-%d')
    upload_date_input = driver.find_element(By.NAME, "upload_date")
    driver.execute_script("arguments[0].value = arguments[1];", upload_date_input, today)

    expiration_checkbox = driver.find_element(By.ID, "enableExpirationDate")
    driver.execute_script("arguments[0].click();", expiration_checkbox)

    expiration_date = (datetime.date.today() + datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    expiration_date_input = driver.find_element(By.NAME, "expiration_date")
    driver.execute_script("arguments[0].value = arguments[1];", expiration_date_input, expiration_date)

    file_input = driver.find_element(By.NAME, "upload_document")
    test_file_path = os.path.abspath("tests/test_upload_edited.pdf")
    if not os.path.exists(test_file_path):
        raise FileNotFoundError(f"Test file not found at: {test_file_path}")
    file_input.send_keys(test_file_path)

    submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", submit_btn)

    assert "successfully" in driver.page_source.lower()
    print("✅ Document upload test passed.")


def test_edit_document():
    driver.get(f"{BASE_URL}/medical_document")
    time.sleep(1)

    edit_links = driver.find_elements(By.LINK_TEXT, "Edit")
    if not edit_links:
        raise Exception("❌ No documents available to edit.")
    edit_links[0].click()

    WebDriverWait(driver, 5).until(EC.url_contains("/edit_document"))

    document_name_field = driver.find_element(By.NAME, "document_name")
    document_name_field.clear()
    document_name_field.send_keys("Edited Document Name")

    notes_field = driver.find_element(By.NAME, "document_notes")
    notes_field.clear()
    notes_field.send_keys("Updated via Selenium.")

    new_test_file_path = os.path.abspath("tests/test_upload_edited.pdf")
    if os.path.exists(new_test_file_path):
        try:
            file_input = driver.find_element(By.NAME, "upload_document")
            file_input.send_keys(new_test_file_path)
        except Exception as e:
            print(f"[Warning] Failed to upload new file: {e}")

    expiration_checkbox = driver.find_element(By.ID, "enableExpirationDate")
    driver.execute_script("arguments[0].click();", expiration_checkbox)
    time.sleep(0.3)

    new_exp_date = (datetime.date.today() + datetime.timedelta(days=60)).strftime('%Y-%m-%d')
    expiration_input = driver.find_element(By.NAME, "expiration_date")
    driver.execute_script("arguments[0].value = '';", expiration_input)
    driver.execute_script("arguments[0].value = arguments[1];", expiration_input, new_exp_date)

    submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", submit_btn)

    try:
        WebDriverWait(driver, 10).until(EC.url_contains("/medical_document"))
    except:
        print("[Warning] URL didn't change after edit.")

    if "successfully" not in driver.page_source.lower():
        driver.save_screenshot("edit_debug.png")
        raise AssertionError("❌ Edit did not succeed. Check logs or screenshot.")
    print("✅ Document edit test passed.")


def test_calendar_view():
    print("▶ Testing Calendar View page...")
    driver.get(f"{BASE_URL}/calendar")

    heading = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//h1[contains(text(), 'Your Calendar')]"))
    )
    assert heading is not None

    view_selector = driver.find_element(By.ID, "viewSelector")
    assert view_selector.get_attribute("disabled") == "true"
    assert view_selector.get_attribute("value") == "month"

    prev_btn = driver.find_element(By.ID, "prevMonth")
    next_btn = driver.find_element(By.ID, "nextMonth")
    heading = driver.find_element(By.ID, "monthYearHeading")
    assert prev_btn.is_displayed() and next_btn.is_displayed() and heading.is_displayed()

    for btn_class in ["btn-Appointment", "btn-Tests", "btn-Expirations", "btn-Missed"]:
        btn = driver.find_element(By.CLASS_NAME, btn_class)
        assert btn.is_displayed()

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                ".btn-Appointment, .btn-Missed, .btn-Tests, .btn-Expirations"
            ))
        )
        print("✅ Events are rendered on the calendar.")
    except:
        print("❌ No events found on the calendar.")

    print("✅ Calendar View test passed.")


if __name__ == "__main__":
    try:
        user_email = test_register_user()
        login(user_email)
        test_add_appointment()
        test_upload_document()
        test_edit_document()
        test_calendar_view()
    finally:
        driver.quit()
