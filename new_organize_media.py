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
CONFIG["SOURCE_DIR"] = "/Users/fernando/Dropbox/fotos (2)"
CONFIG["DESTINATION_DIRS"] = {
    "jpg": "/Users/fernando/Desktop/Test",
    "cr2": "/Users/fernando/Desktop/Test",
    "mov": "/Volumes/video",
    "mp4": "/Volumes/video"
}
CONFIG["ERROR_DIR"] = "/volume1/photo/output/unsorted/"
CONFIG["ENABLED_EXTENSIONS"] = ["jpg", "cr2"]  # "mts", "mov", "3gp", "mp4", "m4v", "avi"]
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


def full_path_from_date(date, extension, suffix=0):
    root = CONFIG["DESTINATION_DIRS"][extension]
    if suffix == 0:
        return os.path.join(root, date.strftime(CONFIG["PATH_FORMAT"]),
                            date.strftime(CONFIG["FILENAME_FORMAT"]) +
                            "." + extension)
    else:
        return os.path.join(root, date.strftime(CONFIG["PATH_FORMAT"]),
                            date.strftime(CONFIG["FILENAME_FORMAT"]) +
                            "({suffix}).".format(suffix=suffix) + extension)


def full_dir_from_date(date, extension):
    root = CONFIG["DESTINATION_DIRS"][extension]
    return os.path.join(root, date.strftime(CONFIG["PATH_FORMAT"]))


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
        for from_filename in files:
            try:
                logging.debug("Getting the date of {0}".format(from_filename))
                from_file = os.path.join(root, from_filename)
                the_date = get_date(from_file)
                logging.debug("The date: {0}".format(the_date))
                to_file = full_path_from_date(the_date, from_file[-3:].lower())
                logging.debug("Source: {0}".format(from_file))
                logging.debug("Fullpath: {0}".format(to_file))

                destination_dir = full_dir_from_date(the_date,
                                                     from_file[-3:].lower())
                if not os.path.exists(destination_dir):
                    if not OPTIONS["-d"]:
                        os.makedirs(destination_dir, mode=0777)
                        subprocess.check_output(["synoindex", "-A",
                                                destination_dir])
                        logging.info("Making dir {0} with permissions 0777".
                                     format(destination_dir))
                    else:
                        logging.info("DRY_RUN - Making dir {0} with permissions \
                            0777".format(destination_dir))

                suffix = 1
                while os.path.exists(to_file):
                    # Change to new formatting pattern
                    to_file = full_path_from_date(the_date,
                                                  from_file[-3:].lower(),
                                                  suffix)
                    suffix = suffix + 1
                if not OPTIONS["-d"]:
                    shutil.move(from_file, to_file)
                    subprocess.check_output(["synoindex", "-a", to_file])
                    logging.info("Moving from {0} to {1}".format(from_file,
                                                                 to_file))
                else:
                    logging.info("DRY_RUN - Moving from {0} to {1}".
                                 format(from_file, to_file))
            except Exception as e:
                logging.exception(e)
                if not os.path.exists(CONFIG["ERROR_DIR"]):
                    if not OPTIONS["-d"]:
                        os.makedirs(CONFIG["ERROR_DIR"], mode=0777)
                        logging.info("Making dir {0} with permissions 0777".
                                     format(CONFIG["ERROR_DIR"]))
                    else:
                        logging.info("DRY_RUN - Making dir {0} with permissions \
                            0777".format(CONFIG["ERROR_DIR"]))
                if not OPTIONS["-d"]:
                    shutil.move(from_file, CONFIG["ERROR_DIR"] + from_filename)
                    logging.info("Moving from {0} to {1}".
                                 format(from_file, CONFIG["ERROR_DIR"] +
                                        from_filename))
                else:
                    logging.info("DRY_RUN - Moving from {0} to {1}".
                                 format(from_file, CONFIG["ERROR_DIR"] +
                                        from_filename))
                # problems.append(from_filename)
            except:
                sys.exit("Execution stopped.")

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
