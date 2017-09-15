#!/usr/bin/env python3

"""
README
subprocess.check_output has issues with the filenames, perhaps due to the spaces, so the solution
is to output this to a bash script and run that.

$ brew install imagemagick
$ python3 bin/convert_tifs_to_pngs.py > bin/convert_tifs_to_pngs.sh
$ bash bin/convert_tifs_to_pngs.sh
"""

import glob

FILES = glob.glob('/Users/freen/Desktop/cropped/**/*.tif', recursive=True)
IMAGEMAGICK_FUZZ = 0

for file in FILES:
    target_png_fpath = file.replace('.tif', '.png')
    cmd = [
        '/usr/local/bin/convert',
        "\"%s\"" % file,
        "-fuzz %d%%" % IMAGEMAGICK_FUZZ,
        '-fill "#FFFFFF"',
        '-opaque "#DDDDDD"',
        "\"%s\"" % target_png_fpath
    ]
    print(' '.join(cmd))
