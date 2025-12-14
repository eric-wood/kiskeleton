import logging


class Colors:
    yellow_bg = "\u001b[43;1m"
    red_bg = "\u001b[41;1m"
    white_fg = "\u001b[37m"
    black_fg = "\u001b[30m"
    reset = "\u001b[0m"


formats = {
    logging.ERROR: "".join(
        [Colors.red_bg, Colors.white_fg, "Error ", Colors.reset, " {message}"]
    ),
    logging.WARNING: "".join(
        [Colors.yellow_bg, Colors.black_fg, "Warning ", Colors.reset, " {message}"]
    ),
}


class Formatter(logging.Formatter):
    def format(self, record):
        fmt = formats.get(record.levelno)
        formatter = logging.Formatter(fmt, style="{")
        return formatter.format(record)


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
stdout_handler = logging.StreamHandler()
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(Formatter())
logger.addHandler(stdout_handler)
