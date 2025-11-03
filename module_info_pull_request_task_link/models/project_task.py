# Copyright 2025 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    pr_ids = fields.One2many("pull.request", "task_id", "Pull Request")
