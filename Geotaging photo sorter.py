# -*- coding: utf-8 -*-
"""
Created on Sun Mar 14 21:34:56 2021

@author: zieli

Copy this scripy to folder with your photos and run.
"""

# Import Python image library:
from PIL import Image
import shutil
import os
#create a dictionary with data from image:
def get_exif(filename):
    image = Image.open(filename)
    image.verify()
    return image._getexif()

#import TAGS and GEOTEAGS to make data human readable:
from PIL.ExifTags import TAGS
from PIL.ExifTags import GPSTAGS

# import GPS data form exif dict:
def get_geotagging(exif):
    if not exif:
        raise ValueError("No EXIF metadata found")

    geotagging = {}
    for (idx, tag) in TAGS.items():
        if tag == 'GPSInfo':
            if idx not in exif:
                raise ValueError("No EXIF geotagging found")

            for (key, val) in GPSTAGS.items():
                if key in exif[idx]:
                    geotagging[val] = exif[idx][key]

    return geotagging

#changing degree-minutes-seconds to decimal value:

def get_decimal_from_dms(dms, ref):
    degrees = dms[0]
    minutes = dms[1] / 60.0
    seconds = dms[2] / 3600.0

    if ref in ['S', 'W']:
        degrees = -degrees
        minutes = -minutes
        seconds = -seconds

    return round(degrees + minutes + seconds, 5)

def get_coordinates(geotags):
    
    lat = get_decimal_from_dms(geotags['GPSLatitude'], geotags['GPSLatitudeRef'])
        
    lon = get_decimal_from_dms(geotags['GPSLongitude'], geotags['GPSLongitudeRef'])
    
    return (lat,lon)


from geopy.geocoders import Nominatim

# Pick OpenStreetMap data:


def get_city_name(geo_address):
    city = ''
    for i in geo_address:
        if i != ',':
            city += i
        else:
            break
    return city

def get_country_name(geo_address):
    country = ''
    for i in range(len(geo_address)+1):
        if geo_address[-i] != ',':
            country = geo_address[-i:]
        else:
            break
    return country

def folder_name(country, city):
    return str(country + ', ' + city)

def create_new_dir(new_dir):
    if new_dir not in os.listdir(os.getcwd()):
        os.mkdir(new_dir)

dir_list = os.listdir(os.getcwd())
new_dir_list = []
for pic in dir_list:
    try:
        if pic.endswith('.jpg'):
            exif = get_exif(pic)
            geotags = get_geotagging(exif)
            coordinates = get_coordinates(geotags)  
            locator = Nominatim(user_agent='myGeocoder')
            location = locator.reverse(coordinates, language = 'pl, en-gb',zoom = 10)
            geo_address = location.address
            city = get_city_name(geo_address)
            country = get_country_name(geo_address)
            new_dir = folder_name(country, city)
            create_new_dir(new_dir)
            shutil.move(os.getcwd() + '\\' + pic, os.getcwd() + '\\' + new_dir + '\\' + pic)
            new_dir_list.append(new_dir)
            print('Moving ' + pic + ' to' + new_dir)
    except KeyError:
        print('No GPS Info in', pic)
        continue

