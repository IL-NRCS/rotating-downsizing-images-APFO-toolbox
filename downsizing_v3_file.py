###############################################
## Arielle Simmons-Steffen                   ##
## Jason Hellums                             ##
##                                           ##
## USDA-NRCS                                 ##
## Date created: September 4, 2022           ##
## Date modified: September 9, 2022          ##
###############################################
## Final product must be a toolbox that works with ArcPro 2
## The librariers for DOWNSAMPLING 
## included in the default ArcPro Py3 install. 
from PIL import Image, ImageFile
from PIL.TiffTags import TAGS
import os
import glob
import arcpy
import logging

Image.MAX_IMAGE_PIXELS = 10000000000
print('start')

## ToDO: Set Footprint to map to a shapefile or gdb/feature class
footprint = arcpy.GetParameterAsText(0)

direction_col = arcpy.GetParameterAsText(1)

photopath_col = arcpy.GetParameterAsText(2)

logging.basicConfig(level=logging.INFO, filename='downsampling_failed.log', datefmt='%Y-%m-%d %H:%M:%S') #Create a log file

def get_photopath_direction_map(footprint):
    """ Get mapping of photopath to direction """
    cursor = arcpy.SearchCursor(footprint)
    map = {}
    for row in cursor:
        direction = row.getValue(direction_col)
        photopath = row.getValue(photopath_col)
        map[photopath] = direction
    return map

def save_with_rotation(photopath, path, mode, rotation=None):
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    image = Image.open(photopath)
    image.mode = mode
    if rotation:
        image = image.rotate(rotation)
    ## convert 'RGB' 
    image.convert('RGB').save(os.path.join(path, f'{im_name}_downsampled.jpg'), dpi=(300, 300))

def process_file(photopath, direction):
    # skip if no direction specified
    if direction is None:
        try:
            save_with_rotation(photopath, path, mode='L')
        except:
            try:
                save_with_rotation(photopath, path, mode='RGB')
            except Exception as e:
                logging.info(f"Failed to downsample {im_name}.tif error: {e}")

    elif os.path.isfile(photopath.replace('.tif', '.jpg')):
        return
    
    elif direction == 'EW':
        try:
            ### for standard 8 bit black and white
            save_with_rotation(photopath, path, mode='L', rotation=90.0)
        except:
            ### for 24 bit rgb
            try:
                save_with_rotation(photopath, path, mode='RGB', rotation=90.0)
            except Exception as e:
                logging.info(f"Failed to downsample {im_name}.tif error: {e}")
    else:
        try:
            save_with_rotation(photopath, path, mode='L')
        except:
            try:
                save_with_rotation(photopath, path, mode='RGB')
            except Exception as e:
                logging.info(f"Failed to downsample {im_name}.tif error: {e}")

## MAKE pd_path from the footprint file
pd_map = get_photopath_direction_map(footprint)

for photopath, direction in pd_map.items():

    if direction == None:
        continue
    elif direction == '':
        direction == None
    photopath = photopath.replace("/", "\\")
    data = photopath.rsplit('\\', 1)
    path = data[0]
    im = data[1]
    im_data = im.rsplit('.',1)
    im_name = im_data[0]
    process_file(photopath, direction)

print('complete')
