import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PullRequest(models.Model):
    _inherit = "pull.request"

    project_id = fields.Many2one(
        "project.project",
        "Project",
        compute="_compute_project_id",
        store=True,
        readonly=False,
        index=True,
    )
    task_id = fields.Many2one(
        "project.task",
        "Task",
        compute="_compute_task_id",
        store=True,
        readonly=False,
        index=True,
        domain="[('project_id', '=?', project_id)]",
    )
    internal_reviewer_ids = fields.Many2many(
        "res.users",
        compute="_compute_internal_reviewer_ids",
        string="Internal Reviewer",
        store=True,
        readonly=False,
        help=(
            "On github you may not have the access right to request a review."
            "Here you can define an internal reviewer, so this person can do a"
            "review"
        ),
    )

    all_waiting_reviewer_ids = fields.Many2many(
        "github.user",
        compute="_compute_all_waiting_reviewer_ids",
        relation="github_user_pull_request_all_waiting_rel",
        readonly=True,
        store=True,
        help="This include internal reviewer + github reviewer",
    )
    partner_id = fields.Many2one(
        # Override field from 'module_info_pull_request'
        related="project_id.partner_id",
        store=True,
    )

    @api.depends(
        "waiting_reviewer_ids",
        "approved_reviewer_ids",
        "refused_reviewer_ids",
        "internal_reviewer_ids",
    )
    def _compute_all_waiting_reviewer_ids(self):
        for record in self:
            waiting_internal = record.internal_reviewer_ids.github_user_ids
            waiting_internal -= (
                record.approved_reviewer_ids + record.refused_reviewer_ids
            )
            record.all_waiting_reviewer_ids = (
                waiting_internal + record.waiting_reviewer_ids
            )

    @api.depends("task_id.reviewer_ids")
    def _compute_internal_reviewer_ids(self):
        for record in self:
            record.internal_reviewer_ids = record.task_id.reviewer_ids

    @api.depends("task_id")
    def _compute_project_id(self):
        for line in self:
            if line.task_id and not line.project_id:
                line.project_id = line.task_id.project_id

    @api.depends("project_id")
    def _compute_task_id(self):
        for line in self:
            if line.project_id != line.task_id.project_id:
                line.task_id = False

    def _update_state(self):
        res = super()._update_state()
        for record in self:
            if record.state == "need_reviewer" and record.internal_reviewer_ids:
                record.state = "waiting_review"
        return res
