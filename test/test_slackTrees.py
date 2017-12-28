import os
import unittest
from slack_trees import SlackTrees
from qgis.core import QgsFeatureRequest, QgsCoordinateTransform, QgsCoordinateReferenceSystem
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

    def test_latlon_to_epsg(self):
        result = self.plugin.latlon_to_epsg(-177.3456, 56.2423)
        expected = 32601

        self.assertEqual(result, expected)

    def test_latlon_to_epsg_raises(self):
        x, y = 10, -91
        msg = 'lat/x {:f} and lon/y {:f} overflowing WGS84 coordinates system'.format(y, x)

        with self.assertRaises(ValueError) as err:
            self.plugin.latlon_to_epsg(x, y)

        self.assertEqual(str(err.exception), msg)

    def test_reproject_features(self):
        feature_generator = self.layer.getFeatures()

        expected = list(self.layer.getFeatures())
        result = list(self.plugin._reproject_features(feature_generator))

        self.assertEqual(len(result), len(expected))

    def test_reproject_features_reprojection(self):
        gen = self.layer.getFeatures()
        src_crs = self.layer.crs()
        dst_crs = QgsCoordinateReferenceSystem(32633)
        transform = QgsCoordinateTransform(src_crs, dst_crs)

        expected = [fet for fet in self.layer.getFeatures()]
        result = list(self.plugin._reproject_features(gen))

        for exp, res in zip(expected, result):
            geometry = exp.geometry()
            geometry.transform(transform)

            self.assertEqual(len(res.attributes()), len(exp.attributes()))
            self.assertEqual(res.geometry().asPoint(), geometry.asPoint())

    # TODO implement
    def test_reproject_feature(self):
        pass

    # TODO implement
    def test_reproject_geometry(self):
        pass

    def test_reproject_geometry_raise(self):
        with self.assertRaises(AssertionError):
            self.plugin._reproject_geometry('foo')

        with self.assertRaises(AssertionError):
            self.plugin._reproject_geometry('foo', src_crs='bar')

    # TODO test with invalid layer
    def test_valid_bounds(self):
        result = self.plugin._valid_bounds()
        self.assertEqual(result, True)

    def test_bounding_box(self):
        pass

    # TODO write test
    def test_slacklines(self):
        feature_generator = self.plugin._reproject_features(self.layer.getFeatures())
        result = list(self.plugin._slacklines(feature_generator))
        print result

    def test_min_distance(self):
        # init test
        result = self.plugin.min_distance
        self.assertEqual(result, 10.0)

        # setter test
        self.plugin.min_distance = 10
        self.assertEqual(self.plugin.min_distance, 10)

    def test_min_distance_raises(self):
        with self.assertRaises(TypeError):
            self.plugin.min_distance = '1'

        with self.assertRaises(ValueError):
            self.plugin.min_distance = -1.0

        with self.assertRaises(ValueError):
            self.plugin.min_distance = 500.00

    def test_max_distance(self):
        # init test
        result = self.plugin.max_distance
        self.assertEqual(result, 50.0)

        # setter test
        self.plugin.max_distance = 100
        self.assertEqual(self.plugin.max_distance, 100)

    def test_max_distance_raises(self):
        with self.assertRaises(TypeError):
            self.plugin.max_distance = '1'

        with self.assertRaises(ValueError):
            self.plugin.max_distance = -1.0

        with self.assertRaises(ValueError):
            self.plugin.max_distance = 501.00


if __name__ == "__main__":
    suite = unittest.makeSuite(SlackTreesTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
