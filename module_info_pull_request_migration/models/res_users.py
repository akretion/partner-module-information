# Copyright 2026  Akretion (https://www.akretion.com).
# @author Sébastien Alix <sebastien.alix@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models
from odoo.tools import groupby


class ResUsers(models.Model):
    _inherit = "res.users"

    def _get_pull_requests_authored_by_project(self, states=None, migration_only=False):
        """Return the Pull Requests in progress authored by current user.

        Result can be filtered with `states` and `migration_only` parameters.
        """
        domain = self._get_pull_requests_authored_domain(states=states)
        prs = self.env["pull.request"].search(domain)
        if migration_only:
            prs = prs._filter_on_project_target_odoo_version()
        # NOTE: Convert defaultdict to dict so mail template doesn't crash.
        return dict(groupby(prs, key=lambda pr: pr.project_id))

    def _get_pull_requests_for_first_review_by_project(
        self, states=None, migration_only=False
    ):
        """Return the Pull Requests to review by current user.

        Result can be filtered with `states` and `migration_only` parameters.
        """
        domain = self._get_pull_requests_for_first_review_domain(states=states)
        prs = self.env["pull.request"].search(domain)
        if migration_only:
            prs = prs._filter_on_project_target_odoo_version()
        # Convert defaultdict to dict so usage in mail template doesn't crash.
        return dict(groupby(prs, key=lambda pr: pr.project_id))

    def _get_pull_requests_for_second_review_by_project(
        self, states=None, migration_only=False
    ):
        """Return the Pull Requests to check and merge by current user.

        Result can be filtered with `states` and `migration_only` parameters.
        """
        domain = self._get_pull_requests_for_second_review_domain(states=states)
        prs = self.env["pull.request"].search(domain)
        if migration_only:
            prs = prs._filter_on_project_target_odoo_version()
        # Convert defaultdict to dict so usage in mail template doesn't crash.
        return dict(groupby(prs, key=lambda pr: pr.project_id))

    @api.model
    def cron_email_pull_requests_migration_digest(self):
        """Cron task sending pull requests migration digest by e-mail."""
        users = self.env["res.users"].search([])
        for user in users:
            if (
                user._get_pull_requests_authored_by_project(
                    states=("draft", "need_fix", "cancel"),
                    migration_only=True,
                )
                or user._get_pull_requests_for_first_review_by_project(
                    migration_only=True
                )
                or user._get_pull_requests_for_second_review_by_project(
                    migration_only=True
                )
            ):
                user._send_email_pull_requests_migration_digest()
        return True

    def _send_email_pull_requests_migration_digest(self):
        """Send pull requests migration digest by e-mail to current user."""
        self.ensure_one()
        template = self.env.ref(
            "module_info_pull_request_migration."
            "mail_template_pull_requests_migration_digest"
        )
        return template.send_mail(self.id)
