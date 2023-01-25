from telegram import InlineKeyboardButton
from telegram.ext import ContextTypes
import constants


def get_choose_gpv_group_menu():
    cgm_cols = 3
    cgm_rows = constants.GROUPS // cgm_cols
    choose_group_menu = {
        "menu": [
            [
                InlineKeyboardButton(
                    i * cgm_cols + j,
                    callback_data=f"gpv_group_choice_{i * cgm_cols + j}",
                )
                for j in range(1, cgm_cols + 1)
            ]
            for i in range(cgm_rows)
        ] + [[InlineKeyboardButton("Назад", callback_data="to_main")]],
        "text": "\n".join(
            [
                "⚡️ Обери групу відключень ⚡️\n",
                "Якщо ще не знаєш своєї групи, знайди її на <a href='https://oblenergo.cv.ua/shutdowns-search/'>сайті ЧернівціОблЕнерго</a> 👈",
                ""
            ]
        ),
    }
    return choose_group_menu


def get_main_menu_not_chosen_group():
    main_menu_not_chosen_group = {
        "menu": [
            [
                InlineKeyboardButton("Обрати групу", callback_data="/choose_group"),
            ],
            [
                InlineKeyboardButton("Допомога", callback_data="/help"),
                InlineKeyboardButton("Про бота", callback_data="/info"),
            ],
            [
                InlineKeyboardButton("Повідомити про помилку", callback_data="/report"),
            ],
        ],
        "text": "🇺🇦🇺🇦🇺🇦🇺🇦🇺🇦🇺🇦🇺🇦🇺🇦🇺🇦🇺🇦🇺🇦🇺🇦🇺🇦",
    }
    return main_menu_not_chosen_group


def get_main_menu_chosen_group():
    main_menu_chosen_group = get_main_menu_not_chosen_group()
    main_menu_chosen_group["menu"][0].insert(
        0, InlineKeyboardButton("Моя група", callback_data="/my_group")
    )
    return main_menu_chosen_group


def get_main_menu(context: ContextTypes.DEFAULT_TYPE):
    return (
        get_main_menu_chosen_group()
        if "gpv_group" in context.user_data
        else get_main_menu_not_chosen_group()
    )
    