# bot.py

import logging
import time
import traceback
from typing import Callable, Dict
from urllib import parse

from flask import Flask, request

from db import *
from helper import *
from message import Message

# Flask App
app = Flask(__name__)

logging.basicConfig(filename='guide.log', level=logging.INFO)


def command_guide(message: Message):
    title = message.text
    found, guide = get_guide(message.group_id, title)

    if found:
        content, picture_url = guide
        if picture_url:
            send_message(message.group_id, content, picture_url=picture_url)
        else:
            send_message(message.group_id, content)

    else:
        msg = f"Could not find a guide titled: {title}"

        if len(guide) > 0:
            msg += "\nPerhaps you meant:\n\t" + \
                "\n\t".join([g[0] for g in guide])

            send_message(message.group_id, msg)


def command_create(message: Message):
    group_id = message.group_id
    title = message.read_next()

    found, ignore = get_guide(group_id, title)
    if found:
        send_message(group_id, "The guide already exists")
    else:
        if "?latex " in message.text:
            content, expr = message.text.split("?latex ", 1)
            try:
                picture_url = save_image(compile_latex(expr))
                create_guide(group_id, title, content, picture_url)
                send_message(group_id, picture_url=picture_url)

            except:
                send_message(group_id,
                             "Oops an error occured while parsing :(\n"
                             "If you want to parse a formula, then surround the "
                             "expression with $")

        else:
            create_guide(group_id, title, message.text, message.picture_url)


def command_delete(message: Message):
    delete_guide(message.group_id, message.text)


def command_edit(message: Message):
    group_id = message.group_id
    title = message.read_next()

    found, ignore = get_guide(group_id, title)
    if not found:
        send_message(group_id, "The guide does not exist")
    else:
        if "?latex " in message.text:
            content, expr = message.text.split("?latex ", 1)
            try:
                picture_url = save_image(compile_latex(expr))
                edit_guide(group_id, title, content, picture_url)
                send_message(group_id, picture_url=picture_url)

            except:
                send_message(group_id,
                             "Oops an error occured while parsing :(\n"
                             "If you want to parse a formula, then surround the "
                             "expression with $")

        else:
            edit_guide(group_id, title, message.text, message.picture_url)


def command_search(message: Message):
    guides = search_guide(message.group_id, message.text)

    if len(guides) > 0:
        msg = "Found the following guides:\n\t" + \
            "\n\t".join([g[0] for g in guides])
    else:
        msg = "Could not find any guides :("

    send_message(message.group_id, msg)


def command_latex(message: Message):
    try:
        latex = compile_latex(message.text)
        image_url = save_image(latex)
        send_message(message.group_id,
                     picture_url=image_url)
    except:
        print(traceback.format_exc(), flush=True)
        send_message(message.group_id,
                     "Oops an error occured while parsing :(\n"
                     "If you want to parse a formula, then surround the "
                     "expression with $")


def command_google(message: Message):
    text = message.text
    query = "lmgtfy.app/?q=" + parse.quote_plus(text)
    send_message(message.group_id, query)


def command_help(message: Message):
    help_msg = """𝗚𝘂𝗶𝗱𝗲 bot created by JP
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
?𝗴𝘂𝗶𝗱𝗲 <name>
?𝗰𝗿𝗲𝗮𝘁𝗲 <name | "phrase"> <content> 
?𝗲𝗱𝗶𝘁 <name | "phrase"> <content>
?𝗱𝗲𝗹𝗲𝘁𝗲 <name>
?𝘀𝗲𝗮𝗿𝗰𝗵 <name>
?𝗹𝗮𝘁𝗲𝘅 <latex formula>
▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"""
    send_message(message.group_id, help_msg)


commands: Dict[str, Callable] = {
    'guide': command_guide,
    'create': command_create,
    'delete': command_delete,
    'edit': command_edit,
    'search': command_search,
    'latex': command_latex,
    'google': command_google,
    'help': command_help,
}


@app.route("/", methods=['POST'])
def webhook():
    try:
        if request is None:
            return "OK", 200

        time.sleep(0.5)
        message = Message(request)

        if message.from_user():
            if message.check_prefix(prefix):
                command_name = message.read_next(check_quote=False)

                if command_name in commands:
                    commands[command_name](message)

        return "OK", 200
    except:
        print(sys.exc_info())
        return "Error", 500
