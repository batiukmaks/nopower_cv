from telegram import InlineKeyboardMarkup, Update, Bot
from telegram.ext import (
    Updater,
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
import constants
from general import get_newest_folder
from bot_management import get_gpv_nopower_ranges, get_group_gpv
from menu import (
    get_choose_gpv_group_menu,
    get_main_menu_chosen_group,
    get_main_menu
)
import config
import os
PORT = int(os.environ.get('PORT', 5000))


# Check version
from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )


# Enable logging
import logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Enable error handling
import html, traceback, json
from telegram.constants import ParseMode

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )
    await context.bot.send_message(
        chat_id=config.DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML
    )


async def show_menu(update: Update, menu):
    await update.message.reply_text(
        text=menu["text"], reply_markup=InlineKeyboardMarkup(menu["menu"])
    )


async def send_welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "\n".join(
            [
                "Привіт 👋",
                "Радий, що ти зацікавився цим ботом 🤙",
                "Сподіваюсь, він хоч трохи полегшить твоє життя 🫶",
            ]
        ),
    )
    await send_bot_info(update, context)


async def send_bot_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
    await show_menu(update, get_main_menu(context))


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = "\n".join(
        [
            f"/start - Почати роботу бота",
            f"/choose_group - Обрати групу відключень",
            f"/my_group - Показати ГПВ для останньої вибраної групи",
            f"/info - Інформація про бота",
            f"/report - Повідомити про помилку",
            f"/help - Це меню",
        ]
    )
    await update.message.reply_text(text)


async def choose_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_menu(update, get_choose_gpv_group_menu())


async def send_my_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await send_gpv_group_info(update, context.user_data["gpv_group"])
        await show_menu(update, get_main_menu_chosen_group())
    except KeyError:
        await choose_group(update, context)


async def send_gpv_group_info(update: Update, group: int):
    nopower = get_gpv_nopower_ranges(get_group_gpv(group))
    text = "\n".join(
        [
            f"💡 Ви обрали групу №{group}",
            "🕑 Згідно з графіком, сьогодні у вас не буде світла в такі години:\n",
        ]
        + [f"📍 {start:02}:00 - {end:02}:00" for start, end in nopower]
        + [
            f"\n\n\n❗️ Можливі незначні відхилення відключень від графіку.",
            f"❗️ В разі різкого збільшення навантаження на мережі, диспетчер зобов'язаний на це повпливати. Єдиний варіант -- аварійне відключення.",
            f"❗️ Електроенергія може бути відсутня також і з інших причин, наприклад через аварійні або планові роботи в мережах.",
        ]
    )
    await update.message.reply_photo(
        open(
            get_newest_folder(constants.website_url) + "/" + constants.local_image, "rb"
        ),
        caption=text,
    )


async def report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if "is_report_active" not in context.user_data:
        context.user_data["is_report_active"] = False

    if not context.user_data["is_report_active"]:
        context.user_data["is_report_active"] = True
        text = '\n'.join([
            f'✏️ Опишіть вашу проблему.',
            f'📷 Якщо треба, прикріпіть одне фото/відео проблеми.',
            f'❗️ Все має бути описано в одному повідомленні.',
        ])
        await update.message.reply_text(text)
    else:
        context.user_data["is_report_active"] = False
        report_received = '\n'.join([
            f'chat_id: {update.message.chat_id}',
            f'Username: @{update.message.chat.username}',
            f'Name: {update.message.chat.full_name}',
        ])
        thank = '\n'.join([
            f'🙏 Дякую за допомогу!',
            f'⚙️ Постараюсь виправити найближчим часом!',
        ])
        await send_message_to_admin(context.bot, report_received)
        await update.message.forward(chat_id=config.ADMIN_CHAT_ID)
        await update.message.reply_text(thank)
        await show_menu(update, get_main_menu(context))


async def send_message_to_admin(bot: Bot, text):
    await bot.send_message(chat_id=config.ADMIN_CHAT_ID, text=text)


async def not_commands_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if "is_report_active" in context.user_data and context.user_data["is_report_active"]:
        await report(update, context)
    else:
        await update.message.reply_text("🆘 Для допомоги введіть /help")


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    if query.data == "/choose_group":
        await choose_group(query, context)
    elif query.data == "/my_group":
        await send_my_group(query, context)
    elif query.data.startswith("gpv_group_choice_"):
        context.user_data["gpv_group"] = int(query.data[query.data.rindex("_") + 1 :])
        await send_gpv_group_info(query, context.user_data["gpv_group"])
    elif query.data == "/help":
        await help(query, context)
    elif query.data == "/info":
        await send_bot_info(query, context)
    elif query.data == "/report":
        await report(query, context)
    await query.delete_message()

    if query.data in [
        "/start",
        "to_main",
        "/help",
    ] or query.data.startswith("gpv_group_choice_"):
        await show_menu(query, get_main_menu(context))


def main() -> None:
    application = Application.builder().token(config.BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", send_welcome_message))
    application.add_handler(CommandHandler("my_group", send_my_group))
    application.add_handler(CommandHandler("choose_group", choose_group))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("info", send_bot_info))
    application.add_handler(CommandHandler("report", report))
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(
        MessageHandler(~filters.COMMAND, not_commands_handler)
    )
    application.add_error_handler(error_handler)

    application.run_polling()

    application.run_webhook(
        listen="0.0.0.0",
        port=int(PORT),
        url_path=config.BOT_TOKEN,
        webhook_url=config.WEBHOOK_URL + config.BOT_TOKEN
    )

    # application.updater.start_webhook(
    #     listen="0.0.0.0",
    #     port=int(PORT),
    #     url_path=config.BOT_TOKEN,
    #     webhook_url=config.WEBHOOK_URL + config.BOT_TOKEN
    # )


if __name__ == "__main__":
    main()
