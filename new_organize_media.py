#!/usr/bin/python
# coding: utf-8
"""
usage:
    organize_media.py [-d] [-v] [-f <to_file>]

options:
    -v              Verbose
    -d              Dry run
    -f <to_file>    True or False [default: ./organize_media.log]
"""

from __future__ import unicode_literals, print_function
import sys
import os
import shutil
import subprocess
import os.path
from datetime import datetime
import re
from docopt import docopt
import logging

VERSION = "1.0.0"

# CONFIG
CONFIG = {}
CONFIG["SOURCE_DIR"] = "/volume1/photo/import"
CONFIG["SOURCE_DIR"] = "/home/fxcrespo/Dropbox/fotos (2)"
CONFIG["DESTINATION_DIRS"] = {
    "jpg": "/volume1/photo",
    "cr2": "/volume1/photo",
    "mov": "/volume1/video",
    "mp4": "/volume1/video"
}
CONFIG["ERROR_DIR"] = "/volume1/photo/output/unsorted/"
CONFIG["ENABLED_EXTENSIONS"] = ["mts", "mov", "jpg", "3gp", "mp4", "m4v",
                                "avi", "cr2"]
CONFIG["FILENAME_FORMAT"] = "%Y_%m_%d-%H_%M_%S"
CONFIG["PATH_FORMAT"] = "%Y/%m"


def should_process(the_file):
    if the_file[-3:].lower() in CONFIG["ENABLED_EXTENSIONS"]:
        return True
    else:
        return False


def get_exif(fn):  # Melhorar para pegar apenas a data e testar com Canon e iPhone
    from PIL import Image
    from PIL.ExifTags import TAGS
    ret = {}
    i = Image.open(fn)
    info = i._getexif()
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        ret[decoded] = value
    return ret


def full_path_from_date(date, extension):
    root = CONFIG["DESTINATION_DIRS"][extension]
    return os.path.join(root, date.strftime(CONFIG["PATH_FORMAT"]),
                        date.strftime(CONFIG["FILENAME_FORMAT"]) +
                        "." + extension)


def get_date(fn):
    the_date = get_exif(fn)["DateTimeOriginal"]
    return datetime.strptime(the_date, "%Y:%m:%d %H:%M:%S")


def main():
    logging.debug("Program - BEGIN")
    logging.debug("DEBUG: {0}".format(OPTIONS["-v"]))
    logging.debug("DRY_RUN: {0}".format(OPTIONS["-d"]))

    HORA = datetime.now()

    logging.info(HORA.strftime(CONFIG["FILENAME_FORMAT"]))
    logging.info(HORA.strftime(CONFIG["PATH_FORMAT"]))

    for root, dirs, files in os.walk(CONFIG["SOURCE_DIR"]):
        files[:] = filter(should_process, files)
        logging.debug(files)
        for a_file in files:
            logging.debug("Getting the date of {0}".format(a_file))
            a_file = os.path.join(root, a_file)
            the_date = get_date(a_file)
            logging.debug("The date: {0}".format(the_date))
            filename = full_path_from_date(the_date, a_file[-3:].lower())
            logging.debug("Fullpath: {0}".format(filename))

    exit(0)

if __name__ == '__main__':
    OPTIONS = docopt(__doc__, version=VERSION)
    THE_LEVEL = logging.INFO

    if OPTIONS["-v"]:
        THE_LEVEL = logging.DEBUG

    try:
        import coloredlogs
        coloredlogs.install(level=THE_LEVEL)
    except ImportError:
        logging.basicConfig(level=THE_LEVEL)

    logging.debug(OPTIONS)

    main()
