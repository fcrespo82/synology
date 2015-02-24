#!/usr/bin/env python
"""
Make a list of the last x photos based and sorted by the filename

usage:
    last-x-photos.py SOURCE DESTINATION [--photos=HOW_MANY] [-v] [-d]

options:
    SOURCE              Copy from
    DESTINATION         Copy to

    --photos=HOW_MANY   How many photos to copy [default: 1000]

    -v                  Verbose
    -d                  Dry-run - Do not execute, only show what would be done
"""

from __future__ import print_function
from __future__ import unicode_literals
import logging
import docopt
import re
import os
import itertools
from shutil import copy2
from PIL import Image

VERSION = "1.0.0"


def expandall(a_path):
    return os.path.expandvars(os.path.expanduser(ARGS["DESTINATION"]))


def fullpath(root, a_dir):
    return os.path.join(root, a_dir)


def extensions_ok(a_file):
    if a_file[-3:].lower() in ["jpg", "cr2"]:
        return True
    else:
        return False


def bigger(image_path):
    logging.debug("Checking size")
    the_image = Image.open(image_path)
    if the_image.size[0]*the_image.size[1] > 4000000:
        the_return = True
    else:
        the_return = False
    logging.debug("Checked")
    return the_return


def get_last_photos(quantity, from_path):
    already_added = 0
    found = []
    for root, dirs, files in os.walk(from_path, topdown=True):
        dirs[:] = sorted(dirs, reverse=True)
        files[:] = sorted(files, reverse=True)
        files[:] = itertools.ifilter(extensions_ok, files)

        the_match = re.match(r".*[0-9]{4}$", root)
        logging.debug(root)
        logging.debug(the_match)

        if not the_match:
            dirs[:] = sorted([x for x in dirs if re.match(r".*[0-9]{4}$", x)],
                             reverse=True)

        logging.debug(dirs)
        logging.debug(files)

        if already_added < int(quantity):
            found.extend(files[:int(quantity)-already_added])
            paths = [root]*len(found)
            found = itertools.imap(fullpath, paths, found)
            found = [x for x in found]

        logging.debug(found)
        if len(found) >= int(quantity):
            break
    return found

if __name__ == '__main__':
    ARGS = docopt.docopt(__doc__, version=VERSION)
    THE_LEVEL = logging.INFO
    if ARGS["-v"]:
        THE_LEVEL = logging.DEBUG

    try:
        import coloredlogs
        coloredlogs.install(level=THE_LEVEL, show_hostname=False, show_name=False)
    except ImportError:
        logging.basicConfig(level=THE_LEVEL)

    logging.debug(ARGS)

    logging.info("Getting last {last} photos".format(last=ARGS["--photos"]))
    LAST_PHOTOS = get_last_photos(ARGS["--photos"], ARGS["SOURCE"])
    logging.info("Got it")

    ONLY_NAMES_ON_SOURCE = [os.path.basename(photo) for photo in LAST_PHOTOS]

    if not os.path.exists(expandall(ARGS["DESTINATION"])):
        if ARGS["-d"]:
            logging.debug("Making folder {0}".format(expandall(ARGS["DESTINATION"])))
        else:
            os.makedirs(expandall(ARGS["DESTINATION"]))

    ONLY_NAMES_ON_DESTINATION = [os.path.basename(photo) for photo
                                 in os.listdir(expandall(ARGS["DESTINATION"]))
                                 if re.match(r'.*\.(jpg)$', photo)]

    logging.info('Identifying photos to add')

    PHOTOS_TO_ADD = set(ONLY_NAMES_ON_SOURCE) - set(ONLY_NAMES_ON_DESTINATION)
    PHOTOS_TO_ADD_TUPLE_LIST = [(photo,
                                os.path.join(expandall(ARGS["DESTINATION"]),
                                 os.path.basename(photo))) for photo
                                in LAST_PHOTOS
                                if os.path.basename(photo) in PHOTOS_TO_ADD]
    TOTAL_PHOTOS_TO_ADD = len(PHOTOS_TO_ADD_TUPLE_LIST)

    logging.info("DONE")

    logging.info('Identifying photos to remove')

    PHOTOS_TO_REMOVE = sorted(ONLY_NAMES_ON_DESTINATION,
                              reverse=True)[:len(PHOTOS_TO_ADD)]
    PHOTOS_TO_REMOVE_FULLPATH = [os.path.join(expandall(ARGS["DESTINATION"]),
                                 photo) for photo in PHOTOS_TO_REMOVE]
    TOTAL_PHOTOS_TO_REMOVE = len(PHOTOS_TO_REMOVE_FULLPATH)

    logging.info("DONE")

    logging.info('Removing {photos} photos'
                 .format(photos=TOTAL_PHOTOS_TO_REMOVE))
    for i, photo in enumerate(PHOTOS_TO_REMOVE_FULLPATH):
        logging.debug(TOTAL_PHOTOS_TO_REMOVE - i)
        # print(photo)
        if ARGS["-d"]:
            logging.debug(photo)
        else:
            os.remove(photo)
    logging.info('Removed {photos} photos'
                 .format(photos=TOTAL_PHOTOS_TO_REMOVE))

    logging.info('Adding {photos} photos'
                 .format(photos=TOTAL_PHOTOS_TO_ADD))
    for i, item in enumerate(PHOTOS_TO_ADD_TUPLE_LIST):
        src, dst = item
        logging.debug(TOTAL_PHOTOS_TO_ADD - i)
        # print(src, dst)
        if ARGS["-d"]:
            logging.debug(src + "->" + dst)
        else:
            copy2(src, dst)
    logging.info('Added {photos} photos'.format(photos=TOTAL_PHOTOS_TO_ADD))

    # After add and remove check if any photo needs resize
    logging.info('Identifying photos to resize')

    PHOTOS_TO_RESIZE = sorted(os.listdir(expandall(ARGS["DESTINATION"])),
                              reverse=True)[:len(PHOTOS_TO_ADD)]
    PHOTOS_TO_RESIZE = [os.path.join(expandall(ARGS["DESTINATION"]),
                        os.path.basename(photo)) for photo
                        in PHOTOS_TO_RESIZE
                        if re.match(r".*\.(jpg)$", photo) and bigger(
                            os.path.join(expandall(ARGS["DESTINATION"]),
                                         os.path.basename(photo)))]
    TOTAL_PHOTOS_TO_RESIZE = len(PHOTOS_TO_RESIZE)

    logging.info('Resizing {} photos'.format(TOTAL_PHOTOS_TO_RESIZE))
    for i, photo in enumerate(PHOTOS_TO_RESIZE):
        logging.debug(TOTAL_PHOTOS_TO_RESIZE - i)

        if ARGS["-d"]:
            logging.debug(photo)
        else:
            img = Image.open(photo)
            new_img = img.resize((img.size[0]/2, img.size[1]/2))
            new_img.save(photo, exif=img.info['exif'])

    logging.info('Resized {} photos'.format(TOTAL_PHOTOS_TO_RESIZE))
