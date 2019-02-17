#!/usr/bin/env python
# -*- coding: utf-8 -*-

from translation import *
from dict_json import *
from constants import *
from simple_cv import *

import os
from uuid import uuid4
from telegram.utils.helpers import escape_markdown
from telegram import InlineQueryResultArticle, ParseMode, \
    InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters
from PyPDF2 import PdfFileReader
import logging


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

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
	                           \nxx  => xx (Example: en ru Hello ==> Привет)\
	                           \nNew functions are comming soon.\
	                           \nThanks for using!')

def lang_code(bot, update):
    file_send = open('lang_codes.txt', 'rb')
    update.message.reply_document(file_send) 

def echo(bot, update):
    update.message.reply_text(retrive_definition(word=update.message.text, dst='ru', src='auto'))
    
def echo_photo(bot, update):
    user = update.message.from_user
    photo_file = bot.get_file(update.message.photo[-1].file_id)
    name = 'user_photo.jpg'
    photo_file.download(name)
    text = get_image_text(name)
    update.message.reply_text(text)
    os.remove(name)
    
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
    
def elvira(bot, update):
    update.message.reply_text("Привет от Петрухи из Киева, Эльвира!")

def inlinequery(bot, update):
    query = update.inline_query.query
    
    #custom_dst, custom_src = 'auto', 'auto'
    #text = ' '
    #query = query.encode('utf-8')
    #try:
    #    ls = query.split(' ')
    #    custom_dst, custom_src = ls[1], ls[0]
    #    text = ' '.join(ls[2:])
    #except:
    #    pass
    
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
                parse_mode=ParseMode.MARKDOWN))
                           
        #InlineQueryResultArticle(
        #    id=uuid4(),
        #    title="Translate xx->xx",
        #    input_message_content=InputTextMessageContent(
        #        "{} .\n".format(retrive_definition(word=text, dst=custom_dst, src=custom_src)),
        #        parse_mode=ParseMode.MARKDOWN))
           
                ]
    
    update.inline_query.answer(results)

def defenition(bot, updater, args, chat_data):
    try:
        word_user = str(args[0])
        output = vocabulary(word_user)
        if type(output) == list:
            for item in output:
                updater.message.reply_text("-" + str(item))
        elif output != False:
            updater.message.reply_text("-" + str(item))
        else:
            updater.message.reply_text('The word doesn\'t exist, please double check it.')                
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
    dp.add_handler(CommandHandler("elvira", elvira))
    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_handler(MessageHandler(Filters.document, echo_file))
    dp.add_handler(MessageHandler(Filters.photo, echo_photo))
    dp.add_handler(InlineQueryHandler(inlinequery))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
