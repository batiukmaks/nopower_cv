from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram import InlineKeyboardMarkup, Update
import os
import constants
from general import get_newest_folder
from image_scrapping import scrape_image
from image_processing import process_image

from bot_management import get_nopower_ranges, get_gpv_for_group
from menu import (
    get_choose_gpv_group_menu,
    get_main_menu_chosen_group,
    get_main_menu_not_chosen_group,
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with three inline buttons attached."""
    await update.message.reply_text(
        "\n".join(
            [
                "Привіт 👋",
                "Радий, що ти зацікавився цим ботом 🤙",
                "Сподіваюсь, він хоч трохи полегшить твоє життя 🫶",
            ]
        ),
    )
    await info(update, context)


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = "\n".join(
        [
            f"😡 Через дії російських окупантів пошкоджені електростанції України",
            f"🗓 Через це в кожній області запроваджують графіки погодинних відключень (ГПВ), згідно з якими вмикають/вимикають світло",
            f"🤯 В Чернівцях та області ГПВ змінюється щодня. Деколи графік може оновитись навіть посеред дня",
            f"🤩 Для того, щоб полегшити життя чернівчанам, створено цей бот. В ньому ви легко можете отримати інформацію про відключення електроенергії саме в вашій групі відключень",
            f"😋 Тепер не потрібно заходити на сайт ЧернівціОблЕнерго, шукати свою групу та запам'ятовувати, коли світло вимикатимуть",
            f"👌 Тепер все легше: ",
            f"      📍 Зайшов в чат з ботом @nopower_cv_bot",
            f"      📍 Запросив ГПВ для своєї групи (/my_group) або обрав іншу групу (/choose_group)",
            f"      📍 Бачиш графік відключень конкретно для обраної групи ✅",
            f"\n\n🤟 Бот написаний Батюком Максимом 🤟",
            f"🇺🇦 Слава Україні 🇺🇦",
        ]
    )
    await update.message.reply_text(text)
    menu = (
        get_main_menu_chosen_group()
        if "gpv_group" in context.user_data
        else get_main_menu_not_chosen_group()
    )
    await show_menu(update, menu)


async def already_chosen_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "gpv_group" not in context.user_data:
        await choose_group(update, context)
    else:
        await send_gpv_group_info(update, context.user_data["gpv_group"])


async def send_gpv_group_info(update: Update, group: int):
    nopower = get_nopower_ranges(get_gpv_for_group(group))
    text = "\n".join(
        [
            f"💡 Ви обрали групу №{group}",
            "🕑 Згідно з графіком, сьогодні у вас не буде світла в такі години:\n",
        ]
        + [f"📍 {start:02}:00 - {end:02}:00" for start, end in nopower]
    )
    await update.message.reply_photo(
        open(
            get_newest_folder(constants.website_url) + "/" + constants.local_image, "rb"
        ),
        caption=text,
    )


async def choose_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu = get_choose_gpv_group_menu()
    await show_menu(update, menu)


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    if query.data == "/choose_group":
        await choose_group(query, context)
    elif query.data == "/my_group":
        await already_chosen_group(query, context)
    elif query.data.startswith("gpv_group_choice_"):
        context.user_data["gpv_group"] = int(query.data[query.data.rindex("_") + 1 :])
        await send_gpv_group_info(query, context.user_data["gpv_group"])
    elif query.data == "/help":
        await help(query, context)
    elif query.data == "/info":
        await info(query, context)
    elif query.data == "/report":
        await report(query, context)
    await query.delete_message()

    if query.data in [
        "/my_group",
        "to_main",
        "/help",
        "/start",
    ] or query.data.startswith("gpv_group_choice_"):
        menu = (
            get_main_menu_chosen_group()
            if "gpv_group" in context.user_data
            else get_main_menu_not_chosen_group()
        )
        await show_menu(query, menu)


async def show_menu(update: Update, menu):
    await update.message.reply_text(
        text=menu["text"], reply_markup=InlineKeyboardMarkup(menu["menu"])
    )


async def invalid_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if "is_report_active" in context.user_data and context.user_data["is_report_active"]:
        await report(update, context)
    else:
        await update.message.reply_text("Для допомоги введіть /help")


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = "\n".join(
        [
            f"/start - Почати роботу бота",
            f"/choose_group - Обрати групу відключень",
            f"/my_group - Показати ГПВ для останньої вибраної групи",
            f"/info - Інформація про бота",
            f"/help - Це меню",
        ]
    )
    await update.message.reply_text(text)


async def report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if "is_report_active" not in context.user_data:
        context.user_data["is_report_active"] = False

    if not context.user_data["is_report_active"]:
        context.user_data["is_report_active"] = True
        await update.message.reply_text('Опишіть вашу проблему. \nЯкщо треба, прикріпіть фото/відео проблеми. \nВсе має бути описано в одному повідомленні.')
    else:
        context.user_data["is_report_active"] = False
        report_received = '\n'.join([
            f'chat_id: {update.message.chat_id}',
            f'Username: @{update.message.chat.username}',
            f'Name: {update.message.chat.full_name}',
        ])
        await update.get_bot().send_message(chat_id=545190147, text=report_received)
        await update.message.forward(chat_id=545190147)
        await update.message.reply_text('Дякую за допомогу! Постараюсь виправити найближчим часом =)')
    

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("my_group", already_chosen_group))
    application.add_handler(CommandHandler("choose_group", choose_group))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("info", info))
    application.add_handler(CommandHandler("report", report))
    application.add_handler(CallbackQueryHandler(menu))
    application.add_handler(
        MessageHandler(~filters.COMMAND, invalid_messages)
    )

    application.run_polling()


if __name__ == "__main__":
    main()
