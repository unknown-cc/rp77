import logging
logging.basicConfig(level=logging.INFO)
from .time import now_str


def terminal(text:str , event:str = ""):
    now = now_str("%H:%M:%S")
    if "\n" in text:
        for line in text.split("\n"):
            if event:
                logging.info(f"[ {now} ] [ {event} ] {line}")
            else:
                logging.info(f"[ {now} ] {line}")
    else:
        if event:
            logging.info(f"[ {now} ] [ {event} ] {text}")
        else:
            logging.info(f"[ {now} ] {text}")