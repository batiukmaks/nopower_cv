from datetime import datetime, timedelta
import os
import shutil
import pytz
import constants


def get_newest_folder(url):
    return "/".join(
        [constants.general_folder, get_current_date(), get_last_updated_time(url)]
    )


def get_current_date() -> str:
    now = datetime.now(pytz.timezone("Europe/Kyiv"))
    date = now.strftime("%d%m%Y")
    return date


# Parse last updated time from dynamic website
# def get_last_updated_time(url) -> str:
#     client = ScrapingAntClient(token=os.environ.get('ScrapingAntClient_token'))
#     page_content = client.general_request(url).content
#     soup = BeautifulSoup(page_content, "html.parser")
#     hour, minute = soup.find(id="time-section").get_text().split(":")
#     Kyiv_time = f"{(int(hour)+2)%24:02}{minute}"
#     return Kyiv_time


def get_last_updated_time(url) -> str:
    now = datetime.now(pytz.timezone("Europe/Kyiv"))
    hour, minute = [int(s) for s in now.strftime("%H %M").split()]
    minute = 0 if minute < 30 else 30
    return f"{hour:02}{minute:02}"


def use_previous_matrix():
    current_filepath = get_newest_folder(constants.website_url)

    previous_date = current_date = datetime.strptime(' '.join(current_filepath.split('/')[-2:]), '%d%m%Y %H%M')
    previous_filepath = ''
    while True:
        previous_date = current_date - timedelta(minutes=30)
        previous_filepath = '/'.join([constants.general_folder, previous_date.strftime('%d%m%Y/%H%M')])
        if os.path.exists(previous_filepath):
            break
        current_date = previous_date

    try:
        invalid_data_path = current_filepath + "/unable_to_process"
        files = os.listdir(previous_filepath)
        if not os.path.exists(invalid_data_path):
            os.mkdir(invalid_data_path)
        else:
            shutil.rmtree(invalid_data_path)
        shutil.copytree(current_filepath, invalid_data_path)
        shutil.rmtree(current_filepath)
        shutil.copytree(previous_filepath, current_filepath)
    except:
        pass

    with open(current_filepath + '/using_previous.txt', 'w') as file:
        file.write('This file is created to inform that current image on the website is invalid and/or we cannot create a valid matrix.')
