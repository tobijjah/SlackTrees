import os
import unittest
from slack_trees import SlackTrees
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
        expected_length = len(list(self.layer.getFeatures()))
        actual_length = len(list(self.plugin._get_unfiltered_features()))

        self.assertEqual(actual_length, expected_length)


if __name__ == "__main__":
    suite = unittest.makeSuite(SlackTreesTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
