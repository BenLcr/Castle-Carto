import ee
ee.Authenticate(force=True)
ee.Initialize(project='my-project')
print(ee.String('Hello from the Earth Engine servers!').getInfo())