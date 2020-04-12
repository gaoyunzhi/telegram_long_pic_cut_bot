#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import Updater, MessageHandler, Filters

import pic_cut
import yaml
from telegram_util import log_on_fail
from telegram import InputMediaPhoto
import os
import cached_url

with open('CREDENTIALS') as f:
    CREDENTIALS = yaml.load(f, Loader=yaml.FullLoader)
tele = Updater(CREDENTIALS['bot_token'], use_context=True)

debug_group = tele.bot.get_chat(-1001198682178)

@log_on_fail(debug_group)
def cut(update, context):
	msg = update.effective_message
	if msg.chat_id == debug_group.id:
		return
		
	cap = msg.caption_markdown or msg.text_markdown or ''
	file = msg.document or (msg.photo and msg.photo[-1])
	if file:
		file = file.get_file().download()
	else:
		try:
			file = cached_url.get(msg.text, force_cache=True)
		except:
			return
	
	cuts = list(pic_cut.cut(file))
	os.system('rm %s' % file)

	if not cuts:
		return

	group = [InputMediaPhoto(open(cuts[0], 'rb'), caption=cap, parse_mode='Markdown')] + \
		[InputMediaPhoto(open(c, 'rb')) for c in cuts[1:]]
	for c in cuts:
		os.system('rm %s' % c)		
	tele.bot.send_media_group(msg.chat_id, group, timeout = 20*60)

tele.dispatcher.add_handler(MessageHandler(Filters.all, cut))

tele.start_polling()
tele.idle()