import ee # earth engine api
import geemap.core as geemap

if __name__ == '__main__':
    ee.Authenticate(force=True)
    ee.Initialize(project='ee-lacourbenjamin03')

    # Coordonées du point
    coord = [46.1633974353336, 3.19505819948892]
    point = ee.Geometry.Point(coord)

    # Créer une région autour du point (un carré de 0.1 degrés de côté)
    region = point.buffer(5000).bounds().getInfo()['coordinates']

    # Charger la collection d'images Sentinel-2
    sentinel_collection = ee.ImageCollection('COPERNICUS/S2_HARMONIZED') \
        .filterBounds(point) \
        .filterDate('2024-01-01', '2024-12-31') \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 5)) 

    # Sélectionner une seule image pour vérification
    image = sentinel_collection.first()

    # Exporter l'image vers Google Drive
    export_task = ee.batch.Export.image.toDrive(
        image=image,
        description='Export_Sentinel_Allier',
        scale=10,  # Résolution spatiale en mètres par pixel
        region=region,  # Utilisation de la région définie
        fileFormat='GeoTIFF'
    )
    
    # Lancer l'exportation
    export_task.start()

    print("Exportation commencée !")
