import os
from datetime import datetime, timedelta
import image_data
import text_data
import constants


# Change here the way you get the data
def get_processed_data(folder):
    get_text_data(folder)
    is_table_valid = check_table_validity(folder)
    if not is_table_valid:
        return get_last_valid_folder(folder)
    return folder


def get_image_data(folder):
    image_data.scrape_image(folder)
    image_data.process_image(folder)


def get_text_data(folder):
    text_data.scrape_page(folder)
    text_data.process_page(folder)


def check_table_validity(folder):
    with open(f"{folder}/{constants.gpv_table}", "r") as file:
        return not any("u" in row for row in file.readlines())


def get_last_valid_folder(folder):
    *other, date, hour = folder.split("/")
    previous_time = current_time = datetime.strptime(f"{date} {hour}", "%d%m%Y %H%M")
    valid_folder = ""
    for i in range(constants.HOURS * 2):
        previous_time = current_time - timedelta(minutes=30)
        previous_folder = (
            f"{constants.general_folder}/{previous_time.strftime('%d%m%Y/%H%M')}"
        )
        if os.path.exists(previous_folder):
            valid_folder = previous_folder
            break
        current_time = previous_time
    return valid_folder
