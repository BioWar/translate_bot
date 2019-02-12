#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import html.parser
import urllib.request
import urllib.parse
import os
from uuid import uuid4
from telegram.utils.helpers import escape_markdown
from telegram import InlineQueryResultArticle, ParseMode, \
    InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters
from PyPDF2 import PdfFileReader
import logging
from constants import *
import json
import difflib
from difflib import SequenceMatcher
from difflib import get_close_matches


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def unescape(text):
    if (sys.version_info[0] < 3):
        parser = HTMLParser.HTMLParser()
    else:
        parser = html.parser.HTMLParser()
    return (parser.unescape(text))


def translate(to_translate, to_language="auto", from_language="auto"):
    
    agent = {'User-Agent':
    "Mozilla/4.0 (\
    compatible;\
    MSIE 6.0;\
    Windows NT 5.1;\
    SV1;\
    .NET CLR 1.1.4322;\
    .NET CLR 2.0.50727;\
    .NET CLR 3.0.04506.30\
    )"}
    
    base_link = "http://translate.google.com/m?hl=%s&sl=%s&q=%s"
    if (sys.version_info[0] < 3):
        to_translate = urllib.quote_plus(to_translate)
        link = base_link % (to_language, from_language, to_translate)
        request = urllib2.Request(link, headers=agent)
        raw_data = urllib2.urlopen(request).read()
    else:
        to_translate = urllib.parse.quote(to_translate)
        link = base_link % (to_language, from_language, to_translate)
        request = urllib.request.Request(link, headers=agent)
        raw_data = urllib.request.urlopen(request).read()
    data = raw_data.decode("utf-8")
    expr = r'class="t0">(.*?)<'
    re_result = re.findall(expr, data)
    if (len(re_result) == 0):
        result = ""
    else:
        result = unescape(re_result[0])
    return (result)

def retrive_definition(word, dst=None, src='auto'):
	translation = translate(word, dst, src)
	return translation	

def start(bot, update):
    update.message.reply_text('Hi, I\'m the Bot which translate text inline, with my inline call @TranslatePV7103_bot!')

def help(bot, update):
    update.message.reply_text('/start - Greetings;\
	                           \n/help - Available commands;\
	                           \n/lang_code - File with available language codes (2.2 Kb);\
	                           \n/def - Defenition of english word (more than 1 answer);\
	                           Echo mode in conversation with me makes possible translation of messages xx => eng. Also sending PDF file (size < 20MB) will be translated and returned as Translation.txt. Inline mode provides such types:\
	                           \neng => ru\
	                           \nru  => eng\
	                           \nxx  => ru\
	                           \nxx  => xx (Start typing text with language code of source language and second word as destination code)\
	                           \nNew functions are comming soon.\
	                           \nThanks for using!')

def lang_code(bot, update):
    file_send = open('lang_codes.txt', 'rb')
    update.message.reply_document(file_send) 

def echo(bot, update):
    update.message.reply_text(retrive_definition(word=update.message.text, dst='en', src='auto'))
    
def echo_file(bot, update):
    user = update.message.from_user
    file = bot.get_file(update.message.document)
    file.download('user_file.pdf')
    with open('user_file.pdf', 'rb') as f:
        text = []
        translation = []
        pdf = PdfFileReader(f)
        num = pdf.getNumPages()
        for i in range(num):
            page = pdf.getPage(i)  
            some_text = page.extractText()
            some_translation = retrive_definition(some_text, dst='ru', src='en')
            translation.append(some_translation)
            text.append(some_text)
    with open('Translation.txt', 'w') as f:
        for i in range(num):
            f.write(text[i])
        f.write('\n\n ===TRANSLATION=== \n\n')
        for i in range(num):
            f.write(translation[i])
    file_send = open('Translation.txt', 'rb')
    update.message.reply_document(file_send) 
    os.remove('Translation.txt')
    os.remove('user_file.pdf')
    
def inlinequery(bot, update):
    query = update.inline_query.query
    custom_dst, custom_src = 'auto', 'auto'
    text = ' '
    try:
        ls = query.split(' ')
        custom_dst, custom_src = ls[1], ls[0]
        text = ' '.join(ls[2:])
    except:
        pass
    results = [
        InlineQueryResultArticle(
            id=uuid4(),
            title="Translate en->ru",
            input_message_content=InputTextMessageContent(
                "{} .\n".format(retrive_definition(word=escape_markdown(query), dst='ru', src='en')),
                parse_mode=ParseMode.MARKDOWN)),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Translate ru->en",
            input_message_content=InputTextMessageContent(
                "{} .\n".format(retrive_definition(word=escape_markdown(query), dst='en', src='ru')),
                parse_mode=ParseMode.MARKDOWN)),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Translate xx->ru",
            input_message_content=InputTextMessageContent(
                "{} .\n".format(retrive_definition(word=escape_markdown(query), dst='ru', src='auto')),
                parse_mode=ParseMode.MARKDOWN)),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Translate xx->xx",
            input_message_content=InputTextMessageContent(
                "{} .\n".format(retrive_definition(word=text, dst=custom_dst, src=custom_src)),
                parse_mode=ParseMode.MARKDOWN))]
    
    update.inline_query.answer(results)

def vocabulary(word):
	data = json.load(open("data.json"))
	word = word.lower()
	if word in data:
		return data[word]
	elif word.title() in data:
		return data[word.title()]
	elif word.upper() in data:
		return data[word.upper()]
	elif len(get_close_matches(word, data.keys())) > 0:
		action = input("Did you mean %s instead? [y or n]:" % get_close_matches(word, data.keys())[0])
		if (action == "y"):
			return data[get_close_matches(word, data.keys())[0]]
		elif (action == "n"):
			return ("The word doesn't exist, yet.")
		else: 
			return ("We don't understand your entry, Apologies.")
	else:
		return ("The word doesn't exist, please double check it.")

def defenition(bot, updater, args, chat_data):
    try:
        word_user = str(args[0])
        print(word_user)
        output = vocabulary(word_user)
        if type(output) == list:
            for item in output:
                updater.message.reply_text("-" + str(item))
        else:
                updater.message.reply_text("-" + str(item))
    except:
        pass

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    updater = Updater(os.environ.get('TOKEN'))
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("lang_code", lang_code))
    dp.add_handler(CommandHandler("def", defenition, 
                                  pass_args=True,
                                  pass_chat_data=True))
    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_handler(MessageHandler(Filters.document, echo_file))
    dp.add_handler(InlineQueryHandler(inlinequery))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
