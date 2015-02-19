#!/usr/bin/python
#coding: utf-8

from __future__ import unicode_literals
import sys
import os, shutil
import subprocess
import os.path
from datetime import datetime
import re
from docopt import docopt

options = docopt("""
usage:
    organize_media.py [-v <verbose>] [-d <dryrun>] [-f <to_file>]

options:
    -v <verbose>        True or False [default: False]
    -d <dryrun>         True or False [default: True]
    -f <to_file>        True or False [default: True]
""")
#import Image
print(options)

DEBUG=options['-v'].lower() == 'true'
DRY_RUN=options['-d'].lower() == 'true'

LOG_TO_FILE=options['-f'].lower() == 'true'

#print('Debug {}'.format(DEBUG))
#print('Dry run {}'.format(DRY_RUN))

#print(DEBUG, DRY_RUN, LOG_TO_FILE)

extensions=['mts', 'mov', 'jpg', '3gp', 'mp4', 'm4v', 'avi']
######################## Functions #########################

def extension(f):
  return f[-3:]

#exif_code = 36867

def mediaDate(f):
  #ext=extension(f).lower()
  _log('Loading image', f)
  #cDate = Image.open(f)._getexif()[exif_code]
  tries=[
    ['/volume1/homes/fernando/bin/exiftool/exiftool', '-s', '-DateTimeOriginal', f],
    ['/volume1/homes/fernando/bin/exiftool/exiftool', '-s', '-CreateDate', f]
  ]
  # d={
  #   "mts": ['/volume1/homes/fernando/bin/exiftool/exiftool', '-s', '-DateTimeOriginal', f],
  #   "mov": ['/volume1/homes/fernando/bin/exiftool/exiftool', '-s', '-CreateDate', f],
  #   "jpg": ['/volume1/homes/fernando/bin/exiftool/exiftool', '-s', '-CreateDate', f],
  #   "3gp": ['/volume1/homes/fernando/bin/exiftool/exiftool', '-s', '-CreateDate', f],
  #   "mp4": ['/volume1/homes/fernando/bin/exiftool/exiftool', '-s', '-CreateDate', f],
  #   "m4v": ['/volume1/homes/fernando/bin/exiftool/exiftool', '-s', '-CreateDate', f],
  #   "avi": ['/volume1/homes/fernando/bin/exiftool/exiftool', '-s', '-FileModifyDate', f] #Camera a prova d'água Sony DSC-TF1
  # }
  # fallback = ['/volume1/homes/fernando/bin/exiftool/exiftool', '-s', '-ModifyDate', f]
  i=0
  cDate = None
  while not cDate:
    _log('Trying with {}'.format(i), tries[i])
    cDate = subprocess.check_output(tries[i])
    i = i + 1

  _log('Date before parsing', cDate)
  matches = re.search(r'.*(\d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2}).*', cDate)
  if matches:
    cDate = matches.group(1)
  else:
    cDate = subprocess.check_output(fallback)
    matches = re.search(r'.*(\d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2}).*', cDate)
    cDate = matches.group(1)
  _log('Date after parsing', cDate)
  return datetime.strptime(cDate, "%Y:%m:%d %H:%M:%S")

HORA=datetime.now()
def _log(field, message, force=False):
  print(1)
  import traceback
  print(2)
  global HORA
  print(3)
  msg = "{} {}: {}".format("+"*(len(traceback.extract_stack())), field, message) #str(message).encode('ascii', 'replace'))
  print(4)
  if DEBUG or force: print(msg.encode("ascii", "replace"))
  print(5)
  if LOG_TO_FILE: log.write(msg.encode("ascii", "replace"))
  print(6)
###################### Main program ########################
log = open('/volume1/homes/fernando/log/{}-organize_media.log'.format(datetime.strftime(HORA, "%Y_%m_%d-%H_%M_%S")), 'w')
os.umask(0000)

try:
  _log("Program","BEGIN")
  _log("DEBUG", DEBUG)
  _log("DRY_RUN", DRY_RUN)

  month_names = [u"01 - Janeiro", u"02 - Fevereiro", u"03 - Marco", u"04 - Abril", u"05 - Maio", u"06 - Junho", u"07 - Julho", u"08 - Agosto", u"09 - Setembro", u"10 - Outubro", u"11 - Novembro", u"12 - Dezembro"]

  destinationDir = {
    "jpg": "/volume1/photo",
    "mov": "/volume1/video",
    "mp4": "/volume1/video"
  }
  _log("destinationDir", destinationDir)

  sourceDir = '/volume1/photo/import'
  destDir = '/volume1/photo/output'
  errorDir = '/volume1/photo/output/unsorted/'

  # The format for the new file names.
  fmt = "%Y_%m_%d-%H_%M_%S"
  _log('fmt', fmt)

  # The problem files.
  problems = []

  # Get all the JPEGs in the source folder.
  medias = os.listdir(sourceDir)
  medias = [ x for x in medias if (extensions.count(x[-3:]) == 1) or (extensions.count((x[-3:]).lower()) == 1) ]
  # Prepare to output as processing occurs
  lastMonth = 0
  lastYear = 0

  _log("medias", "Number of files to process {0}".format(len(medias)), force=True)
  if len(medias) == 0:
    remove_log = True
  else:
    remove_log = False
  # Create the destination folder if necessary
  if not os.path.exists(destDir):
    if not DRY_RUN:
      os.makedirs(destDir, mode=0777)
      subprocess.check_output(['synoindex', '-A', destDir])
      _log("Directory", "Making dir {} with permissions 0777".format(destDir))
    else:
      _log("DRY-RUN - Directory", "Making dir {} with permissions 0777".format(destDir))

  # Copy medias into year and month subfolders. Name the copies according to
  # their timestamps. If more than one media has the same timestamp, add
  # suffixes '1', '2', etc. to the names.
  dates = {}
  _log("Process", "Start", force=True)
  for idx, media in enumerate(medias):
    _log("Media" , media)
    original = sourceDir + '/' + media
    suffix = 1
    try:
      _log(80*'='+ '\nFILE NAME', original)
      EXTENSION=extension(original).lower()
      _log('EXTENSION', EXTENSION)
      vDate = mediaDate(original)
      _log('vDate', vDate)
      yr = vDate.year
      mo = vDate.month
      newname = vDate.strftime(fmt)
      _log('newname', newname)
      month_name = month_names[mo-1]
      _log('month_name', month_name)
      destDir = destinationDir[EXTENSION]
      thisDestDir = destDir + ('/%04d/%s' % (yr, month_name))
      _log('thisDestDir', thisDestDir)
      if not os.path.exists(thisDestDir):
        if not DRY_RUN:
          os.makedirs(thisDestDir, mode=0777)
          subprocess.check_output(['synoindex', '-A', thisDestDir])
          _log("Directory", "Making dir {} with permissions 0777".format(thisDestDir))
        else:
          _log("DRY_RUN - Directory", "Making dir {} with permissions 0777".format(thisDestDir))

      duplicate = thisDestDir + '/%s.%s' % (newname, EXTENSION)
      _log('duplicate', duplicate)
      while os.path.exists(duplicate):
        newname = vDate.strftime(fmt) + "({})".format(suffix)
        duplicate = destDir + '/%04d/%s/%s.%s' % (yr, month_name, newname, EXTENSION)
        suffix = suffix + 1
      if not DRY_RUN:
        shutil.move(original, duplicate)
        subprocess.check_output(['synoindex', '-a', duplicate])
        _log("File", "Moving from {} to {}".format(original, duplicate), force=True)
      else:
        _log("DRY_RUN - File", "Moving from {} to {}".format(original, duplicate), force=True)
    except Exception as e:
      _log("Exception", e)
      if not os.path.exists(errorDir):
        if not DRY_RUN:
          os.makedirs(errorDir, mode=0777)
          _log("Directory", "Making dir {} with permissions 0777".format(errorDir))
        else:
          _log("DRY_RUN - Directory", "Making dir {} with permissions 0777".format(errorDir))
      if not DRY_RUN:
        shutil.move(original, errorDir + media)
        _log("File", "Moving from {} to {}".format(original, errorDir + media))
      else:
        _log("DRY_RUN - File", "Moving from {} to {}".format(original, errorDir + media))
      problems.append(media)
    except:
      sys.exit("Execution stopped.")

  # Report the problem files, if any.
  if len(problems) > 0:
    _log("Problem files", "\n".join(problems))
    _log("These can be found in", errorDir)
except Exception, e:
  _log("Exception", e)
  #log.write(e + "\n")
finally:
  _log("Program","END")
  log.close()
  if remove_log:
    os.remove('/volume1/homes/fernando/log/{}-organize_media.log'.format(datetime.strftime(HORA, "%Y_%m_%d-%H_%M_%S")))
