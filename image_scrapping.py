import urllib.request
import os
from general import get_newest_folder
import constants
import csv
import re


def scrape_image(url, path, filename):
    date_folder_path = path[: path.rindex("/")]
    if not os.path.exists(date_folder_path):
        os.mkdir(date_folder_path)
    if not os.path.exists(path):
        os.mkdir(path)
    # scrape_gpv_image(url + filename, "/".join([path, constants.local_image]))
    html_filepath = scrape_html_page(f"{date_folder_path}/{constants.local_html_file}")
    matrix = get_gpv_matrix(html_filepath)
    save_gpv_matrix(f"{path}/{constants.gpv_table}", matrix)


def scrape_gpv_image(url, filepath):
    urllib.request.urlretrieve(url, filepath)


def scrape_html_page(dst):
    filepath, resp = urllib.request.urlretrieve(constants.website_url, dst)
    return filepath


def get_gpv_matrix(filepath):
    matrix = [['u']*constants.HOURS for _ in range(constants.GROUPS)]
    i = 0
    with open(filepath, 'r') as file:
        for line in file.read().replace(' ', '').split('\n'):
            occurences = re.findall('>[вз]<', line)
            for occurence in occurences:
                matrix[i//constants.HOURS][i%constants.HOURS] = 'g' if occurence[1] == 'з' else 'r' if occurence[1] == 'в' else 'u'
                i += 1
    return matrix


def save_gpv_matrix(path_to_save, matrix):
    with open(path_to_save, 'w') as file:
        writer = csv.writer(file)
        writer.writerows(matrix)


if __name__ == "__main__":
    scrape_image(
        constants.website_url,
        get_newest_folder(constants.website_url),
        constants.website_image_filename,
    )
