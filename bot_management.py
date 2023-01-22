import os
import csv
import constants
from general import get_newest_folder
from image_scrapping import scrape_image
from image_processing import process_image

def get_gpv_for_group(group):
    newest_folder = get_newest_folder(constants.website_url)
    path = "/".join([newest_folder, constants.gpv_table])
    if not os.path.exists(path):
        scrape_image(
            constants.website_url, newest_folder, constants.website_image_filename
        )
        process_image("/".join([newest_folder, constants.local_image]))

    with open(path, "r") as csvfile:
        reader = csv.reader(csvfile)
        return [row for i, row in enumerate(reader) if i == int(group) - 1][0]


def get_nopower_ranges(group_gpv):
    nopower = sorted(
        [
            x[1]
            for x in list(
                filter(
                    lambda x: x[0] == "r",
                    list(zip(group_gpv, range(0, constants.HOURS))),
                )
            )
        ]
    )
    ranges = [[nopower[0]]]
    for i in range(1, len(nopower)):
        if nopower[i - 1] != nopower[i] - 1:
            ranges[-1].append((nopower[i - 1] + 1) % 24)
            ranges.append([nopower[i]])
    ranges[-1].append((nopower[-1] + 1) % 24)
    return ranges