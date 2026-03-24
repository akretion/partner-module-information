from odoo import api, fields, models


class ModuleInformation(models.Model):
    _inherit = "module.information"

    pr_ids = fields.Many2many("pull.request", string="Active Pull Request")
    pr_nbr = fields.Integer(
        compute="_compute_pr_nbr", store=True, string="# of Modules"
    )

    @api.depends("pr_ids")
    def _compute_pr_nbr(self):
        for record in self:
            record.pr_nbr = len(record.pr_ids)

    def action_view_pull_request(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": ("Pull Request"),
            "res_model": "pull.request",
            "view_mode": "list,form",
            "domain": [("module_ids", "=", self.id)],
        }
