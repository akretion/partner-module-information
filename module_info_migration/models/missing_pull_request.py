# Copyright 2025 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MissingPullRequest(models.Model):
    _name = "missing.pull.request"
    _description = "Missing Pull Request"
    _order = "repo_id, src_version_id, target_version_id, pr_id"

    pr_id = fields.Many2one(
        "pull.request",
        "Pr",
        readonly=True,
        index=True,
    )
    title = fields.Char(related="pr_id.title")
    url = fields.Char(related="pr_id.url")
    organization = fields.Char(
        related="repo_id.organization",
        store=True,
        index=True,
    )
    repo_id = fields.Many2one(
        "module.repo",
        "Repo",
        related="pr_id.repo_id",
        store=True,
        readonly=True,
        index=True,
    )
    state = fields.Selection(
        [
            ("to_analyse", "To Analyse"),
            ("todo", "Todo"),
            ("ignore", "Drop this code"),
            ("useless", "Useless linting"),
        ],
        default="to_analyse",
        index=True,
    )
    module_ids = fields.Many2many(
        comodel_name="module.module",
        string="Module",
        related="pr_id.module_ids",
        index=True,
    )
    src_version_id = fields.Many2one(
        "odoo.version",
        "Src Version",
        related="pr_id.version_id",
        store=True,
        index=True,
    )
    target_version_id = fields.Many2one(
        "odoo.version",
        "Target Version",
        readonly=True,
        index=True,
    )
    missing_commits = fields.Text()

    def set_todo(self):
        self.state = "todo"

    def set_ignore(self):
        self.state = "ignore"

    def set_useless(self):
        self.state = "useless"

    def set_to_analyse(self):
        self.state = "to_analyse"
