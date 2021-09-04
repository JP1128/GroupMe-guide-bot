from io import BytesIO
from typing import List, Optional

import requests
from PIL import Image
from requests.models import Response
from sympy import preview

from config import *


def save_image(image_data: BytesIO) -> str:
    """Saves the image represented by the provided image_data
    to the GroupME image service, and return the url for the
    image 

    Args:
        image_data (BytesIO): Byte data of an image

    Returns:
        str: url for the image
    """
    
    res = requests.post('https://image.groupme.com/pictures',
                        data=image_data.getvalue(),
                        headers={'Content-Type': "image/png"},
                        params={'access_token': access_token})

    return res.json()['payload']['picture_url']


def get_bot_id(group_id: str) -> int:
    """Retrives the bot_id in the form of int via
    the specified group_id that the bot is a member of.
    If no such bot exists, then -1 is returned.

    Args:
        group_id (int): the id of the group that the
                        message is sent in

    Returns:
        int: bot_id
    """

    res = requests.get(bot_url,
                       params={'token': access_token})

    for bot in res.json()['response']:
        if bot['group_id'] == group_id:
            return bot['bot_id']

    return -1


def send_message(group_id: str,
                 text: Optional[str] = None,
                 *, picture_url: Optional[str] = None) -> Optional[Response]:
    """Sends message to the group with the speicifed group_id
    with the text and picture_url as provided

    Args:
        group_id (str): group_id for the group where the message should be sent
        text (Optional[str], optional): text that the message contains. Defaults to None.
        picture_url (Optional[str], optional): url of the picture (GroupMe Image Service). Defaults to None.

    Returns:
        Response: response object
    """
    
    bot_id = get_bot_id(group_id)

    # A bot could not be found inside group_id
    if bot_id == -1:
        return

    if text is None or len(text) == 0:
        text = empty_character

    params = {'bot_id': bot_id, 'text': text}
    if picture_url:
        params['picture_url'] = picture_url
    
    response = requests.post(post_message, json=params)
    return response


def compile_latex(expr: str,) -> BytesIO:
    """[summary]

    Args:
        expr (str): latex formula to parse

    Returns:
        BytesIO: binary data representing the compiled latex image
    """
    latex_img = BytesIO()

    if expr.startswith('$') and expr.endswith('$'):
        expr = "$\\begin{{aligned}}{}\\end{{aligned}}$".format(expr[1:-1])

    preview(expr, output='png', viewer='BytesIO',
            outputbuffer=latex_img,
            dvioptions=['-D', '1500'])

    return pad_image(latex_img)


def pad_image(image_data: BytesIO) -> BytesIO:
    old_img = Image.open(image_data)
    old_w, old_h = old_img.size

    new_w = old_w if old_w > min_width else min_width
    new_h = old_h

    # Pad the image
    new_w += padding
    new_h += padding

    # Keep the image in specified ratio
    if new_w / new_h > ratio:
        new_h += round(new_w / ratio - new_h)

    elif new_w / new_h < ratio:
        new_w += round(new_h * ratio - new_w)

    new_img = BytesIO()
    bg = Image.new(old_img.mode, (new_w, new_h), 'white')
    bg.paste(old_img, ((new_w - old_w) // 2, (new_h - old_h) // 2))
    bg.save(new_img, format='PNG')
    return new_img
