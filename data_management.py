import csv
import constants
from general import get_folder_with_latest_data


def get_gpv_for_group(group):
    newest_folder = get_folder_with_latest_data()
    filepath = "/".join([newest_folder, constants.gpv_table])

    with open(filepath, "r") as csvfile:
        reader = csv.reader(csvfile)
        return [row for i, row in enumerate(reader) if i == int(group) - 1][0]


def get_nopower_ranges(group_gpv):
    group_gpv = group_gpv[-constants.HOURS:]
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
    