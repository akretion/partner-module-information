# Copyright 2025 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    is_migration_project = fields.Boolean(
        compute="_compute_is_migration_project",
        store=True,
    )

    @api.depends("partner_id.migration_project_id")
    def _compute_is_migration_project(self):
        for record in self:
            record.is_migration_project = (
                record == record.partner_id.migration_project_id
            )
