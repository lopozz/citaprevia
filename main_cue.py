#!/usr/bin/env python3

import os
import time
import logging
import datetime

from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.utils import (
    random_delay,
    send_discord_message,
    update_df_with_appointment,
    create_driver,
    is_within_time_ranges,
)


WEBHOOK_URL = os.environ["WEBHOOK_URL"]
MIN = 2
MAX = 4
CITY = "Valencia"
OFICINA = None  # "CNP-COMISARIA DE BAILEN, Bailen, 9, VALENCIA"
URL = "https://sede.administracionespublicas.gob.es/pagina/index/directorio/icpplus"
DEFAULT_INTERVAL = 20
TARGETED_INTERVAL = 5
TARGET_TIMES = [("9:20", "9:40")]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    filename="./citaprevia.log",
    filemode="a",
)

logger = logging.getLogger(__name__)


def check_cue(headless=False):
    driver = create_driver(headless)
    wait = WebDriverWait(driver, 10)

    # changing the property of the navigator value for webdriver to undefined
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
        Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
        })
        """
        },
    )

    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    driver.execute_cdp_cmd(
        "Network.setExtraHTTPHeaders",
        {
            "headers": {
                "User-Agent": UserAgent().random,
                "Referer": URL,
            }
        },
    )
    driver.implicitly_wait(0.25)

    # cookies = driver.get_cookies()
    # for cookie in cookies:
    #     driver.add_cookie(cookie)
    driver.delete_all_cookies()

    try:
        logger.info("Initializing Chrome driver...")

        driver.get(URL)
        random_delay(MIN, MAX)

        element = wait.until(EC.element_to_be_clickable((By.ID, "submit")))
        element.click()

        random_delay(MIN, MAX)

        # Select province
        element = wait.until(EC.presence_of_element_located((By.ID, "form")))
        select = Select(element)
        select.select_by_visible_text(CITY)
        random_delay(MIN, MAX)
        element = wait.until(EC.element_to_be_clickable((By.ID, "btnAceptar")))
        element.click()

        # Select oficina
        random_delay(MIN, MAX)
        logger.info("CUE procedure in progress...")

        if OFICINA:
            element = wait.until(EC.presence_of_element_located((By.ID, "sede")))
            select = Select(element)
            select.select_by_visible_text(OFICINA)
            random_delay(MIN, MAX)
            element = wait.until(
                EC.presence_of_element_located((By.ID, "tramiteGrupo[0]"))
            )
            select = Select(element)
            select.select_by_visible_text(
                "POLICIA-CERTIFICADO DE REGISTRO DE CIUDADANO DE LA U.E."
            )
        else:
            element = wait.until(
                EC.presence_of_element_located((By.ID, "tramiteGrupo[1]"))
            )
            select = Select(element)
            select.select_by_visible_text(
                "POLICIA-CERTIFICADO DE REGISTRO DE CIUDADANO DE LA U.E."
            )
        random_delay(MIN, MAX)
        element = wait.until(EC.element_to_be_clickable((By.ID, "btnAceptar")))
        element.click()

        random_delay(MIN, MAX)
        element = wait.until(EC.element_to_be_clickable((By.ID, "btnEntrar")))
        element.click()

        # Insert personal data
        random_delay(MIN, MAX)
        element = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//input[@id='rdbTipoDocPas' and @value='PASAPORTE']")
            )
        )
        element.click()

        element = wait.until(
            EC.presence_of_element_located((By.ID, "txtIdCitado"))
        ).send_keys("YB6548687")
        element = wait.until(
            EC.presence_of_element_located((By.ID, "txtDesCitado"))
        ).send_keys("LORENZO POZZI")

        random_delay(MIN, MAX)
        element = wait.until(EC.element_to_be_clickable((By.ID, "btnEnviar")))
        element.click()

        random_delay(MIN, MAX)
        element = wait.until(EC.element_to_be_clickable((By.ID, "btnEnviar")))
        element.click()

        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        if "En este momento no hay citas disponibles" in driver.page_source:
            current_day = datetime.datetime.today().strftime("%A")
            logger.info("❌ No citas...")
        elif (
            "Su sesión ha caducado por permanecer demasiado tiempo inactiva"
            in driver.page_source
        ):
            current_day = datetime.datetime.today().strftime("%A")
            logger.error("⚠️ Error inactive session...")
        else:
            logger.info("✅ A cita was found!")
            with open(
                f"page_source_success_{str(datetime.datetime.now()).replace(' ', '_')}.html",
                "w",
                encoding="utf-8",
            ) as f:
                f.write(driver.page_source)

            update_df_with_appointment(
                "appointments.csv",
                CITY,
                OFICINA,
                "CUE",
            )

            send_discord_message(WEBHOOK_URL, URL, logger)

    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
        current_day = datetime.datetime.today().strftime("%A")
        with open(
            f"error_page_{current_day}-{datetime.datetime.now().hour}-{str(datetime.datetime.now().minute).zfill(2)}.html",
            "w",
            encoding="utf-8",
        ) as f:
            f.write(driver.page_source)
        send_discord_message(
            WEBHOOK_URL,
            f"Script failed on {current_day} at {datetime.datetime.now().hour}:{str(datetime.datetime.now().minute).zfill(2)}: {str(e)}",
            logger,
        )

    finally:
        logger.info("Closing driver...")
        driver.quit()


def main(headless=False):
    while True:
        if is_within_time_ranges(TARGET_TIMES):
            logger.info("Running in targeted mode!")
            check_cue(headless)
            next_interval = TARGETED_INTERVAL
        else:
            logger.info("Running in default mode...")
            check_cue(headless)
            next_interval = DEFAULT_INTERVAL

        logger.info(f"Sleeping for {next_interval} minutes before the next execution.")
        time.sleep(next_interval * 60)


if __name__ == "__main__":
    main()
