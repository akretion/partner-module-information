from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    target_odoo_version_id = fields.Many2one(
        "odoo.version",
        string="Target version",
    )
    migration_project_id = fields.Many2one(
        "project.project",
        string="Migration Project",
        domain="[('partner_id', '=', id)]",
    )
    migrated_module_nbr = fields.Integer(
        compute="_compute_migrated_module_nbr",
    )

    def _compute_migrated_module_nbr(self):
        for record in self:
            if record.target_odoo_version_id:
                record.migrated_module_nbr = self.env["module.partner"].search_count(
                    [
                        ("migration_status", "=", "done"),
                        ("partner_id", "=", record.id),
                    ]
                )
            else:
                record.migrated_module_nbr = 0

    def get_action_migration_tree(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "module.partner",
            "name": f"Migration {self.name}",
            "views": [],
            "view_mode": "tree,form",
            "domain": [["partner_id", "=", self.id]],
        }
