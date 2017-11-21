import unittest
from slack_trees import SlackTrees
from utilities import get_qgis_app


QGISS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class SlackTreesTest(unittest.TestCase):

    def setUp(self):
        self.plugin = SlackTrees(IFACE)

    def tearDown(self):
        self.plugin = None

    def test_fail(self):
        self.fail('FAIl')


if __name__ == "__main__":
    suite = unittest.makeSuite(SlackTreesTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)