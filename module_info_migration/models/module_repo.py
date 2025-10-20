# Copyright 2025 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ModuleRepo(models.Model):
    _inherit = "module.repo"

    missing_pr_ids = fields.One2many("missing.pull.request", "repo_id", "Missing Pr")
