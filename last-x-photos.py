"""
    Make a list of the last x photos based and sorted by
    the filename
"""
from __future__ import print_function
# Begin customization -------------------------------------

QUANTITY = 1000
SOURCE_DIR=u'/volume1/photo'
YEARS = xrange(2009, 1+2014) #exclude last
DESTINATION_DIR=u'/volume1/backups/Dropbox/Fernando/Fotos dropbox Thais'

# End customization ---------------------------------------
# ---------------------------------------------------------
import os
from shutil import copy2
from pprint import pprint
from PIL import Image
#__debug__ = True

def fullpath(item, item2):
    return os.path.join(item, item2)

def get_last_photos(quantity):
    years_paths = [ os.path.realpath(os.path.expanduser(os.path.join(SOURCE_DIR, str(year)))) for year in YEARS ]
    years_paths.sort(reverse=True)
    _LAST_X_PHOTOS = []
    for year_path in years_paths:
        for root, dirs, files in os.walk(year_path):
            if dirs.count(u'eaDir'):
                dirs.remove(u'eaDir')
            dirs.sort(reverse=True)
            files.sort(reverse=True)
            files = [ _file for _file in files if _file.endswith(u'.jpg') and not _file.endswith(u'.DS_Store')]
            already_added = len(_LAST_X_PHOTOS)
            if __debug__: print(root, len(files), len(_LAST_X_PHOTOS))
            if already_added < quantity:
                _LAST_X_PHOTOS.extend(files[:quantity-already_added])
                _path = [root]*len(_LAST_X_PHOTOS)
                _LAST_X_PHOTOS = map(fullpath, _path, _LAST_X_PHOTOS)
            else:
                break
        if len(_LAST_X_PHOTOS) >= quantity:
            break
    return _LAST_X_PHOTOS

def bigger(image):
    img = Image.open(image)
    return True if img.size[0]*img.size[1]>4000000 else False

if __name__ == '__main__':
    last_photos = get_last_photos(QUANTITY)

    # print(last_photos)
    only_names = [ os.path.basename(photo) for photo in last_photos ]
    only_names = [ photo for photo in only_names if not photo.endswith(u'.DS_Store') ] # Fix photos selected
    # print(only_names)

    photos_on_destination = os.listdir(os.path.expanduser(DESTINATION_DIR))
    only_names_on_destination = [ os.path.basename(photo) for photo in photos_on_destination if not photo.endswith(u'.DS_Store') ] # Fix photos selected
    # print(only_names_on_destination)

    photos_to_add = set(only_names) - set(only_names_on_destination)
    photos_to_remove = set(only_names_on_destination) - set(only_names)

    photos_to_add_tuple_list = [ (photo, os.path.join(os.path.expanduser(DESTINATION_DIR), os.path.basename(photo))) for photo in last_photos if os.path.basename(photo) in photos_to_add ]
    photos_to_remove_fullpath = [ os.path.join(os.path.expanduser(DESTINATION_DIR), photo) for photo in photos_to_remove ]

    # print(u'add', photos_to_add_tuple_list)
    # print(u'remove', photos_to_remove_fullpath)

    total_photos_to_add = len(photos_to_add_tuple_list)
    if __debug__: print(u'Adding {} photos'.format(total_photos_to_add))
    for i, item in enumerate(photos_to_add_tuple_list):
        src, dst = item
        if __debug__: print(total_photos_to_add - i, end=u'.')
        # print(src, dst)
        copy2(src, dst)
    if __debug__: print()

    total_photos_to_remove = len(photos_to_remove_fullpath)
    if __debug__: print(u'Removing {} photos'.format(total_photos_to_remove))
    for i, photo in enumerate(photos_to_remove_fullpath):
        if __debug__: print(total_photos_to_remove - i, end=u'.')
        # print(photo)
        os.remove(photo)
    if __debug__: print()

    photos_to_resize = os.listdir(os.path.expanduser(DESTINATION_DIR))
    photos_to_resize = [ os.path.join(os.path.expanduser(DESTINATION_DIR), os.path.basename(photo)) for photo in photos_to_resize if not photo.endswith(u'.DS_Store') and bigger(os.path.join(os.path.expanduser(DESTINATION_DIR), os.path.basename(photo))) ]

    # photos_to_resize = photos_to_resize[:10]
    # print(u'resize', photos_to_resize)

    total_photos_to_resize = len(photos_to_resize)
    if __debug__: print(u'Resizing {} photos'.format(total_photos_to_resize))
    for i, photo in enumerate(photos_to_resize):
        if __debug__: print(total_photos_to_resize - i, end=u'.')
        #print(photo)
        img = Image.open(photo)
        new_img = img.resize((img.size[0]/2, img.size[1]/2))
        new_img.save(photo, exif=img.info[u'exif'])
    if __debug__: print()
