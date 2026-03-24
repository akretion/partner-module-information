from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    pr_id = fields.Many2one("pull.request", string="PR")
    name = fields.Char(
        compute="_compute_name",
        store=True,
        readonly=False,
    )

    #    def _timesheet_preprocess(self, vals):
    #        # _timesheet_preprocess need to have the task_id defined
    #        # and the compute is called after so we need to add the task_id here
    #        if vals.get("pr_id") and not vals.get("task_id"):
    #            pr = self.env["pull.request"].browse(vals["pr_id"])
    #            vals["task_id"] = pr.task_id.id
    #        return super()._timesheet_preprocess(vals)

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
