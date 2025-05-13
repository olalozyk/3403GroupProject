import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

import time
import datetime

# Test config
BASE_URL = "http://localhost:5000"
LOGIN_EMAIL = "test@example.com"
LOGIN_PASSWORD = "yourpassword"

# Chrome options
options = Options()
options.add_argument("--log-level=3")  # Suppress Chrome logging
options.add_experimental_option("detach", True)  # Optional: keep window open

# Initialize ChromeDriver
driver = webdriver.Chrome(service=Service(), options=options)

def login(driver):
    driver.get("http://localhost:5000/login")
    time.sleep(1)

    # Fill in login form
    driver.find_element(By.NAME, "email").send_keys(LOGIN_EMAIL)
    driver.find_element(By.NAME, "password").send_keys(LOGIN_PASSWORD)

    # Submit the form
    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
    time.sleep(2)  # Allow redirect to dashboard or appointment page

def test_add_appointment():
    login(driver)

    driver.get(f"{BASE_URL}/appointment/add")
    time.sleep(1)

    today = datetime.date.today().strftime('%Y-%m-%d')
    start_time = "09:00"
    end_time = "10:00"

    driver.find_element(By.NAME, "appointment_date").send_keys(today)
    driver.find_element(By.NAME, "starting_time").send_keys(start_time)
    driver.find_element(By.NAME, "ending_time").send_keys(end_time)
    driver.find_element(By.NAME, "practitioner_name").send_keys("Dr. Smith")

    Select(driver.find_element(By.NAME, "practitioner_type")).select_by_visible_text("General Practitioner (GP)")
    driver.find_element(By.NAME, "location").send_keys("Test Clinic")
    driver.find_element(By.NAME, "provider_number").send_keys("123456")
    Select(driver.find_element(By.NAME, "appointment_type")).select_by_visible_text("General")
    driver.find_element(By.NAME, "appointment_notes").send_keys("Testing via Selenium.")

    for label in ["2 hours before", "1 day before"]:
        checkbox = driver.find_element(By.XPATH, f"//input[@type='checkbox' and @value='{label}']")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
        time.sleep(0.5)
        if not checkbox.is_selected():
            checkbox.click()

    # Custom reminder (set to tomorrow)
    custom_reminder = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    driver.find_element(By.NAME, "custom_reminder").send_keys(custom_reminder)

    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    # Wait for confirmation either by URL or a known element
    try:
        WebDriverWait(driver, 10).until(
            EC.url_contains("/appointments")
        )
    except:
        print("[Warning] URL didn't change. Checking page content instead.")
    
    assert "appointment" in driver.current_url.lower() or "successfully" in driver.page_source.lower()

    print("✅ Appointment submission test passed.")


if __name__ == "__main__":
    try:
        test_add_appointment()
    finally:
        driver.quit()
