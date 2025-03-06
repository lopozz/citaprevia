import os
import time
import logging
import datetime

import undetected_chromedriver as uc

from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.utils import (
    random_delay,
    send_discord_message,
    update_df_with_appointment,
    chrome_options,
    wait_page_loaded,
    generate_schedule,
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
OUTPUT_DIR = "output"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    filename=os.path.join(OUTPUT_DIR, "citaprevia.log"),
    filemode="a",
)

logger = logging.getLogger(__name__)


def check_cue(headless=False):
    options = chrome_options(headless)

    driver = uc.Chrome(
        headless=headless,
        options=options,
        # driver_executable_path="/opt/chromedriver-linux64/chromedriver",
        # browser_executable_path="/usr/bin/google-chrome",
        # version_main=131,
    )

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
        driver.get(URL)
        random_delay(MIN, MAX)

        logger.info("CUE procedure in progress...")
        element = wait.until(EC.element_to_be_clickable((By.ID, "submit")))
        element.click()

        # wait_page_loaded(driver, 20)

        random_delay(4, 7)

        # Select province
        element = wait.until(EC.presence_of_element_located((By.ID, "form")))
        select = Select(element)
        select.select_by_visible_text(CITY)
        random_delay(MIN, MAX)
        element = wait.until(EC.element_to_be_clickable((By.ID, "btnAceptar")))
        element.click()

        random_delay(MIN, MAX)
        # wait_page_loaded(driver, 20)

        # Select oficina

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
        # wait_page_loaded(driver, 20)

        element = wait.until(EC.element_to_be_clickable((By.ID, "btnEntrar")))
        element.click()

        random_delay(MIN, MAX)
        # wait_page_loaded(driver, 20)

        # Insert personal data

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
        # wait_page_loaded(driver, 20)

        element = wait.until(EC.element_to_be_clickable((By.ID, "btnEnviar")))
        element.click()

        wait_page_loaded(driver, 20)

        if "En este momento no hay citas disponibles" in driver.page_source:
            logger.info("No citas...")
        elif (
            "Su sesión ha caducado por permanecer demasiado tiempo inactiva"
            in driver.page_source
        ):
            logger.error("🚨 Error inactive session...")
        elif "requested URL was rejected" in driver.page_source:
            logger.error("🚨 Bot was detected...")
        else:
            current_day = datetime.datetime.today().strftime("%A")
            select_element = driver.find_element(By.ID, "idSede")
            options = select_element.find_elements(By.TAG_NAME, "option")

            for option in options:
                logger.info(f"A cita was found on {current_day} in {option.text}!")

                update_df_with_appointment(
                    os.path.join(OUTPUT_DIR, "appointments.csv"),
                    CITY,
                    option.text,
                    "CUE",
                )
                if option.text == "CNP-COMISARIA DE BAILEN, Bailen, 9, VALENCIA":
                    logger.info(
                        f"✅ A cita was found on {current_day} in {option.text}!"
                    )
                    send_discord_message(
                        WEBHOOK_URL, f"Cita found in {option.text}: {URL}", logger
                    )

                    success_page_dir = os.path.join(
                        OUTPUT_DIR,
                        f"success_page_{str(datetime.datetime.now()).replace(' ', '_')}.html",
                    )
                    with open(
                        success_page_dir,
                        "w",
                        encoding="utf-8",
                    ) as f:
                        f.write(driver.page_source)

    except Exception as e:
        logger.error(f"❌ Script failed: {str(e)}")
        current_day = datetime.datetime.today().strftime("%A")
        error_page_dir = os.path.join(
            OUTPUT_DIR,
            f"error_page_{current_day}-{datetime.datetime.now().hour}-{str(datetime.datetime.now().minute).zfill(2)}.html",
        )
        with open(
            error_page_dir,
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


def main(headless=True):
    while True:
        job_times = generate_schedule()

        for run_time in job_times:
            now = datetime.now()
            run_time = now.replace(
                hour=run_time.hour,
                minute=run_time.minute,
                second=run_time.second,
                microsecond=0,
            )

            # If run_time is in the past, skip to the next one
            if run_time < now:
                continue

            # Wait until the scheduled time
            wait_time = (run_time - datetime.now()).total_seconds()
            if wait_time > 0:
                time.sleep(wait_time)

            # Execute the function
            check_cue(headless)

        time.sleep(5)


# def main(headless=True):
#     while True:
#         if is_within_time_ranges(TARGET_TIMES):
#             logger.info("Initializing procedure in targeted mode!")
#             check_cue(headless)
#             next_interval = TARGETED_INTERVAL
#         else:
#             logger.info("Initializing procedure in default mode...")
#             check_cue(headless)
#             next_interval = DEFAULT_INTERVAL

#         logger.info(f"Sleeping for {next_interval} minutes before the next execution.")
#         time.sleep(next_interval * 60)


if __name__ == "__main__":
    main()
