import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ModulePartner(models.Model):
    _name = "module.partner"
    _description = "Modules used by partner"

    partner_id = fields.Many2one(
        "res.partner", required=True, index=True, string="Partner", ondelete="cascade"
    )
    version_id = fields.Many2one(
        "odoo.version",
        string="Version",
        required=True,
        index=True,
        ondelete="cascade",
    )
    module_id = fields.Many2one(
        "module.information",
        required=True,
        index=True,
        string="Module",
        ondelete="cascade",
    )
    repo_id = fields.Many2one(
        related="module_id.repo_id",
        store=True,
    )
    organization = fields.Char(
        related="repo_id.organization",
        store=True,
    )

    @api.model
    def _prepare_module_info_vals(self, module_info, partner):
        vals = {
            "name": module_info.get("name"),
            "shortdesc": module_info.get("shortdesc"),
            "description": module_info.get("description"),
            "authors": module_info.get("author"),
        }
        if module_info["is_custom"]:
            vals["partner_id"] = partner.id
        return vals

    @api.model
    def _prepare_partner_module_vals(self, partner, version, module, module_info):
        return {
            "partner_id": partner.id,
            "version_id": version.id,
            "module_id": module.id,
        }

    @api.model
    def update_or_create(self, partner, version_num, module_info):
        # check if module already exists
        module_info_obj = self.env["module.information"]

        partner_id = partner.id if module_info["is_custom"] else False
        module = module_info_obj.search(
            [
                ("name", "=", module_info["name"]),
                ("partner_id", "=", partner_id),
            ]
        )
        if not module:
            # in this case, Module is custom
            # create it with the customer partner_id
            module = module_info_obj.create(
                self._prepare_module_info_vals(module_info, partner)
            )
        version = self.env["odoo.version"].search([("name", "=", version_num)])
        partner_module_vals = self._prepare_partner_module_vals(
            partner, version, module, module_info
        )
        partner_module = self.search(
            [
                ("partner_id", "=", partner.id),
                ("module_id", "=", module.id),
                ("version_id", "=", version.id),
            ]
        )
        if partner_module:
            partner_module.write(partner_module_vals)
        else:
            partner_module = self.create(partner_module_vals)

        # if module is not listed in module.version, we create it.
        # if we use the module to synchronize module_information from
        # github_connector_odoo, we should rarely create any module.version
        # from here except for custom modules.

        # we can't know if it is merged or in PR, let's consider it in PR (pending)
        # it will be updated by synchro with github_connector_odoo (if
        # used) or manually
        module_version = self.env["module.version"].search(
            [("module_id", "=", module.id), ("version_id", "=", version.id)]
        )
        if not module_version:
            self.env["module.version"].create(
                {"module_id": module.id, "version_id": version.id, "state": "pending"}
            )
        return partner_module
