from typing import Optional
from flask.wrappers import Request


class Message:
    def __init__(self, request: Request) -> None:
        request_json = request.json

        self.sender_type: str = request_json['sender_type']
        self.group_id: str = request_json['group_id']
        self.name: str = request_json['name']
        self.text: str = request_json['text']
        self.picture_url: Optional[str] = None

        attachments = request_json['attachments']
        if attachments:
            for attachment in attachments:
                if attachment['type'] == 'image':
                    self.picture_url = attachment['url']
                    break

    def from_user(self) -> bool:
        return self.sender_type == "user"

    def check_prefix(self, prefix) -> bool:
        matches = self.text.startswith(prefix)

        if matches:
            self.text = self.text[len(prefix):]

        return matches

    def read_next(self, check_quote=True) -> str:
        self.text = self.text.lstrip()

        if len(self.text) == 0:  # No next word
            return ""

        if check_quote and self.text[0] == '"':
            i = self.text.find('"', 1)

            if i != -1:
                phrase = self.text[1:i]
                self.text = self.text[i + 1:].lstrip()
                return phrase

        i = self.text.find(' ')

        if i == -1:
            word = self.text
            self.text = ""
            return word

        word = self.text[:i]
        self.text = self.text[i + 1:].lstrip()
        return word
