class CommandException(Exception):
    pass


class IllegalQuotationMark(CommandException):
    pass


class GuideException(Exception):
    pass


class InvalidGuideTitle(GuideException):
    pass
