import logging
import os

import requests_mock

from odoo.tests import TransactionCase

_logger = logging.getLogger(__name__)


class TestinfoImport(TransactionCase):
    def setUp(self):
        super().setUp()
        self.modules = {"sale_import_delivery_carrier": 1}
        data_dir = os.path.join(os.path.dirname(__file__), "data", "pr.diff")
        with open(data_dir) as f:
            self.pr_diff = f.read()

    def test_module_from_pr(self):
        url = "https://api.github.com/repos/test/test/pulls"
        with requests_mock.mock() as m:
            m.get(url, text=self.pr_diff)
            res = self.env["pull.request"]._get_module_from_pr(url, self.modules)
            self.assertEqual(len(res), 1)
