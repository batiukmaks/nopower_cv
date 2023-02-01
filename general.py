from datetime import datetime
import os
import shutil
import pytz
import constants
from data_retrieving import get_processed_data


def get_folder_with_latest_valid_data():
    is_latest = True
    valid_folder = latest_time_folder = get_newest_folder()
    if not os.path.exists(latest_time_folder):
        os.makedirs(latest_time_folder)
        valid_folder = get_processed_data(latest_time_folder)
    if valid_folder != latest_time_folder:
        shutil.rmtree(latest_time_folder)
        is_latest = False
    return (valid_folder, is_latest)


def get_newest_folder():
    return "/".join(
        [
            constants.general_folder,
            get_current_date(),
            get_last_updated_time(constants.website_url),
        ]
    )


def get_current_date() -> str:
    now = datetime.now(pytz.timezone("Europe/Kyiv"))
    date = now.strftime("%d%m%Y")
    return date


def get_last_updated_time(url) -> str:
    now = datetime.now(pytz.timezone("Europe/Kyiv"))
    hour, minute = [int(s) for s in now.strftime("%H %M").split()]
    minute = 0 if minute < 30 else 30
    return f"{hour:02}{minute:02}"
