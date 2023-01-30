import urllib.request
import constants
import cv2
import numpy as np
import csv


def scrape_image(folder):
    photo_url = "/".join([constants.website_url, constants.website_image_filename])
    filepath = "/".join([folder, constants.local_image])
    urllib.request.urlretrieve(photo_url, filepath)
    return filepath


def process_image(folder):
    filepath = f"{folder}/{constants.local_image}"
    original_image = cv2.imread(filepath, 0)
    detected_image = cv2.imread(filepath)

    contours = get_contours(original_image)
    table = retrieve_table(contours, detected_image)
    save_detected_image(detected_image, folder)
    save_table(table, folder)
    is_table_valid = not any("u" in row for row in table)
    if not is_table_valid:
        raise Exception("Table is invalid.")


def get_contours(image):
    found = find_contours(image)
    sorted = sorted(found, key=contours_sort_key)
    filtered = list(filter(filter_contours, sorted))
    return filtered


def find_contours(image):
    ret, thresh_value = cv2.threshold(image, 100, 255, cv2.THRESH_BINARY_INV)
    kernel = np.ones((5, 5), np.uint8)
    dilated_value = cv2.dilate(thresh_value, kernel, iterations=1)
    contours, hierarchy = cv2.findContours(
        dilated_value, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )
    return list(contours)


def contours_sort_key(contour):
    x, y, w, h = cv2.boundingRect(contour)
    return (-(y + h), -(x + w))


def filter_contours(contour):
    x, y, w, h = cv2.boundingRect(contour)
    return w <= 15 and h <= 15


def retrieve_table(contours, image):
    matrix = [["u"] * (constants.HOURS + 3) for i in range(constants.GROUPS)]
    i = 0
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cropped = image[y : y + 15, x : x + 15]
        color = (
            "g"
            if is_green(list(cropped[0][0]))
            else "r"
            if is_red(list(cropped[0][0]))
            else "u"
        )
        if color != "u":
            matrix[constants.GROUPS - (i // (constants.HOURS + 3)) - 1][
                (constants.HOURS + 3) - (i % (constants.HOURS + 3)) - 1
            ] = color
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 1)
            i += 1
        if i == constants.GROUPS * (constants.HOURS + 3):
            break
    return matrix


def is_green(rgb):
    return rgb == [157, 208, 196]


def is_red(rgb):
    return rgb == [101, 116, 222]


def save_table(table, folder):
    with open(f"{folder}/{constants.gpv_table}", "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(table)


def save_detected_image(detected_image, folder):
    cv2.imwrite(
        f"{folder}/{constants.detected_image}",
        detected_image,
    )
