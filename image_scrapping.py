import urllib.request
import os
from general import get_newest_folder
import constants


def scrape_image(url, path, filename):
    date_folder_path = path[: path.rindex("/")]
    if not os.path.exists(date_folder_path):
        os.mkdir(date_folder_path)
    if not os.path.exists(path):
        os.mkdir(path)
        scrape_gpv_image(url + filename, "/".join([path, constants.local_image]))


def scrape_gpv_image(url, filepath):
    urllib.request.urlretrieve(url, filepath)


if __name__ == "__main__":
    scrape_image(
        constants.website_url,
        get_newest_folder(constants.website_url),
        constants.website_image_filename,
    )
