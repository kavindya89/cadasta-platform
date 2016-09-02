from osgeo import gdal, ogr

from django.contrib.gis.geos import GeometryCollection, GEOSGeometry

# enable osgeo exceptions
gdal.UseExceptions()

KEEP_LAYERS = ['tracks', 'routes', 'waypoints']


class GPXProcessor:

    def __init__(self, gpx_file):
        self.driver = ogr.GetDriverByName('GPX')
        self.ds = self.driver.Open(gpx_file)

    def get_layers(self):
        """Get the layers from the GPX file."""
        layers = {}
        layer_count = self.ds.GetLayerCount()
        for idx in range(0, layer_count):
            layer = self.ds.GetLayerByIndex(idx)
            name = layer.GetName()
            if name in KEEP_LAYERS:
                features = self._get_features(layer)
                layers[name] = features
        return layers

    def _get_features(self, layer):
        """Get the features from the layer."""
        features = []
        for f in range(0, layer.GetFeatureCount()):
            feature = layer.GetFeature(f)
            wkt = feature.GetGeometryRef().ExportToWkt()
            geom = GEOSGeometry(wkt)
            features.append(geom)
        return GeometryCollection(features)
