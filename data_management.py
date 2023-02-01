import csv
import constants
from general import get_folder_with_latest_valid_data


def get_gpv_for_group(group):
    last_valid_folder, is_latest = get_folder_with_latest_valid_data()
    filepath = "/".join([last_valid_folder, constants.gpv_table])

    gpv = None
    try:
        with open(filepath, "r") as csvfile:
            reader = csv.reader(csvfile)
            gpv = [row for i, row in enumerate(reader) if i == int(group) - 1][0]
    except FileNotFoundError:
        gpv = None
    return (gpv, is_latest)


def get_nopower_ranges(group_gpv):
    group_gpv = group_gpv[-constants.HOURS :]
    status_hours = list(zip(group_gpv, range(0, constants.HOURS)))
    nopower = sorted(
        [
            x
            for x in list(
                filter(
                    lambda x: x[0] in ["r", "m"],
                    status_hours,
                )
            )
        ],
        key=lambda x: x[1],
    )
    ranges = [[nopower[0][0], nopower[0][1]]]
    for i in range(1, len(nopower)):
        if nopower[i - 1][1] != nopower[i][1] - 1 or nopower[i - 1][0] != nopower[i][0]:
            ranges[-1].append((nopower[i - 1][1] + 1) % 24)
            ranges.append([nopower[i][0], nopower[i][1]])
    ranges[-1].append((nopower[-1][1] + 1) % 24)
    return ranges
