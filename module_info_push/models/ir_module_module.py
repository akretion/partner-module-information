import logging

import requests

from odoo import _, api, fields, models, release
from odoo.exceptions import UserError
from odoo.modules.module import get_module_path

_logger = logging.getLogger(__name__)


ERROR_MESSAGE = _("There is an issue with module synchronization")


class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    is_custom_module = fields.Boolean(compute="_compute_is_custom_module", store=True)

    @api.model
    def _get_installed_module_info(self):
        modules = self.search([("state", "in", ("installed", "to upgrade"))])
        return {
            "version": release.version,
            "modules": [
                {
                    "name": module.name,
                    "shortdesc": module.shortdesc,
                    "description": module.description_html,
                    "author": module.author,
                    "is_custom": module.is_custom_module,
                }
                for module in modules
            ],
        }

    # called by cron
    @api.model
    def push_installed_module_info(self):
        # get external instance for which we want to send the data
        api_key = self.env["ir.config_parameter"].sudo().get_param("module.api.key")
        api_url = self.env["ir.config_parameter"].sudo().get_param("module.api.url")
        if not api_key or not api_url:
            return
        module_info = self._get_installed_module_info()
        url = f"{api_url}/module-api/module/synchronize_installed_module_info"
        headers = {"API-KEY": api_key}
        try:
            res = requests.post(
                url, headers=headers, json={"modules_info": module_info}, timeout=3
            )
        except Exception as e:
            _logger.error("Error when calling odoo %s", e)
            raise UserError(ERROR_MESSAGE) from e
        data = res.json()
        if isinstance(data, dict) and data.get("code", 0) >= 400:
            _logger.error(
                "Error module sync API : %s : %s",
                data.get("name"),
                data.get("description"),
            )
            raise UserError(ERROR_MESSAGE)
        return data

    def _compute_is_custom_module(self):
        custom_path = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("module.custom.path", "/local-src/")
        )
        for record in self:
            module_path = get_module_path(record.name)
            record.is_custom_module = module_path and custom_path in module_path
