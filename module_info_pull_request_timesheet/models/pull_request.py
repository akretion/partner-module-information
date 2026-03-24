import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class PullRequest(models.Model):
    _inherit = "pull.request"

    allow_timesheets = fields.Boolean(
        related="project_id.allow_timesheets", string="Allow Timesheets"
    )
    timesheet_ids = fields.One2many("account.analytic.line", "pr_id", "Timesheets")
