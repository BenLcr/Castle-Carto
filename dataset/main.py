import os
import json
import re
import cv2
import pandas as pd
from datetime import datetime
from geopy.distance import geodesic
from image_downloading import download_image

# coord_eiffel = [48.858370, 2.294481]
coord_list = []
largeur_plan = 200

def extract_wgs84(input_csv):
    # Charger le fichier CSV
    df = pd.read_csv(input_csv, delimiter=';')
    
    coord = df['coordonnees_au_format_WGS84'].dropna()

    return coord

def create_square_lat_lon(lat, lon, side_length=largeur_plan):
    half_side_meters = side_length / 2  # Rayon du carré en mètres
    # Calculer les décalages en latitude et longitude
    # 1 degré de latitude équivant environ à 111.32 km, et pour la longitude cela varie selon la latitude
    offset = geodesic(meters=half_side_meters)
    # Calculer les coordonnées des 4 coins du carré
    upper_left = offset.destination((lat, lon), 135)  # Angle 135° pour haut-gauche
    lower_right = offset.destination((lat, lon), 315)  # Angle 315° pour bas-droit
    return upper_left.latitude, upper_left.longitude, lower_right.latitude, lower_right.longitude

file_dir = os.path.dirname(__file__)
prefs_path = os.path.join(file_dir, 'preferences.json')
default_prefs = {
        'url': 'https://mt.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        'tile_size': 256,
        'channels': 3,
        'datafile': os.path.join(file_dir, 'database.csv'),
        'dir': os.path.join(file_dir, 'images'),
        'headers': {
            'cache-control': 'max-age=0',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'
        },
        'tl': '',
        'br': '',
        'zoom': ''
    }

def run():
    with open(os.path.join(file_dir, 'preferences.json'), 'r', encoding='utf-8') as f:
        prefs = json.loads(f.read())

    if not os.path.isdir(prefs['dir']):
        os.mkdir(prefs['dir'])

    datadir = prefs['datafile']
    
    coord_list = extract_wgs84(datadir)

    print(coord_list)

    # Création d'images à partir de la liste de coordonnées
    for elt in coord_list:
        lat, lon = map(float, elt.split(','))

        lat = float(lat)
        lon = float(lon)
        
        lat2, lon2, lat1, lon1 = create_square_lat_lon(lat, lon)

        print(lat2, lon2, lat1, lon1)

        zoom = 18
        channels = int(prefs['channels'])
        tile_size = int(prefs['tile_size'])

        img = download_image(lat1, lon1, lat2, lon2, zoom, prefs['url'],
            prefs['headers'], tile_size, channels)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        name = f'img_{timestamp}.png'
        cv2.imwrite(os.path.join(prefs['dir'], name), img)
        print(f'Saved as {name}')


if os.path.isfile(prefs_path):
    run()
else:
    with open(prefs_path, 'w', encoding='utf-8') as f:
        json.dump(default_prefs, f, indent=2, ensure_ascii=False)

    print(f'Preferences file created in {prefs_path}')
