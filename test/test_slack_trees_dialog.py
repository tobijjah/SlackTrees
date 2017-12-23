# coding=utf-8
"""Dialog test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tobi.seyde@gmail.com'
__date__ = '2017-11-14'
__copyright__ = 'Copyright 2017, Tobias Seydewitz'

import unittest
from PyQt4.QtGui import QDialogButtonBox, QDialog
from slack_trees_dialog import SlackTreesDialog
from utilities import get_qgis_app


QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class SlackTreesDialogTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        """Runs before each test."""
        self.dialog = SlackTreesDialog(None)

    def tearDown(self):
        """Runs after each test."""
        self.dialog = None

    @unittest.skip('Button does not exists any more')
    def test_dialog_ok(self):
        """Test we can click OK."""
        button = self.dialog.CancelOkButtons.button(QDialogButtonBox.Ok)
        button.click()
        result = self.dialog.result()
        self.assertEqual(result, QDialog.Accepted)

    def test_dialog_cancel(self):
        """Test we can click cancel."""
        button = self.dialog.CancelButton.button(QDialogButtonBox.Cancel)
        button.click()
        result = self.dialog.result()
        self.assertEqual(result, QDialog.Rejected)

    def test_progressbar_update(self):
        expected = 10
        self.dialog._update_progressbar(10)
        result = self.dialog.ProgressBar.value()

        self.assertEqual(expected, result)


if __name__ == "__main__":
    suite = unittest.makeSuite(SlackTreesDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
