import urllib.request
import re
import csv
import constants


def scrape_page(folder):
    filepath = "/".join([folder, constants.local_html_file])
    urllib.request.urlretrieve(constants.website_url, filepath)


def process_page(folder):
    table = retrieve_table(f"{folder}/{constants.local_html_file}")
    save_table(table, folder)


def retrieve_table(filepath):
    matrix = [["u"] * constants.HOURS for _ in range(constants.GROUPS)]
    i = 0
    with open(filepath, "r") as file:
        for line in file.read().replace(" ", "").split("\n"):
            occurences = re.findall(">[вз]<", line)
            for occurence in occurences:
                matrix[i // constants.HOURS][i % constants.HOURS] = (
                    "g" if occurence[1] == "з" else "r" if occurence[1] == "в" else "u"
                )
                i += 1
    return matrix


def save_table(table, folder):
    with open(f"{folder}/{constants.gpv_table}", "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(table)
