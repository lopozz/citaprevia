import json
import time
import random
import requests
import datetime


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
