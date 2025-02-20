import json
import time
import random
import requests
import datetime


def update_json_with_current_time(json_file):
    # Get the current day and time
    current_day = datetime.datetime.today().strftime(
        "%A"
    )  # Get full day name (e.g., "Monday")
    current_time = (
        datetime.datetime.now().hour + datetime.datetime.now().minute / 60.0
    )  # Convert time to float

    try:
        # Load the JSON file
        with open(json_file, "r") as file:
            data = json.load(file)

        # Append the current time to the corresponding day
        if current_day in data:
            data[current_day].append(
                round(current_time, 2)
            )  # Round to 2 decimal places

        # Save the updated JSON file
        with open(json_file, "w") as file:
            json.dump(data, file, indent=4)

        print(f"Updated {current_day} with time: {round(current_time, 2)}")

    except Exception as e:
        print(f"Error updating JSON: {e}")


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
