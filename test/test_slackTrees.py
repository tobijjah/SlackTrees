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
        actual = list(self.plugin._get_unfiltered_features())

        self.assertEqual(len(actual), len(expected))

    def test_get_filtered_features(self):
        expected = list(self.layer.getFeatures(QgsFeatureRequest().setFilterExpression(u'"random" = 4')))
        actual = list(self.plugin._get_filtered_features(3, '==', 4))

        self.assertEqual(len(actual), len(expected))

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


if __name__ == "__main__":
    suite = unittest.makeSuite(SlackTreesTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
