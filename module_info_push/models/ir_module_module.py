# coding: utf-8

import requests
from odoo import models, fields, api, release, _
from odoo.exceptions import UserError
import logging


_logger = logging.getLogger(__name__)


ERROR_MESSAGE = _("There is an issue with module synchronization")


class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    @api.model
    def _get_installed_module_info(self):
        modules = self.search([("state", "in", ("installed", "to upgrade"))])
        info = {"version": release.version, "modules": []}
        for module in modules:
            # TODO get description from readme if any...
            modules_info = {
                "name": module.name,
                "shortdesc": module.shortdesc,
                "description": module.description_html,
                "author": module.author,
            }
            info["modules"].append(modules_info)
        return info

    # called by cron
    @api.model
    def push_installed_module_info(self):
        # get external instance for which we want to send the data
        api_key = self.env["ir.config_parameter"].sudo().get_param("module.api.key")
        api_url = self.env["ir.config_parameter"].sudo().get_param("module.api.url")
        if not api_key or not api_url:
            return
        module_info = self._get_installed_module_info()
        url = "{}/module-api/module/synchronize_installed_module_info".format(api_url)
        headers = {"API-KEY": api_key}
        try:
            res = requests.post(
                url, headers=headers, json={"modules_info": module_info}
            )
        except Exception as e:
            _logger.error("Error when calling odoo %s", e)
            raise UserError(ERROR_MESSAGE)
        data = res.json()
        if isinstance(data, dict) and data.get("code", 0) >= 400:
            _logger.error(
                "Error module sync API : %s : %s",
                data.get("name"),
                data.get("description"),
            )
            raise UserError(ERROR_MESSAGE)
        return data
