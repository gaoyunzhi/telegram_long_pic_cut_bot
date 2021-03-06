#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import Updater, MessageHandler, Filters

import yaml
from telegram_util import log_on_fail, AlbumResult
import album_sender

with open('token') as f:
    tele = Updater(f.read().strip(), use_context=True)

debug_group = tele.bot.get_chat(-1001198682178)

@log_on_fail(debug_group)
def cut(update, context):
	msg = update.effective_message
	if msg.chat_id == debug_group.id or msg.media_group_id:
		return

	file = msg.document or (msg.photo and msg.photo[-1])
	file_path = (file and file.get_file().file_path) or msg.text or ''
	if not file_path.startswith('http'):
		return

	result = AlbumResult()
	result.cap = msg.caption_markdown or msg.text_markdown or ''
	result.imgs = [file_path]

	album_sender.send_v2(msg.chat, result, send_all=True, time_sleep=20, size_factor=1.5)

tele.dispatcher.add_handler(MessageHandler(Filters.all, cut))

tele.start_polling()
tele.idle()