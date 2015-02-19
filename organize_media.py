#!/usr/bin/python
# coding: utf-8
"""
usage:
        organize_media.py [-v] [-d] [-f <to_file>]

options:
        -v                          Verbose
        -d                          Disable dry run
        -f <to_file>                True or False [default: ./organize_media.log]
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


def extension(f):
        return f[-3:]


def mediaDate(f):
    # exif_code = 36867
    # cDate = Image.open(f)._getexif()[exif_code]

    logging.debug("Loading image: {0}".format(f))
    tries = [
        ["/volume1/homes/fernando/bin/exiftool/exiftool", "-s",
         "-DateTimeOriginal", f],
        ["/volume1/homes/fernando/bin/exiftool/exiftool", "-s",
         "-CreateDate", f]
    ]

    i = 0
    cDate = None
    while not cDate:
        logging.debug("Trying with {0} - {1}".format(i, tries[i]))
        cDate = subprocess.check_output(tries[i])
        i = i + 1

    logging.debug("Date before parsing: {0}".format(cDate))
    matches = re.search(r".*(\d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2}).*", cDate)
    if matches:
        cDate = matches.group(1)
    else:
        cDate = subprocess.check_output(fallback)
        matches = re.search(r".*(\d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2}).*",
                            cDate)
        cDate = matches.group(1)
    logging.debug("Date after parsing: {0}".format(cDate))
    return datetime.strptime(cDate, "%Y:%m:%d %H:%M:%S")

os.umask(0000)


def main():
    try:
        logging.debug("Program - BEGIN")
        logging.debug("DEBUG: {0}".format(OPTIONS["-v"]))
        logging.debug("DRY_RUN: {0}".format(OPTIONS["-d"]))

        month_names = [u"01 - Janeiro", u"02 - Fevereiro", u"03 - Marco",
                       u"04 - Abril", u"05 - Maio", u"06 - Junho",
                       u"07 - Julho", u"08 - Agosto", u"09 - Setembro",
                       u"10 - Outubro", u"11 - Novembro", u"12 - Dezembro"]

        destinationDir = {
            "jpg": "/volume1/photo",
            "mov": "/volume1/video",
            "mp4": "/volume1/video"
        }
        logging.info("Destination dir {0}".format(destinationDir))

        sourceDir = "/volume1/photo/import"
        destDir = "/volume1/photo/output"
        errorDir = "/volume1/photo/output/unsorted/"

        # The format for the new file names.
        fmt = "%Y_%m_%d-%H_%M_%S"
        logging.debug("Format: {0}".format(fmt))

        # The problem files.
        problems = []

        # Get all the JPEGs in the source folder.
        medias = os.listdir(sourceDir)
        medias = [x for x in medias if (x[-3:].lower() in extensions)]
        # Prepare to output as processing occurs
        lastMonth = 0
        lastYear = 0

        logging.info("Number of files to process {0}".format(len(medias)))

        # Create the destination folder if necessary
        if not os.path.exists(destDir):
            if not DRY_RUN:
                os.makedirs(destDir, mode=0777)
                subprocess.check_output(["synoindex", "-A", destDir])
                logging.info("Making dir {} with permissions 0777".format(
                    destDir))
            else:
                logging.info("DRY-RUN - Making dir {} with permissions 0777".
                             format(destDir))

        # Copy medias into year and month subfolders. Name the copies
        # according to their timestamps. If more than one media has the
        # same timestamp, add suffixes "1", "2", etc. to the names.
        dates = {}
        logging.info("Process - Start")
        for idx, media in enumerate(medias):
            logging.debug("Media: {}".format(media))
            original = sourceDir + "/" + media
            suffix = 1
            try:
                logging.debug("{0:=^80}".format(""))
                logging.debug("FILE NAME: {}".format(original))
                EXTENSION = extension(original).lower()
                logging.debug("EXTENSION: {}".format(EXTENSION))
                vDate = mediaDate(original)
                logging.debug("vDate: {}".format(vDate))
                yr = vDate.year
                mo = vDate.month
                newname = vDate.strftime(fmt)
                logging.debug("newname: {}".format(newname))
                month_name = month_names[mo-1]
                logging.debug("month_name: {}".format(month_name))
                destDir = destinationDir[EXTENSION]
                thisDestDir = destDir + ("/%04d/%s" % (yr, month_name))
                logging.debug("thisDestDir: {}".format(thisDestDir))
                if not os.path.exists(thisDestDir):
                    if not DRY_RUN:
                        os.makedirs(thisDestDir, mode=0777)
                        subprocess.check_output(["synoindex", "-A",
                                                thisDestDir])
                        logging.info("Making dir {} with permissions 0777".
                                     format(thisDestDir))
                    else:
                        logging.info("DRY_RUN - Making dir {} with permissions \
                            0777".format(thisDestDir))

                # Change to new formatting pattern
                duplicate = thisDestDir + "/%s.%s" % (newname, EXTENSION)
                logging.debug("duplicate: {}".format(duplicate))
                while os.path.exists(duplicate):
                    newname = vDate.strftime(fmt) + "({})".format(suffix)
                    # Change to new formatting pattern
                    duplicate = destDir + "/%04d/%s/%s.%s" % (yr, month_name, newname, EXTENSION)
                    suffix = suffix + 1
                if not DRY_RUN:
                    shutil.move(original, duplicate)
                    subprocess.check_output(["synoindex", "-a", duplicate])
                    logging.info("Moving from {} to {}".
                                 format(original, duplicate))
                else:
                    logging.info("DRY_RUN - Moving from {} to {}".
                                 format(original, duplicate))
            except Exception as e:
                logging.exception(e)
                if not os.path.exists(errorDir):
                    if not DRY_RUN:
                        os.makedirs(errorDir, mode=0777)
                        logging.info("Making dir {} with permissions 0777".
                                     format(errorDir))
                    else:
                        logging.info("DRY_RUN - Making dir {} with permissions \
                            0777".format(errorDir))
                if not DRY_RUN:
                    shutil.move(original, errorDir + media)
                    logging.info("Moving from {} to {}".
                                 format(original, errorDir + media))
                else:
                    logging.info("DRY_RUN - Moving from {} to {}".
                                 format(original, errorDir + media))
                problems.append(media)
            except:
                sys.exit("Execution stopped.")

        # Report the problem files, if any.
        if len(problems) > 0:
            logging.error("Problem files: {}".format("\n".join(problems)))
            logging.info("These can be found in: {}".format(errorDir))
    except Exception, e:
        logging.exception(e)
    finally:
        logging.info("Program - END")

if __name__ == "__main__":
    OPTIONS = docopt(__doc__, version=VERSION)
    THE_LEVEL = logging.INFO

    print(OPTIONS["-v"])
    if OPTIONS["-v"]:
        THE_LEVEL = logging.DEBUG

    try:
        import coloredlogs
        coloredlogs.install(level=THE_LEVEL)
    except ImportError:
        logging.basicConfig(level=THE_LEVEL)

    logging.debug(OPTIONS)

    # LOG_TO_FILE = options["-f"]

    # print("Debug {}".format(DEBUG))
    # print("Dry run {}".format(DRY_RUN))

    # print(DEBUG, DRY_RUN, LOG_TO_FILE)

    extensions = ["mts", "mov", "jpg", "3gp", "mp4", "m4v", "avi"]

    HORA = datetime.now()
    main()
