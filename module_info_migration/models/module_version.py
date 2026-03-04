# Copyright 2025 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ModuleVersion(models.Model):
    _inherit = "module.version"

    missing_pr_ids = fields.Many2many(
        comodel_name="missing.pull.request",
        string="Missing Pr",
        compute="_compute_missing_pr_ids",
    )

    @api.depends(
        "module_id.pr_ids.missing_pr_ids",
    )
    def _compute_missing_pr_ids(self):
        for record in self:
            record.missing_pr_ids = record.module_id.pr_ids.missing_pr_ids.filtered(
                lambda s, record=record: s.src_version_id == record.version_id
            )

    def _update_migration_hook(self):
        res = super()._update_migration_hook()
        if self.migrations:
            for migration in self.migrations:
                if migration["process"] == "port_commits":
                    target_version_id = self.env["odoo.version"]._get_id(
                        migration["target_branch"]
                    )
                    for pr_number, pr_info in migration["results"].items():
                        try:
                            pr_number = int(pr_number)
                        except Exception:
                            _logger.warning("Pr is missing, ignore %s" % pr_info)
                            continue
                        repo = self.module_id.repo_id
                        pr = self.env["pull.request"].search(
                            [
                                ("repo_id", "=", repo.id),
                                ("number", "=", pr_number),
                            ]
                        )
                        if not pr:
                            pr = repo.import_pr_number(pr_number)
                        miss = self.env["missing.pull.request"].search(
                            [
                                ("repo_id", "=", repo.id),
                                ("pr_id", "=", pr.id),
                                ("target_version_id", "=", target_version_id),
                            ]
                        )
                        if not miss:
                            miss = self.env["missing.pull.request"].create(
                                {
                                    "repo_id": repo.id,
                                    "pr_id": pr.id,
                                    "target_version_id": target_version_id,
                                    "missing_commits": "\n".join(
                                        pr_info["missing_commits"]
                                    ),
                                }
                            )
        return res
