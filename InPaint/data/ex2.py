import os
import shutil
from PIL import Image, ImageStat
from typing import Optional
import hashlib

import warnings

warnings.filterwarnings("ignore")


def validate_images(input_dir: str,
                    output_dir: str,
                    log_file: str,
                    formatter: Optional[str] = ""):
    """
    [Ex 2] A method to validate images

    :param input_dir: A string input directory where the function looks for files
    :param output_dir: A string output directory where the function outputs files
    :param log_file: path to store the log-file
    :param formatter: string output name format

    :return: counts of copied valid files
    """

    # create output dir if does not exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # create log file dir if does not exist
    if not os.path.exists(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

    input_dir = os.path.abspath(input_dir)

    # walk over all files, and store their metadata
    keys = []
    metadata = {}
    print()
    # go over all files
    for dir_path, dir_names, filenames in os.walk(input_dir):
        for f in filenames:
            # add current filename as key
            keys.append(f)

            # full path of file
            path = os.path.join(dir_path, f)
            hash_value = None

            # attempt to read the file as an image file
            try:
                image_file = Image.open(path)

                # image specific metadata
                image_data = {
                    'mode': image_file.mode,
                    'variance': ImageStat.Stat(image_file).var,
                    'size': image_file.size
                }

                # md5 hash_value for current opened image
                hash_value = hashlib.md5(image_file.tobytes())
                hash_value = hash_value.hexdigest()

            except IOError as e:
                # not an image file
                image_data = None

            metadata[f] = {
                'path': path,
                'format': f.split('.')[-1],
                'hash': hash_value,
                'size': os.path.getsize(path),
                'image_data': image_data,
            }

    # sort according to filename
    # keys = sorted(keys, key=lambda x: os.path.basename(x).split('.')[0])
    already_copied, i = [], 0
    log_file_contents = ""

    for key in keys:
        data = metadata[key]
        errors = []
        # error codes 1-3
        if data['format'].lower() not in ['jpeg', 'jpg']:
            errors.append(f"{key};1\n")

        elif data['size'] > 250000:
            errors.append(f"{key};2\n")

        elif data['image_data'] is None:
            errors.append(f"{key};3\n")

        else:

            image_data = data['image_data']
            h, w = image_data['size']

            # error codes 4-6
            if h < 96 or w < 96 or image_data['mode'].lower() != 'rgb':
                errors.append(f"{key};4\n")

            if 0.0 in list(image_data['variance']):
                errors.append(f"{key};5\n")

            if len(already_copied) > 0 and data['hash'] in already_copied:
                errors.append(f"{key};6\n")

        if len(errors) == 0:
            # valid image file, copy and add hash to already copied
            shutil.copy(data['path'], os.path.join(output_dir, f"{i:{formatter}}.jpg"))
            already_copied.append(data['hash'])
            i += 1
        else:
            log_file_contents += errors[0]

    # write logfile
    with open(log_file, 'w') as lf:
        lf.writelines(log_file_contents)
    lf.close()

    return i
