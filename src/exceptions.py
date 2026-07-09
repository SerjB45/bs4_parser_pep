class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег."""
    pass


class ConnectionFailed(Exception):
    """Не получили ответ от сайта"""
    pass
