# -*- coding: utf-8 -*-
"""Modulo principal do BOT."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
from settings import API_KEY, APP_NAME, PORT, DEBUG
from core.pugbot import PugBot
from core.help import Help as helper

import os

REGRAS_PATH = os.path.join(os.getcwd(), "REGRAS.md")

def start(bot, update, **kwargs):
    """Mostra um mensagem de apresentação do BOT."""
    message = 'Olá! Sou o Bot do Python User Group - MA (PUGMA)!\n'

    f = open(REGRAS_PATH, 'r')

    message += f.read()

    bot.send_message(
        chat_id=update.message.chat_id,
        text=message,
        parse_mode='Markdown'
    )

@helper.command_doc
def regras(bot, update, **kwargs):
    """/regras - Apresenta as regras do grupo."""
    bot_chat = "https://t.me/{}?start=rules".format(bot.username)
    try:
        rules_keyboard = [[InlineKeyboardButton(
            text="Leia as regras:",
            url=bot_chat
        )]]

        subtext = "abaixo as regras:"

        if 'username' not in kwargs:
            username = ""
            subtext = subtext.capitalize()
        else:
            username = kwargs["username"]
            subtext = "@{}, {}".format(username, subtext)

        if 'user_id' not in kwargs:
            user_id = None
        else:
            user_id = kwargs["user_id"]

        bot.send_message(
            chat_id=update.message.chat_id,
            text=subtext,
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(rules_keyboard)
        )

    except Exception as e:
        print(e)


@helper.command_doc
def help(bot, update):
    """/help - Lista os comandos do bot"""
    try:
        lista = helper().lista_comando
        message = ""
        for i in lista:
            message += i + "\n"
        bot.send_message(
            chat_id=update.message.chat_id,
            text=message,
            parse_mode='Markdown')
    except Exception as e:
        print(e)

def generate_hello_msg(username, is_bot):
    msg = ""
    if is_bot:
        msg = (
            '00101100 00100000 01101000 01100101 01101100 '
            '01101100 01101111 00100000 01101101 01111001 '
            '00100000 01100110 01100101 01101100 01101100 '
            '01101111 01110111 00100000 01101101 01100001 '
            '01100011 01101000 01101001 01101110 01100101 '
            '00100000 01100110 01110010 01101001 01100101 '
            '01101110 01100100 00100001'
        )
    else:
        msg = (
            'Este é o Python User Group - MA (PUG-MA). '
            'Um grupo para a galera de Python do Maranhão (ou não) que '
            'queira interagir e ficar por dentro do que está rolando na '
            'cena de Python aqui.'
        )

    if username is not None:
        msg = 'Olá ' + f'@{username}! ' + msg

    return msg


def hello_new_users(bot, update):
    """Recebe um usário novo no chat do grupo."""
    new_chat_members = update.message.new_chat_members

    for member in new_chat_members:
        user_id = member.id

        if user_id != bot.id:
            username, user_id, is_bot = member.username, member.id, member.is_bot

            message = generate_hello_msg(username, is_bot)

            bot.send_message(
                chat_id=update.message.chat_id,
                text=message
            )

            regras(bot, update, username=username, user_id=user_id)


@helper.command_doc
def last_meetup(bot, update):
    """/lastMeetup - Apresenta o último meetup do PUG."""
    lastMeetup = PugBot().last_event()
    bot.send_photo(
        chat_id=update.message.chat_id,
        caption=lastMeetup['text'],
        photo=lastMeetup['photo']
    )


@helper.command_doc
def meetup(bot, update, args):
    """/meetup # - Apresenta um meetup específico do PUG
                   baseado no seu número de apresentação."""
    index = int(''.join(args))
    meetup = PugBot().event(index)
    bot.send_photo(
        chat_id=update.message.chat_id,
        caption=meetup['text'],
        photo=meetup['photo']
    )


def main():
    """Rotina principal de iniciação do BOT."""
    updater = Updater(token=API_KEY)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start, pass_args=True)

    new_user_handler = MessageHandler(
        Filters.status_update.new_chat_members,
        hello_new_users
    )

    last_meetup_handler = CommandHandler('lastMeetup', last_meetup)
    meetup_handler = CommandHandler('meetup', meetup, pass_args=True)
    help_handler = CommandHandler('help', help)
    regras_handler = CommandHandler('regras', regras, pass_args=True)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(new_user_handler)
    dispatcher.add_handler(meetup_handler)
    dispatcher.add_handler(last_meetup_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(regras_handler)

    if DEBUG:
        updater.start_polling()
    else:
        updater.start_webhook(
            listen='0.0.0.0',
            port=PORT,
            url_path=API_KEY
        )
        updater.bot.set_webhook(f'https://{APP_NAME}.herokuapp.com/{API_KEY}')

    updater.idle()


if __name__ == '__main__':
    main()
