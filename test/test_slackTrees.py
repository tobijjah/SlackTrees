import os
import unittest
from slack_trees import SlackTrees
from qgis.core import QgsFeatureRequest
from utilities import get_qgis_app, make_test_layer, delete_layer


QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class SlackTreesTest(unittest.TestCase):

    def setUp(self):
        self.plugin = SlackTrees(IFACE)
        self.layer, self.path = make_test_layer(os.path.join(os.path.dirname(__file__), 'test_layer.shp'))
        self.plugin.layer = self.layer

    def tearDown(self):
        self.plugin = None
        self.layer = None
        delete_layer(self.path)

    def test_get_unfiltered_features(self):
        expected = list(self.layer.getFeatures())
        result = list(self.plugin._get_unfiltered_features())

        self.assertEqual(len(result), len(expected))

    def test_get_filtered_features(self):
        expected = list(self.layer.getFeatures(QgsFeatureRequest().setFilterExpression(u'"random" = 4')))
        result = list(self.plugin._get_filtered_features(3, '==', 4))

        self.assertEqual(len(result), len(expected))

    def test_get_features(self):
        all_features = list(self.plugin._get_features('', '', ''))
        unknown_field = list(self.plugin._get_features('test', '==', 'test'))
        expected = list(self.layer.getFeatures(QgsFeatureRequest().setFilterExpression(u'"random" = 4')))
        known_field = list(self.plugin._get_filtered_features(3, '==', 4))

        self.assertEqual(len(all_features), 20)
        self.assertEqual(len(unknown_field), 20)
        self.assertEqual(len(known_field), len(expected))

    def test_reproject_features(self):
        feature_generator = self.layer.getFeatures()
        print self.layer.crs()

    def test_latlon_to_epsg(self):
        result = self.plugin._latlon_to_epsg(-177.3456, 56.2423)
        expected = 32601

        self.assertEqual(result, expected)

    def test_latlon_to_epsg_raises(self):
        x, y = 10, -91
        msg = 'lat/x {:f} and lon/y {:f} overflowing WGS84 coordinates system'.format(y, x)

        with self.assertRaises(ValueError) as err:
            self.plugin._latlon_to_epsg(x, y)

        self.assertEqual(str(err.exception), msg)


if __name__ == "__main__":
    suite = unittest.makeSuite(SlackTreesTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
