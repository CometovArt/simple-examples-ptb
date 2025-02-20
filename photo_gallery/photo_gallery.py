# This program is dedicated to the public domain under the CC0 license.

"""
A simple example of implementing a photo gallery using messages with inline keyboards.

Usage:
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
from dotenv import dotenv_values

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Update
from telegram.ext import Application, ContextTypes, CommandHandler, CallbackQueryHandler

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "This is a simple implementation of a photo gallery.\n\n"
        "This menu is sent with a photo because you can't make the "
        "«Back to menu» button from a media message into a text message."
    )
    
    keyboard = [
        [InlineKeyboardButton(text="Photo Gallery", callback_data="photo_gallery:0")],
        [InlineKeyboardButton(text="Photo Carousel", callback_data="photo_carousel:0")],
        [InlineKeyboardButton(text="Carousel with Cache", callback_data="carousel_with_cache:0")],
    ]
    
    # This menu can be opened either via a command or via a button, 
    # so both cases need to be handled:
    
    if not update.callback_query:
        await update.effective_message.reply_photo(
            photo=open("media/menu.jpg", "rb"), caption=text, 
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    else:
        await update.effective_message.edit_media(
            media=InputMediaPhoto(media=open("media/menu.jpg", "rb"), caption=text),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


async def photo_gallery(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "This is a simple Photo Gallery.\n\n"
        "Has pagination limited to a list of media."
    )
    
    # carousel_page is the position of the media in the list that 
    # needs to be displayed. We get it from callback_query.data
    carousel_page = int(update.callback_query.data.split(':')[1])
    
    media_path = "media/"
    photo_list = [
        "media_1.jpg", 
        "media_2.jpg", 
        "media_3.jpg", 
        "media_4.jpg", 
        "media_5.jpg"
    ]
    
    photo = media_path + photo_list[carousel_page]
    
    keyboard = list()
    button_prev = InlineKeyboardButton(text="◀️", callback_data=f"photo_gallery:{carousel_page-1}")
    button_next = InlineKeyboardButton(text="▶️", callback_data=f"photo_gallery:{carousel_page+1}")
    
    # To limit media pagination we display only specific buttons:
    if carousel_page >= len(photo_list) - 1:
        keyboard.append([button_prev])
    elif carousel_page <= 0:
        keyboard.append([button_next])
    else:
        keyboard.append([button_prev, button_next])
    
    keyboard.append([InlineKeyboardButton(text="Back to menu", callback_data="start_menu")])
 
    await update.effective_message.edit_media(
        media=InputMediaPhoto(media=open(photo, "rb"), caption=text),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    
    
async def photo_carousel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "This is a simple Photo Carousel.\n\n"
        "It has unlimited pagination, the photos in it are repeated in a circle."
    )
    
    # carousel_page is the position of the media in the list that 
    # needs to be displayed. We get it from callback_query.data
    carousel_page = int(update.callback_query.data.split(':')[1])
    
    media_path = "media/"
    photo_list = [
        "media_1.jpg", 
        "media_2.jpg", 
        "media_3.jpg", 
        "media_4.jpg", 
        "media_5.jpg"
    ]
    
    # Infinite pagination is implemented by simply resetting 
    # the value if it is greater/less than the allowed values.
    if carousel_page > len(photo_list) - 1:
        carousel_page = 0
    elif carousel_page < 0:
        carousel_page = len(photo_list) - 1
    
    photo = media_path + photo_list[carousel_page]
 
    keyboard = [
        [
            InlineKeyboardButton(text="◀️", callback_data=f"photo_carousel:{carousel_page-1}"),
            InlineKeyboardButton(text="▶️", callback_data=f"photo_carousel:{carousel_page+1}"),
        ],
        [InlineKeyboardButton(text="Back to menu", callback_data="start_menu")],
    ]
 
    await update.effective_message.edit_media(
        media=InputMediaPhoto(media=open(photo, "rb"), caption=text),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    
    
async def carousel_with_cache(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.bot_data.setdefault("photo_cache", dict())
    
    text = (
        "This is a simple Photo Carousel with Cache.\n\n"
        "You can save the file_id of sent media so that when editing a message, "
        "the files are not uploaded to Telegram servers each time.\n\n"
    )
    
    carousel_page = int(update.callback_query.data.split(':')[1])
    
    media_path = "media/"
    photo_list = [
        "media_1.jpg", 
        "media_2.jpg", 
        "media_3.jpg", 
        "media_4.jpg", 
        "media_5.jpg"
    ]
    
    if carousel_page > len(photo_list) - 1:
        carousel_page = 0
    elif carousel_page < 0:
        carousel_page = len(photo_list) - 1
    
    photo = media_path + photo_list[carousel_page]
 
    keyboard = [
        [
            InlineKeyboardButton(text="◀️", callback_data=f"carousel_with_cache:{carousel_page-1}"),
            InlineKeyboardButton(text="▶️", callback_data=f"carousel_with_cache:{carousel_page+1}"),
        ],
        [InlineKeyboardButton(text="Back to menu", callback_data="start_menu")],
    ]
    
    # This is a very primitive cache implementation that compares whether 
    # bot_data has a file_id for a file with the selected name or not. 
    # If necessary, make a more complex media check, 
    # and also store the file_id in the database.
 
    if file_id := context.bot_data["photo_cache"].get(photo_list[carousel_page]):
        text += "Status:\n🟢 This media has already been cached and served using file_id."
        await update.effective_message.edit_media(
            media=InputMediaPhoto(media=file_id, caption=text),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    else:
        text += "Status:\n🟠 This media has not yet been cached and sent as a file."
        message = await update.effective_message.edit_media(
            media=InputMediaPhoto(media=open(photo, "rb"), caption=text),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        context.bot_data["photo_cache"][photo_list[carousel_page]] = message.photo[-1].file_id


def main() -> None:
    """Start the bot."""
    # Get a bot token from a tokens.env file
    token = dotenv_values("token.env").get("BOT_TOKEN") # or just place here your bot's token
    
    # Create the Application and pass it your bot's token
    application = Application.builder().token(token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(start, "^start_menu$"))
    
    application.add_handler(CallbackQueryHandler(photo_gallery, "^photo_gallery:"))
    application.add_handler(CallbackQueryHandler(photo_carousel, "^photo_carousel:"))
    application.add_handler(CallbackQueryHandler(carousel_with_cache, "^carousel_with_cache:"))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()