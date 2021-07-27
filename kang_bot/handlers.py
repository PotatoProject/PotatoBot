import html
import io
import math

from PIL import Image
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from aiogram.utils.exceptions import InvalidStickersSet, InvalidPeerID, BotBlocked, BadRequest

from kang_bot import bot


async def kang_handler(msg: types.Message) -> None:
    user_id = msg.from_user.id
    first_name = html.escape(msg.from_user.first_name)
    bot_username = (await bot.get_me()).username

    if msg.reply_to_message:
        if msg.reply_to_message.sticker:
            file_id = msg.reply_to_message.sticker.file_id
        elif msg.reply_to_message.photo:
            file_id = msg.reply_to_message.photo[-1].file_id
        elif msg.reply_to_message.document:
            file_id = msg.reply_to_message.document.file_id
        else:
            await msg.reply("Please reply to a sticker or file.")
            return
    else:
        await msg.reply("Please reply to a sticker or file.")
        return

    if msg.get_args():
        sticker_emoji = msg.get_args()[0]
    elif msg.reply_to_message.sticker and msg.reply_to_message.sticker.emoji:
        sticker_emoji = msg.reply_to_message.sticker.emoji
        await msg.reply_to_message.sticker.download()
    else:
        sticker_emoji = "🤔"

    kang_file = await bot.download_file_by_id(file_id, io.BytesIO())

    if not msg.reply_to_message.sticker:
        try:
            im = Image.open(kang_file)
            maxsize = 512
            if (im.width and im.height) < maxsize:
                w = im.width
                h = im.height
                if im.width > im.height:
                    scale = maxsize / w
                    neww = maxsize
                    newh = h * scale
                else:
                    scale = maxsize / h
                    neww = w * scale
                    newh = maxsize
                sizenew = (math.floor(neww), math.floor(newh))
                im = im.resize(sizenew)
            else:
                im.thumbnail((maxsize, maxsize))
            sticker_file = io.BytesIO()
            im.save(sticker_file, "PNG")
            sticker_file.seek(0)
        except OSError:
            await msg.reply("Something went wrong.")
            return
    else:
        sticker_file = kang_file

    packnum = 0
    packname = "a" + str(user_id) + "_by_" + bot_username
    packname_found = False
    max_stickers = 120
    while not packname_found:
        try:
            stickerset = await bot.get_sticker_set(packname)
            if len(stickerset.stickers) >= max_stickers:
                packnum += 1
                packname = "a" + str(packnum) + "_" + str(user_id) + "_by_" + bot_username
            else:
                packname_found = True
        except InvalidStickersSet:
            packname_found = True
    try:
        try:
            await bot.add_sticker_to_set(user_id=user_id, name=packname, png_sticker=sticker_file.getvalue(),
                                         emojis=sticker_emoji)
        except InvalidStickersSet:
            if packnum > 0:
                extra_version = " " + str(packnum)
            else:
                extra_version = ""
            await bot.create_new_sticker_set(user_id=user_id, name=packname, png_sticker=sticker_file.getvalue(),
                                             emojis=sticker_emoji, title=f"{first_name}s kang pack" + extra_version)
    except (InvalidPeerID, BotBlocked):
        buttons = InlineKeyboardMarkup()
        buttons.add(InlineKeyboardButton("Start", url=f"https://t.me/{bot_username}"))
        await msg.reply("Message me in PM first.", reply_markup=buttons)
        return
    except BadRequest:
        await msg.reply("Invalid emoji.")
        return

    text = "Sticker successfully added. Get it [here](t.me/addstickers/{packname})\nEmoji is: {emoji}".format(packname=packname, emoji=sticker_emoji)
    await msg.reply(text, parse_mode=ParseMode.MARKDOWN)
