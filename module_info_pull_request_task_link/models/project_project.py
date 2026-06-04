# Copyright 2025 Akretion (https://www.akretion.com).
# @author Sébastien Alix <sebastien.alix@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    internal_second_reviewer_ids = fields.Many2many(
        comodel_name="res.users",
        relation="project_project_internal_second_reviewer_rel",
        column1="project_project_id",
        column2="internal_second_reviewer_id",
        string="Internal Second Reviewers",
        help=(
            "Second reviewers are those approving for good PRs,"
            " and possibly merging them."
        ),
    )
