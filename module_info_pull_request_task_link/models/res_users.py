# Copyright 2026  Akretion (https://www.akretion.com).
# @author Sébastien Alix <sebastien.alix@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models
from odoo.osv import expression


class ResUsers(models.Model):
    _inherit = "res.users"

    def _get_pull_requests_authored_domain(self, states=None):
        if not states:
            states = (
                "draft",
                "need_fix",
                "cancel",
                "waiting_review",
                "need_reviewer",
                "approved_internal",
                "approved",
            )
        base_domain = [
            ("state", "in", states),
            ("project_id", "!=", False),
        ]
        user_domain = [("author_user_id", "in", self.ids)]
        return expression.AND([base_domain, user_domain])

    def _get_pull_requests_for_first_review_domain(self, states=None):
        if not states:
            states = ("waiting_review",)
        base_domain = [
            ("state", "in", states),
            ("project_id", "!=", False),
        ]
        user_domain = [
            ("author_user_id", "not in", self.ids),
            ("internal_first_reviewer_ids", "in", self.ids),
        ]
        return expression.AND([base_domain, user_domain])

    def _get_pull_requests_for_second_review_domain(self, states=None):
        if not states:
            states = ("need_reviewer", "approved_internal", "approved")
        base_domain = [
            ("state", "in", states),
            ("project_id", "!=", False),
        ]
        internal_reviewers = self.search([("github_user_ids", "!=", False)])
        approval_domain = expression.OR(
            [
                [("state", "=", "approved")],
                [
                    (
                        "approved_reviewer_ids",
                        "in",
                        internal_reviewers.github_user_ids.ids,
                    )
                ],
            ]
        )
        user_domain = [
            ("author_user_id", "not in", self.ids),
            ("internal_second_reviewer_ids", "in", self.ids),
        ]
        return expression.AND([base_domain, approval_domain, user_domain])
