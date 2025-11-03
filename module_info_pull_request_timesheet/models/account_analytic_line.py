from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    pr_id = fields.Many2one("pull.request", string="PR")
    name = fields.Char(
        compute="_compute_name",
        store=True,
        readonly=False,
    )

    @api.depends("pr_id")
    def _compute_task_id(self):
        res = super()._compute_task_id()
        for record in self:
            if record.pr_id:
                record.task_id = record.pr_id.task_id
        return res

    @api.depends("pr_id")
    def _compute_name(self):
        for record in self:
            if record.pr_id:
                record.name = (
                    "Review PR " f"{','.join(record.pr_id.module_ids.mapped('name'))}"
                )
