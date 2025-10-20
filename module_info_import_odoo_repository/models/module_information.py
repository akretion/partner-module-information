import logging
import re

import requests

from odoo import api, models

_logger = logging.getLogger(__name__)


class ModuleInformation(models.Model):
    _inherit = "module.information"

    # called by cron
    @api.model
    def synchronize_module_from_odoo_repository(self):
        url = self.env["ir.config_parameter"].sudo().get_param("odoo_repository_url")
        response = requests.get(url, timeout=60)
        for module in response.json():
            self.with_delay()._update_module_from_odoo_repository(module)

    def _update_module_from_odoo_repository(self, module):
        version_id = self.env["odoo.version"]._get_id(module["branch"])
        version = self.env["odoo.version"].browse(version_id)
        url = module["repository"]["repo_url"].lower()
        match = re.search(r"github\.com\/([^\/]+)\/([^\/]+)", url)
        if match:
            # Only support github module for now, use org and repo
            # from the url to be homogenious with existing data from
            # module_info_import
            org, repo = match.groups()
            mod = self._update_or_create_modules(
                version,
                org,
                repo,
                module["module"],
                self._prepare_vals_from_odoo_repository(module),
            )
            mod_version = mod.module_version_ids.filtered(
                lambda s: s.version_id == version
            )
            if mod_version.migrations != module["migrations"]:
                mod_version.migrations = module["migrations"]
                mod_version._update_migration_hook()

    def _prepare_vals_from_odoo_repository(self, module):
        return {
            "description": module["summary"],
            "shortdesc": module["title"],
            "authors": ",".join(module["authors"]),
        }
