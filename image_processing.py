import cv2
import numpy as np
import csv
from general import get_newest_folder, use_previous_matrix
import constants


def process_image(filepath):
    original_image = cv2.imread(filepath, 0)
    detected_image = cv2.imread(filepath)
    
    contours = get_contours(original_image)
    matrix = get_gpv_matrix(contours, detected_image)
    is_matrix_valid = not any('u' in row for row in matrix)
    if not is_matrix_valid:
        use_previous_matrix()
    else:
        save_gpv_matrix(matrix, filepath)
        save_detected_image(detected_image, filepath)


def get_contours(image):
    ret, thresh_value = cv2.threshold(image, 100, 255, cv2.THRESH_BINARY_INV)
    kernel = np.ones((3, 3), np.uint8)
    dilated_value = cv2.dilate(thresh_value, kernel, iterations=1)
    contours, hierarchy = cv2.findContours(
        dilated_value, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )
    return contours


def get_gpv_matrix(contours, image):
    matrix = [["u"] * constants.HOURS for i in range(constants.GROUPS)]
    i = 0
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cropped = image[y : y + h, x : x + w]
        color = (
            "g"
            if is_green(list(cropped[0][0]))
            else "r"
            if is_red(list(cropped[0][0]))
            else "u"
        )
        if color != 'u':
            matrix[constants.GROUPS - (i // constants.HOURS) - 1][
                constants.HOURS - (i % constants.HOURS) - 1
            ] = color
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 1)
            i += 1
        if i == constants.GROUPS * constants.HOURS:
            break
    return matrix


def is_green(rgb):
    return rgb == [157, 208, 196]


def is_red(rgb):
    return rgb == [101, 116, 222]


def save_gpv_matrix(matrix, filepath):
    with open(filepath[: filepath.rindex("/") + 1] + "table.csv", "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(matrix)


def save_detected_image(detected_image, filepath):
    cv2.imwrite(
        filepath[: filepath.rindex("/") + 1] + "detected_table_image.jpg",
        detected_image,
    )


if __name__ == "__main__":
    filepath = "/".join(
        [get_newest_folder(constants.website_url), constants.local_image]
    )
    process_image(filepath)
