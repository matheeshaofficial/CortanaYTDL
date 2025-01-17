#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

# the logging things
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import numpy
import os
from PIL import Image
import time

# the secret configuration specific things
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

# the Strings used for this "thing"
from translation import Translation

import pyrogram
logging.getLogger("pyrogram").setLevel(logging.WARNING)

from helper_funcs.chat_base import TRChatBase


@pyrogram.Client.on_message(pyrogram.Filters.command(["generatecustomthumbnail"]))
async def generate_custom_thumbnail(bot, update):
    TRChatBase(update.from_user.id, update.text, "generatecustomthumbnail")
    if str(update.from_user.id) not in Config.SUPER7X_DLBOT_USERS:
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.NOT_AUTH_USER_TEXT,
            reply_to_message_id=update.message_id
        )
        return
    if update.reply_to_message is not None:
        reply_message = update.reply_to_message
        if reply_message.media_group_id is not None:
            download_location = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + "/" + str(reply_message.media_group_id) + "/"
            save_final_image = download_location + str(round(time.time())) + ".jpg"
            list_im = os.listdir(download_location)
            if len(list_im) == 2:
                imgs = [ Image.open(download_location + i) for i in list_im ]
                inm_aesph = sorted([(numpy.sum(i.size), i.size) for i in imgs])
                min_shape = inm_aesph[1][1]
                imgs_comb = numpy.hstack(numpy.asarray(i.resize(min_shape)) for i in imgs)
                imgs_comb = Image.fromarray(imgs_comb)
                # combine: https://stackoverflow.com/a/30228789/4723940
                imgs_comb.save(save_final_image)
                # send
                await bot.send_photo(
                    chat_id=update.chat.id,
                    photo=save_final_image,
                    caption=Translation.CUSTOM_CAPTION_UL_FILE,
                    reply_to_message_id=update.message_id
                )
            else:
                await bot.send_message(
                    chat_id=update.chat.id,
                    text=Translation.ERR_ONLY_TWO_MEDIA_IN_ALBUM,
                    reply_to_message_id=update.message_id
                )
            try:
                [os.remove(download_location + i) for i in list_im ]
                os.remove(download_location)
            except:
                pass
        else:
            await bot.send_message(
                chat_id=update.chat.id,
                text=Translation.REPLY_TO_MEDIA_ALBUM_TO_GEN_THUMB,
                reply_to_message_id=update.message_id
            )
    else:
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.REPLY_TO_MEDIA_ALBUM_TO_GEN_THUMB,
            reply_to_message_id=update.message_id
        )


@pyrogram.Client.on_message(pyrogram.Filters.photo)
async def save_photo(bot, update):
    TRChatBase(update.from_user.id, update.text, "save_photo")
    if str(update.from_user.id) in Config.BANNED_USERS:
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.ABUSIVE_USERS,
            reply_to_message_id=update.message_id,
            disable_web_page_preview=True,
            parse_mode="html"
        )
        return
    if update.media_group_id is not None:
        if str(update.from_user.id) not in Config.SUPER7X_DLBOT_USERS:
            await bot.send_message(
                chat_id=update.chat.id,
                text=Translation.NOT_AUTH_USER_TEXT,
                reply_to_message_id=update.message_id
            )
            return
        # album is sent
        download_location = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + "/" + str(update.media_group_id) + "/"
        # create download directory, if not exist
        if not os.path.isdir(download_location):
            os.makedirs(download_location)
        await bot.download_media(
            message=update,
            file_name=download_location
        )
    else:
        # received single photo
        download_location = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".jpg"
        await bot.download_media(
            message=update,
            file_name=download_location
        )
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.SAVED_CUSTOM_THUMB_NAIL,
            reply_to_message_id=update.message_id
        )


@pyrogram.Client.on_message(pyrogram.Filters.command(["deletethumbnail"]))
async def delete_thumbnail(bot, update):
    TRChatBase(update.from_user.id, update.text, "deletethumbnail")
    if str(update.from_user.id) in Config.BANNED_USERS:
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.ABUSIVE_USERS,
            reply_to_message_id=update.message_id,
            disable_web_page_preview=True,
            parse_mode="html"
        )
        return
    download_location = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id)
    try:
        os.remove(download_location + ".jpg")
        # os.remove(download_location + ".json")
    except:
        pass
    await bot.send_message(
        chat_id=update.chat.id,
        text=Translation.DEL_ETED_CUSTOM_THUMB_NAIL,
        reply_to_message_id=update.message_id
    )

@Client.on_message(filters.private & filters.command(["showthumb"]))
async def show_thumb(bot, update):
    thumb_image_path = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".jpg"
    if not os.path.exists(thumb_image_path):
        mes = await thumb(update.from_user.id)
        if mes != None:
            m = await bot.get_messages(update.chat.id, mes.msg_id)
            await m.download(file_name=thumb_image_path)
            thumb_image_path = thumb_image_path
        else:
            thumb_image_path = None    

    if thumb_image_path is not None:
        try:
            await bot.send_photo(
                chat_id=update.chat.id,
                photo=thumb_image_path
            )
        except:
            pass

    elif thumb_image_path is None:
        await bot.send_message(
            chat_id=update.chat.id,
            text="no thumbnail found",
            reply_to_message_id=update.message_id
        )
