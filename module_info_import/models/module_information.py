import logging

import requests
import yaml

from odoo import _, api, models

_logger = logging.getLogger(__name__)


ERROR_MESSAGE = _("There is an issue with module information synchronization")


class ModuleInformation(models.Model):
    _inherit = "module.information"

    @api.model
    def get_module_info(self, version):
        url = (
            "https://raw.githubusercontent.com/akretion"
            f"/odoo-module-tracker/gh-pages/{version}.yml"
        )
        response = requests.get(url, timeout=120)
        # not all odoo versions are present in the github yaml files we don't
        # want the sync cron to fail if version is not managed.
        if response.status_code != 200:
            return {}
        return yaml.safe_load(response.text)

    # called by cron
    @api.model
    def synchronize_module(self):
        versions = self.env["odoo.version"].search([])
        for version in versions:
            data = self.get_module_info(version.name)
            for orga, repos in data.items():
                for repo, modules in repos.items():
                    for module_name, vals in modules.items():
                        self._update_or_create_modules(
                            version, orga, repo, module_name, vals
                        )

    @api.model
    def _update_or_create_modules(
        self, version, orga_name, repo_name, module_name, vals
    ):
        repo = self._get_or_create_repo(orga_name, repo_name)
        vals = {
            "repo_id": repo.id,
            "name": module_name,
            "description": vals["description"],
            "shortdesc": vals["name"],
            "authors": vals["author"],
        }
        module = self.search([("name", "=", module_name), ("partner_id", "=", False)])
        if module:
            if module._should_update_module(version.name, orga_name):
                module.write(vals)
            module._add_available_version(version)
        else:
            vals.update({"available_version_ids": [(4, version.id, 0)]})
            module = self.create(vals)

    @api.model
    def _get_or_create_repo(self, orga_name, repo_name):
        repo = self.env["module.repo"].search(
            [("name", "=", repo_name), ("organization", "=", orga_name)]
        )
        if repo:
            return repo
        else:
            return self.env["module.repo"].create(
                {"organization": orga_name, "name": repo_name}
            )

    @api.model
    def _add_available_version(self, version):
        module_version = self.module_version_ids.filtered(
            lambda s: s.version_id == version
        )
        if module_version:
            if module_version.state != "done":
                # In case that a version have been creating from a pending PR
                module_version.state = "done"
        else:
            self.env["module.version"].create(
                {
                    "module_id": self.id,
                    "version_id": version.id,
                    "state": "done",
                }
            )

    @api.model
    def _should_update_module(self, version, orga):
        self.ensure_one()
        # It means that the module was first created by a push from a partner instance
        # we want to update it and avoid a crash in this case.
        if not self.available_version_ids:
            return True
        orga_priority = {"oca": 100, "akretion": 50}
        return max(
            [float(v) for v in self.mapped("available_version_ids.name")]
        ) <= float(version) and orga_priority.get(
            self.repo_id.organization, 0
        ) <= orga_priority.get(orga, 0)
