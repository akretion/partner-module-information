import logging
import re
from datetime import datetime

import requests

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PullRequest(models.Model):
    _name = "pull.request"

    title = fields.Char(index=True, readonly=True)
    repo_id = fields.Many2one(
        "module.repo", string="Host Repository", index=True, readonly=True
    )
    date_open = fields.Datetime(string="Opening Date", readonly=True)
    date_updated = fields.Datetime(string="Date of Last Update", readonly=True)
    date_closed = fields.Datetime(string="Date of close", readonly=True)
    module_ids = fields.Many2many(
        "module.information", string="Related Modules", readonly=True
    )
    version_id = fields.Many2one("odoo.version", readonly=True, index=True)
    reviewer_ids = fields.Many2many("res.users")
    reviewer_count = fields.Integer(compute="_compute_reviewer_count", readonly=True)
    state = fields.Char(index=True, readonly=True)
    url = fields.Char(readonly=True)
    number = fields.Integer(index=True, string="Github number", readonly=True)
    author = fields.Char(index=True, readonly=True)
    orga = fields.Char(index=True, readonly=True)
    need_review = fields.Boolean(string="Review requested")
    reviewer_ids_nbr = fields.Integer(
        compute="_compute_reviewer_ids_nbr", readonly=True, store=True
    )
    author_user_id = fields.Many2one(
        "res.users", compute="_compute_author_user_id", store=True
    )

    _sql_constraints = [
        (
            "uniq_number_and_repo",
            "unique(number, repo_id)",
            "the pair pr number and repo must be unique",
        ),
    ]

    @api.depends("author")
    def _compute_author_user_id(self):
        for record in self:
            record.author_user_id = (
                self.env["res.users"]
                .search(
                    [("github_user", "=", record.author), ("github_user", "!=", False)]
                )
                .id
            )

    @api.depends("reviewer_ids")
    def _compute_reviewer_ids_nbr(self):
        for record in self:
            record.reviewer_ids_nbr = len(record.reviewer_ids)

    @api.depends("reviewer_ids")
    def _compute_reviewer_count(self):
        for record in self:
            record.reviewer_count = len(record.reviewer_ids)

    def _get_module_from_pr(self, url, modules):
        git_token = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("module.info.pull.request.git.token")
        )
        response = requests.get(
            url, headers={"authorization": f"Bearer {git_token}"}, timeout=10
        )
        matchs = re.findall(r"\+{3,5} b.*", response.text)
        module_ids = []
        for line in matchs:
            # regex get first /module/
            module_name = re.search(r"(?<=/)(\w*)(?=/)", line)
            if not module_name:
                continue
            module_name = module_name.group(0)
            module_id = modules.get(module_name)
            if module_id and module_id not in module_ids:
                module_ids.append(module_id)
        return module_ids

    def create_or_update_pr(self, pr, repo, modules_info, odoo_version):
        vals = {}
        pr_obj = self.search(
            [("number", "=", pr["number"]), ("repo_id", "=", repo[0].id)]
        )
        if pr_obj and pr_obj.state == "open":
            # Closed PR has no update
            # PR exist in bdd and is open

            vals.update(
                {
                    "date_updated": datetime.strptime(
                        pr["updated_at"], "%Y-%m-%dT%H:%M:%SZ"
                    ).strftime("%Y-%m-%d %H:%M:%S")
                }
            )
            if pr.get("closed_at", False):
                vals.update(
                    {
                        "date_closed": datetime.strptime(
                            pr["closed_at"], "%Y-%m-%dT%H:%M:%SZ"
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                        "state": pr["state"],
                    }
                )
            pr_obj.write(vals)
            pr_obj._update_module_version()

        elif not pr_obj and pr["state"] == "open":
            # PR not exist in bdd
            vals.update(
                {
                    "title": pr["title"],
                    "number": pr["number"],
                    "repo_id": repo[0].id,
                    "date_open": datetime.strptime(
                        pr["created_at"], "%Y-%m-%dT%H:%M:%SZ"
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    "module_ids": [
                        (6, 0, self._get_module_from_pr(pr["diff_url"], modules_info))
                    ],
                    "version_id": odoo_version.get(pr["base"]["ref"][:4], ""),
                    "state": pr["state"],
                    "url": pr["html_url"],
                    "author": pr["user"]["login"],
                    "orga": pr["head"]["user"]["login"],
                }
            )
            pr_obj = pr_obj.create(vals)
            pr_obj._update_module_version()

    def _update_module_version(self):
        # manage module version depending on PRs
        # If there is a PR, then make sure we have at least a pending module version
        # if a PR close, make sure to delete related pending version if not other PR
        # for this module and this version.
        self.ensure_one()
        if self.state == "open":
            for module in self.module_ids:
                module_version = self.env["module.version"].search(
                    [
                        ("module_id", "=", module.id),
                        ("version_id", "=", self.version_id.id),
                    ]
                )
                if not module_version:
                    self.env["module.version"].create(
                        {
                            "state": "pending",
                            "module_id": module.id,
                            "version_id": self.version_id.id,
                        }
                    )
        else:
            # PR is closed, if we have a pending module version, we should unlink it
            # if there is no other PR
            module_versions = self.env["module.version"].search(
                [
                    ("module_id", "=", self.module_ids.ids),
                    ("version_id", "=", self.version_id.id),
                    ("state", "=", "pending"),
                ]
            )
            to_unlink = self.env["module.version"]
            for module_version in module_versions:
                other_pr = self.search(
                    [
                        ("module_ids", "=", module_version.module_id.id),
                        ("version_id", "=", module_version.version_id.id),
                        ("state", "=", "open"),
                    ]
                )
                if not other_pr:
                    to_unlink |= module_version
            to_unlink.unlink()

    def open_url(self):
        return {
            "type": "ir.actions.act_url",
            "target": "new",
            "url": self.url,
        }
