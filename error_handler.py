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
import traceback, json
from telegram import Update
from telegram.ext import ContextTypes
from io import StringIO
import config


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb_string = "".join(tb_list)

    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"update = {json.dumps(update_str, indent=2, ensure_ascii=False)}"
        "\n\n"
        f"context.chat_data = {str(context.chat_data)}\n\n"
        f"context.user_data = {str(context.user_data)}\n\n\n"
        f"{tb_string}"
    )

    file = StringIO(message)
    file.name = f"logs.txt"
    await context.bot.send_document(
        chat_id=config.DEVELOPER_CHAT_ID,
        document=file,
        caption="\n".join(
            [
                f"📍 error: {tb_list[-1].rstrip()}",
                f"📍 chat_id: {update.message.chat.id if update.callback_query is None else update.callback_query.message.chat_id}",
                f"📍 full name: {update.message.chat.full_name if update.callback_query is None else update.callback_query.message.chat.full_name}",
                f"📍 username: @{update.message.chat.username if update.callback_query is None else update.callback_query.message.chat.username}",
            ]
        ),
    )
