#!/usr/bin/env python3

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import os
import datetime
from citaprevia.utils import update_json_with_current_time
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import random

import logging
from fake_useragent import UserAgent

ua = UserAgent()

def create_driver(headless=True):
    options = uc.ChromeOptions()

    if headless:
        options.add_argument('--headless=new')
        options.add_argument('--disable-gpu')

    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors")
    options.add_argument("--allow-insecure-localhost")
    options.add_argument("--disable-web-security")

    # Mimic regular browser behavior
    options.add_argument('--start-maximized')

    # adding argument to disable the AutomationControlled flag 
    options.add_argument('--disable-blink-features=AutomationControlled')


    # options.add_experimental_option("useAutomatadd_experimental_optionionExtension", False) 

    # Use history data
    home_directory = os.path.expanduser("~")  # Expands '~' to the full home directory path
    user_data_dir = f"{home_directory}/.config/google-chrome/Default"
    options.add_argument(f"--user-data-dir={user_data_dir}")
    # options.add_argument("--user-data-dir=/tmp/selenium-profile")
    # options.add_argument("--user-data-dir=~/.config/google-chrome/Default")

    # options.add_argument(f"--user-agent={ua.ranadd_experimental_optiondom}")
    options.add_argument(f"--user-agent={ua.random}")

    options.add_argument("accept-language=es-ES,es;q=0.9,en;q=0.8")

    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    return uc.Chrome(
        headless=headless,
        options=options,
        driver_executable_path="/opt/chromedriver-linux64/chromedriver",
        browser_executable_path="/usr/bin/google-chrome",
        version_main=131
    )

def random_delay(min, max):
    time.sleep(random.uniform(min, max))


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    filename='citaprevia.log',
    filemode='a'  # or 'w' to overwrite each time
)

logger = logging.getLogger(__name__)

def send_discord_message(webhook_url, message):
    data = {
        "content": message,
    }
    response = requests.post(webhook_url, json=data)
    if response.status_code == 204:
        logger.info(f"Message sent to Discord successfully.")
    else:
        logger.error(f"Failed to send message to Discord: {response.text}")

webhook_url = "https://discord.com/api/webhooks/1328049126075797536/oWw-EP60901AUv8EEj1yofx0XB8-LMzR3KVHzvTpa1bsGhZlhn_hFpWq9d9PH9LYeW-h"
MIN = 2
MAX = 4
def main(headless=True):
    
    driver = create_driver(headless)
    wait = WebDriverWait(driver, 10)

    # changing the property of the navigator value for webdriver to undefined 
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
        })
        """
    })

    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    driver.execute_cdp_cmd(
        "Network.setExtraHTTPHeaders",
        {"headers": {"User-Agent": ua.random, "Referer": "https://icp.administracionelectronica.gob.es/icpplus/index.html"}}
    )
    driver.implicitly_wait(0.25)

    cookies = driver.get_cookies()
    for cookie in cookies:
        driver.add_cookie(cookie)

    try:
        logger.info(f"Initializing Chrome driver...")

        
        url = "https://icp.administracionelectronica.gob.es/icpplus/index.html"
        driver.get(url)
        random_delay(MIN, MAX)

        
        # wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

        logger.info(f"Starting CUE procedure...")

        random_delay(MIN, MAX)
        # Select province
        # element = wait.until(EC.presence_of_element_located((By.ID, 'form')))
        element = driver.find_element(By.ID, 'form')
        select = Select(element)
        select.select_by_visible_text('Valencia')
        random_delay(MIN, MAX)

        element = driver.find_element(By.ID, 'btnAceptar')
        element.click()

        # element = wait.until(EC.element_to_be_clickable((By.ID, "btnAceptar")))
        # driver.execute_script("arguments[0].scrollIntoView(true);", element)
        random_delay(MIN, MAX)

        logger.info(f"CUE procedure in progress...")

        # Select comisaria

        # time.sleep(random.uniform(2, 5))
        random_delay(MIN, MAX)
        element = wait.until(EC.presence_of_element_located((By.ID, 'sede')))
        select = Select(element)
        select.select_by_visible_text('CNP-COMISARIA DE BAILEN, Bailen, 9, VALENCIA')
        random_delay(MIN, MAX)
        
        element = wait.until(EC.presence_of_element_located((By.ID, 'tramiteGrupo[0]')))
        # toggle_option = driver.find_element(By.ID, '')
        select = Select(element)
        select.select_by_visible_text('POLICIA-CERTIFICADO DE REGISTRO DE CIUDADANO DE LA U.E.')
        random_delay(MIN, MAX)
        element = wait.until(EC.element_to_be_clickable((By.ID, "btnAceptar")))
        # driver.execute_script("arguments[0].scrollIntoView(true);", element)
        element.click()
        
        random_delay(MIN, MAX)
        element = wait.until(EC.element_to_be_clickable((By.ID, "btnEntrar")))
        element.click()

        # Insert personal data
        # random_delay(MIN, MAX)
        # element = wait.until(EC.element_to_be_clickable((By.ID, "btnAceptar")))
        # element.click()
        random_delay(MIN, MAX)
        element = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@id='rdbTipoDocPas' and @value='PASAPORTE']")))
        element.click()


        element = wait.until(EC.presence_of_element_located((By.ID, "txtIdCitado"))).send_keys("YB6548687")
        # element = driver.find_element(By.ID, "txtIdCitado").send_keys("Z2800743S")
        # element = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/main/div/div/section/div[2]/form/div/div/div[1]/div[2]/div/div/div[2]/input"))
        # )
        # element.send_keys("Z2800743S")
        # pasaporte_field = driver.find_element(By.ID, "txtIdCitado").send_keys("YB6548687")  
        # for char in "YB6548687":
        #     pasaporte_field.send_keys(char)
        #     time.sleep(random.uniform(0.1, 0.3))
        # time.sleep(random.uniform(2, 5))
        element = wait.until(EC.presence_of_element_located((By.ID, "txtDesCitado"))).send_keys("LORENZO POZZI")
    

        # name_field = driver.find_element(By.ID, "txtDesCitado").send_keys("LORENZO POZZI")  
        # for char in "LORENZO POZZI":
        #     name_field.send_keys(char)
        #     time.sleep(random.uniform(0.1, 0.3))

        random_delay(MIN, MAX)
        element = wait.until(EC.element_to_be_clickable((By.ID, "btnEnviar")))
        element.click()
        # button = driver.find_element(By.ID, "btnEnviar").click()

        random_delay(MIN, MAX)
        element = wait.until(EC.element_to_be_clickable((By.ID, "btnEnviar")))
        element.click()
        
        # button = driver.find_element(By.ID, "btnEnviar").click()
        current_url = driver.current_url

        elements = driver.find_elements(By.XPATH, '/html/body/div[1]/div/main/div/div[2]/section/div[2]/form/div[1]/p')

        if elements:
            send_discord_message(webhook_url, current_url)
            driver.save_screenshot("screenshot_yes.png")
            with open("page_source_success.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)

            update_json_with_current_time("citaprevia/data.json")
            logger.info("A cita was found!")
        else:
            current_day = datetime.datetime.today().strftime('%A')
            logger.info(f'No citas on {current_day} at {datetime.datetime.now().hour}:{datetime.datetime.now().minute}')

        random_delay(MIN, MAX)

    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
        send_discord_message(webhook_url, f"Script failed on {current_day} at {datetime.datetime.now().hour}:{datetime.datetime.now().minute}: {str(e)}")

    finally:
        logger.info("Closing driver...")
        driver.quit()

if __name__ == "__main__":
    main()