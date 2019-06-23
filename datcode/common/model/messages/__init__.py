import importlib
import json
import os
import sys

from datcode.config import options


MEASSAGES = {}


def get_message(message, lang=options.default_lang):
    load_message(lang)

    return MEASSAGES[lang].get(message, None)


def load_message(lang):
    if lang not in MEASSAGES:
        module = '{}.{}'.format(__name__, lang)
        module = importlib.import_module(module)
        messages = getattr(module, 'messages')
        MEASSAGES[lang] = messages
