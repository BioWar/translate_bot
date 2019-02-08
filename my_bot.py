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
import logging

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
    update.message.reply_text('Call /start for instractions.')

def echo(bot, update):
    update.message.reply_text(retrive_definition(word=update.message.text, dst='en', src='auto'))

def inlinequery(bot, update):
    query = update.inline_query.query
    results = [
        InlineQueryResultArticle(
            id=uuid4(),
            title="Translate en->ru",
            input_message_content=InputTextMessageContent(
                "{} .\n".format(retrive_definition(word=escape_markdown(query), dst='ru', src='en')),
                parse_mode=ParseMode.MARKDOWN)),]
        #InlineQueryResultArticle(
        #    id=uuid4(),
        #    title="Translate ru->en",
        #    input_message_content=InputTextMessageContent(
        #        "{} .\n".format(retrive_definition(word=escape_markdown(query), dst='en', src='ru')),
        #        parse_mode=ParseMode.MARKDOWN)),
        #InlineQueryResultArticle(
        #    id=uuid4(),
        #    title="Translate xx->ru",
        #    input_message_content=InputTextMessageContent(
        #        "{} .\n".format(retrive_definition(word=escape_markdown(query), dst='ru', src='auto')),
        #        parse_mode=ParseMode.MARKDOWN))]
    
    update.inline_query.answer(results)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    updater = Updater(os.environ.get('TOKEN'))
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
	
    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_handler(InlineQueryHandler(inlinequery))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
