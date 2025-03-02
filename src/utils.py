import os
import json
import time
import random
import requests
import datetime

import pandas as pd
import undetected_chromedriver as uc

from fake_useragent import UserAgent
from selenium.webdriver.support.ui import WebDriverWait


def update_json_with_current_time(json_file):
    current_day = datetime.datetime.today().strftime("%A")
    current_time = datetime.datetime.now()

    with open(json_file, "r") as file:
        data = json.load(file)

    current_time_float = float(
        f"{current_time.hour}.{str(current_time.minute).zfill(2)}"
    )
    data[current_day].append(float(current_time_float))

    with open(json_file, "w") as file:
        json.dump(data, file)


def update_df_with_appointment(df_file, city, address, document):
    now = datetime.datetime.now()
    current_day = now.strftime("%A")  # Example: 'Monday'
    current_date = now.strftime("%Y-%m-%d")  # Example: '2024-02-26'
    current_time = now.strftime("%H:%M")

    if os.path.exists(df_file):
        df = pd.read_csv(df_file)
    else:
        columns = ["Date", "Day", "Time", "City", "Address", "Document"]
        df = pd.DataFrame(columns=columns)

    new_row = pd.DataFrame(
        [[current_date, current_day, current_time, city, address, document]],
        columns=df.columns,
    )
    df = pd.concat([df, new_row], ignore_index=True)

    df.to_csv(df_file, index=False)


def random_delay(min, max):
    time.sleep(random.uniform(min, max))


def send_discord_message(webhook_url, message, logger):
    data = {
        "content": message,
    }
    response = requests.post(webhook_url, json=data)
    if response.status_code == 204:
        logger.info("Message sent to Discord successfully.")
    else:
        logger.error(f"Failed to send message to Discord: {response.text}")


def chrome_options(headless=True):
    options = uc.ChromeOptions()

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")

    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors")
    options.add_argument("--allow-insecure-localhost")
    options.add_argument("--disable-web-security")

    # Mimic regular browser behavior
    options.add_argument("--start-maximized")

    # adding argument to disable the AutomationControlled flag
    options.add_argument("--disable-blink-features=AutomationControlled")

    # options.add_experimental_option("useAutomatadd_experimental_optionionExtension", False)

    # Use history data
    home_directory = os.path.expanduser(
        "~"
    )  # Expands '~' to the full home directory path
    user_data_dir = f"{home_directory}/.config/google-chrome/Default"
    options.add_argument(f"--user-data-dir={user_data_dir}")
    # options.add_argument("--user-data-dir=/tmp/selenium-profile")
    # options.add_argument("--user-data-dir=~/.config/google-chrome/Default")

    options.add_argument(f"--user-agent={UserAgent().random}")

    options.add_argument("accept-language=es-ES,es;q=0.9,en;q=0.8")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    return options


def is_within_time_ranges(time_ranges):
    """
    Check if current time is within any of the specified time ranges

    Args:
        time_ranges: List of tuples with (start_time, end_time) in format "HH:MM"

    Returns:
        bool: True if current time is within any of the ranges
    """
    current_time = datetime.datetime.now().time()

    for start_time, end_time in time_ranges:
        start = datetime.time(
            int(start_time.split(":")[0]), int(start_time.split(":")[1])
        )
        end = datetime.time(int(end_time.split(":")[0]), int(end_time.split(":")[1]))

        if start <= current_time <= end:
            return True

    return False

def wait_page_loaded(driver, t=20):
    WebDriverWait(driver, t).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )