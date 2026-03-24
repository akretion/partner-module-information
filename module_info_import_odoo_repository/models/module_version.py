# Copyright 2025 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ModuleVersion(models.Model):
    _inherit = "module.version"

    migrations = fields.Json(help="Migration information from odoo repository")

    def _update_migration_hook(self):
        """Hook that can do extra processing after updating the migrations fields"""
        self.ensure_one()
