from datetime import datetime
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
