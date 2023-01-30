import image_data
import text_data


# Change here the way you get the data
def get_processed_data(folder):
    get_text_data(folder)


def get_image_data(folder):
    image_data.scrape_image(folder)
    image_data.process_image(folder)


def get_text_data(folder):
    text_data.scrape_page(folder)
    text_data.process_page(folder)
