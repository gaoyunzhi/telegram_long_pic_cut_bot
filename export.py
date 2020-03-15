#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import Updater, MessageHandler, Filters

import export_to_telegraph
from html_telegraph_poster import TelegraphPoster
import yaml
from telegram_util import getDisplayUser, matchKey, log_on_fail

with open('CREDENTIALS') as f:
    CREDENTIALS = yaml.load(f, Loader=yaml.FullLoader)
tele = Updater(CREDENTIALS['bot_token'], use_context=True)

r = tele.bot.send_message(-1001198682178, 'start')
r.delete()
debug_group = r.chat

known_users = [420074357, 652783030]

with open('TELEGRAPH_TOKENS') as f:
	TELEGRAPH_TOKENS = {}
	for k, v in yaml.load(f, Loader=yaml.FullLoader).items():
		TELEGRAPH_TOKENS[int(k)] = v

def saveTelegraphTokens():
	with open('TELEGRAPH_TOKENS', 'w') as f:
		f.write(yaml.dump(TELEGRAPH_TOKENS, sort_keys=True, indent=2))

def msgTelegraphToken(msg):
	user_id = msg.from_user.id
	if user_id in TELEGRAPH_TOKENS:
		p = TelegraphPoster(access_token = TELEGRAPH_TOKENS[user_id])
	else:
		p = TelegraphPoster()
		r = p.create_api_token(msg.from_user.first_name, msg.from_user.username)
		TELEGRAPH_TOKENS[user_id] = r['access_token']
		saveTelegraphTokens()
	msgAuthUrl(msg, p)

def msgAuthUrl(msg, p):
	r = p.get_account_info(fields=['auth_url'])
	msg.reply_text('Use this url to login in 5 minutes: ' + r['auth_url'])

def getTelegraph(msg, url):
	user_id = msg.from_user.id
	if user_id not in TELEGRAPH_TOKENS:
		msgTelegraphToken(msg)
	export_to_telegraph.token = TELEGRAPH_TOKENS[user_id]
	return export_to_telegraph.export(url, True, force = True)

@log_on_fail(debug_group)
def exportGroup(update, context):
	msg = update.message
	new_text = msg.text
	links = []
	for item in msg.entities:
		if (item["type"] == "url"):
			url = msg.text[item["offset"]:][:item["length"]]
			markdown_url = '(%s)' % url
			if markdown_url in new_text:
				new_text = new_text.replace('(%s)' % url, '(link)')
			else:
				new_text = new_text.replace(url, '[link](%s)' % url)
			if not '://' in url:
				url = "https://" + url
			u = getTelegraph(msg, url)
			links.append('[%s](%s)' % (u, u))
	if not links:
		return
	new_text = '|'.join(links) + '|' + new_text
	msg.chat.send_message(new_text, parse_mode='Markdown')
	msg.delete()

@log_on_fail(debug_group)
def export(update, context):
	msg = update.message
	for item in msg.entities:
		if (item["type"] == "url"):
			url = msg.text[item["offset"]:][:item["length"]]
			if not '://' in url:
				url = "https://" + url
			u = getTelegraph(msg, url)
			msg.reply_text(u)
			if msg.from_user.id not in known_users:
				r = debug_group.send_message( 
					text=getDisplayUser(msg.from_user) + ': ' + u, 
					parse_mode='Markdown')

@log_on_fail(debug_group)
def command(update, context):
	if matchKey(update.message.text, ['auth', 'token']):
		return msgTelegraphToken(update.message)
	return update.message.reply_text('Feed me link, currently support wechat, bbc, stackoverflow, NYT, and maybe more')

tele.dispatcher.add_handler(MessageHandler(Filters.text & Filters.group, exportGroup))
tele.dispatcher.add_handler(MessageHandler(Filters.text & Filters.private, export))
tele.dispatcher.add_handler(MessageHandler(Filters.private & Filters.command, command))

tele.start_polling()
tele.idle()