import os
from telegram import InlineKeyboardMarkup, Update, error
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    JobQueue,
)
from datetime import datetime, timedelta
import pytz
from data_management import get_nopower_ranges, get_gpv_for_group
from menu import get_choose_gpv_group_menu, get_main_menu_chosen_group, get_main_menu
import logging_management
import text
import config


PORT = int(os.environ.get("PORT", 5000))


async def send_welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text.welcome)
    message_to_pin = await update.message.reply_text(text.warning)
    await message_to_pin.pin()
    await send_bot_info(update, context)


async def send_bot_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text.bot_info)
    await show_menu(update, get_main_menu(context))


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text.help)


async def choose_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_menu(update, get_choose_gpv_group_menu())


async def send_my_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await send_gpv_group_info(update, context.user_data["gpv_group"])
        await show_menu(update, get_main_menu_chosen_group())
    except KeyError:
        await choose_group(update, context)


async def send_gpv_group_info(update: Update, group: int):
    gpv, is_latest_data, is_emergency_shutdowns = get_gpv_for_group(group)
    if gpv is None and is_emergency_shutdowns:
        await update.message.reply_photo(
            open("assets/emergency_shutdowns.jpg", "rb"),
            caption=text.emergency_shutdowns,
            parse_mode=ParseMode.HTML
        )
    elif gpv is None:
        await update.message.reply_photo(
            open("assets/issues.jpg", "rb"),
            caption=text.invalid_table_provided,
            parse_mode=ParseMode.HTML
        )
    else:
        nopower = get_nopower_ranges(gpv)
        caption = text.gpv_info(group, nopower)
        if not is_latest_data:
            caption += text.using_previous_table
        await update.message.reply_photo(
            open("assets/ligthbulb_ukraine.jpeg", "rb"),
            caption=caption,
            parse_mode=ParseMode.HTML,
        )

    if not is_emergency_shutdowns and (gpv is None or not is_latest_data):
        await show_menu(update, get_main_menu_chosen_group())
        raise Exception('Table is invalid.')


async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "is_report_active" not in context.user_data:
        context.user_data["is_report_active"] = False

    if not context.user_data["is_report_active"]:
        context.user_data["is_report_active"] = True
        await update.message.reply_text(text.report_request)
    else:
        context.user_data["is_report_active"] = False
        report_received = "\n".join(
            [
                f"chat_id: {update.message.chat_id}",
                f"Username: @{update.message.chat.username}",
                f"Name: {update.message.chat.full_name}",
            ]
        )
        await context.bot.send_message(
            chat_id=config.ADMIN_CHAT_ID, text=report_received
        )
        await update.message.forward(chat_id=config.ADMIN_CHAT_ID)
        await update.message.reply_text(text.report_submitted)
        await show_menu(update, get_main_menu(context))


async def not_commands_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.pinned_message:
        pass
    elif (
        "is_report_active" in context.user_data
        and context.user_data["is_report_active"]
    ):
        await report(update, context)
    elif "Слава Україні" in update.message.text:
        await update.message.reply_text('🇺🇦 Героям слава 🇺🇦')
    elif not update.message.from_user.is_bot:
        await update.message.reply_text("🆘 Для допомоги введіть /help")


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    try:
        await query.delete_message()
    except error.BadRequest:
        # A message can only be deleted if it was sent less than 48 hours ago.
        pass

    if query.data in [
        "/start",
        "to_main",
        "/help",
    ] or query.data.startswith("gpv_group_choice_"):
        await show_menu(query, get_main_menu(context))
    add_user_to_stats(query, context)


async def send_stats_manually(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != config.ADMIN_CHAT_ID:
        await not_commands_handler(update, context)
    else:
        await logging_management.send_stats(context)


async def show_menu(update: Update, menu):
    await update.message.reply_text(
        text=menu["text"],
        reply_markup=InlineKeyboardMarkup(menu["menu"]),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


def add_user_to_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.bot_data["logger"].add(
        (
            update.message.chat.id,
            update.message.chat.full_name,
            update.message.chat.username,
        )
    )


def main():
    application = Application.builder().token(config.BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", send_welcome_message))
    application.add_handler(CommandHandler("my_group", send_my_group))
    application.add_handler(CommandHandler("choose_group", choose_group))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("info", send_bot_info))
    application.add_handler(CommandHandler("report", report))
    application.add_handler(CommandHandler("stats", send_stats_manually))
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(MessageHandler(~filters.COMMAND, not_commands_handler))
    application.add_error_handler(logging_management.error_handler)

    job_queue = JobQueue()
    job_queue.set_application(application)
    job_queue.run_repeating(logging_management.send_stats, timedelta(hours=4))
    application.bot_data["logger"] = set()
    application.bot_data["start_time"] = datetime.now(pytz.timezone("Europe/Kyiv"))

    job_queue.scheduler.start()
    application.run_polling()

    application.run_webhook(
        listen="0.0.0.0",
        port=int(PORT),
        url_path=config.BOT_TOKEN,
        webhook_url=config.WEBHOOK_URL + config.BOT_TOKEN,
    )


if __name__ == "__main__":
    main()
