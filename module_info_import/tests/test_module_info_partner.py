import os

import requests_mock
import yaml

from odoo.tests import TransactionCase


class TestinfoImport(TransactionCase):
    def setUp(self):
        super().setUp()
        data_dir = os.path.join(
            os.path.dirname(__file__), "data", "module_list_14.yaml"
        )
        with open(data_dir) as f:
            self.modules_yaml = f.read()
        self.env["odoo.version"].search([]).unlink()
        self.env["odoo.version"].create({"name": "14.0"})

    def test_modules_import(self):
        with requests_mock.mock() as m:
            m.get(
                "https://raw.githubusercontent.com/akretion/"
                "odoo-module-tracker/gh-pages/14.0.yml",
                text=self.modules_yaml,
            )

            self.env["module.information"].synchronize_module()

            modules_dict = yaml.safe_load(self.modules_yaml)

            module_list = []
            for _orga, repos in modules_dict.items():
                for _repo, modules in repos.items():
                    for module in modules:
                        if module not in module_list:
                            module_list.append(module)

            self.assertEqual(
                len(module_list),
                self.env["module.information"].search_count(
                    [("available_version_ids", "=", "14.0")]
                ),
            )

    def test_modules_import_duplicate(self):
        data_dir = os.path.join(
            os.path.dirname(__file__), "data", "module_list_14_duplicate.yaml"
        )

        with open(data_dir) as f:
            self.modules_yaml = f.read()
            with requests_mock.mock() as m:
                m.get(
                    "https://raw.githubusercontent.com/akretion/"
                    "odoo-module-tracker/gh-pages/14.0.yml",
                    text=self.modules_yaml,
                )
                self.env["module.information"].synchronize_module()
                module = self.env["module.information"].search(
                    [("name", "=", "single_module_test")]
                )
                # test module single is imported
                self.assertEqual(module.repo_id.organization, "tiers")
                # test module duplicate
                module = self.env["module.information"].search(
                    [("name", "=", "duplicate_module_test1")]
                )
                # check priority to OCA
                self.assertEqual(module.repo_id.organization, "oca")
                # test duplicate module diffrent order
                module = self.env["module.information"].search(
                    [("name", "=", "duplicate_module_test2")]
                )
                # check priority to OCA
                self.assertEqual(module.repo_id.organization, "oca")
