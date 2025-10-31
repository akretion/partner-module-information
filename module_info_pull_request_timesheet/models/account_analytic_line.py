from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    pr_id = fields.Many2one(
        comodel_name="pull.request",
        string="PR",
        compute="_compute_pr_id",
        store=True,
        readonly=False,
    )

    @api.depends("pr_id")
    def _compute_pr_id(self):
        res = super()._compute_task_id()
        for record in self:
            if record.pr_id:
                record.task_id = record.pr_id.task_id.id
        return res

    # Use compute readonly field do not work
    # TODO retry in v16
    @api.onchange("name")
    def _onchange_name(self):
        for record in self:
            if record.pr_id:
                record.name = (
                    "Review PR " f"{','.join(record.pr_id.module_ids.mapped('name'))}"
                )
