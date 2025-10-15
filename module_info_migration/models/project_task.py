from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    module_partner_ids = fields.Many2many(
        "module.partner", string="Modules", domain="[('partner_id', '=', partner_id)]"
    )
    is_migration_project = fields.Boolean(
        related="project_id.is_migration_project",
    )
