# Copyright 2025 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import models


class PullRequest(models.Model):
    _inherit = "pull.request"

    def _post_update(self):
        res = super()._post_update()
        self._link_to_migration_task()
        return res

    def _link_to_migration_task(self):
        for record in self:
            if not record.task_id:
                migrated_modules = record.module_ids.filtered(
                    lambda s, vrs=record.version_id: vrs not in s.available_version_ids
                )
                task = self.env["project.task"].search(
                    [
                        (
                            "project_id.partner_id.target_odoo_version_id",
                            "=",
                            record.version_id.id,
                        ),
                        ("project_id.is_migration_project", "=", True),
                        ("module_partner_ids.module_id", "in", migrated_modules.ids),
                    ],
                    order="create_date desc",
                    limit=1,
                )
                record.task_id = task

    def _filter_on_project_target_odoo_version(self):
        return self.filtered(
            lambda pr: pr.project_id.partner_id.target_odoo_version_id == pr.version_id
        )

    def _generate_template_notes(self, digest_type, user):
        self.ensure_one()
        method_name = f"_generate_template_{digest_type}_notes"
        return getattr(self, method_name)(user)

    def _generate_template_author_notes(self, user):
        self.ensure_one()
        if self.state == "waiting_review":
            reviewers = ", ".join(
                self.waiting_for_first_reviewers.mapped("display_name")
            )
            return f"Waiting for the review of your teammate(s): {reviewers}"
        return ""

    def _generate_template_author_approved_notes(self, user):
        self.ensure_one()
        # TODO: PR could be approved but still has one last comment from someone
        # else to address, or approved and waiting to be merge by the second reviewer
        return ""

    def _generate_template_first_reviewer_notes(self, user):
        self.ensure_one()
        waiting_for_user = self.waiting_for_first_reviewers & user.github_user_ids
        waiting_for_first_reviewers = (
            self.waiting_for_first_reviewers - user.github_user_ids
        )
        waiting_for_second_reviewers = (
            self.waiting_for_second_reviewers - user.github_user_ids
        )
        res = ""
        if waiting_for_user:
            res = """
                Waiting for your review
            """
        elif waiting_for_first_reviewers:
            reviewers = ", ".join(waiting_for_first_reviewers.mapped("display_name"))
            res = f"""
                Waiting for the review of your teammate(s):
                {reviewers}
            """
        elif waiting_for_second_reviewers:
            reviewers = ", ".join(waiting_for_second_reviewers.mapped("display_name"))
            res = f"""
                Waiting for the validation of your teammate(s):
                {reviewers}
            """
        return res

    def _generate_template_second_reviewer_notes(self, user):
        self.ensure_one()
        if self.approved_internal_reviewer_ids:
            reviewers = ", ".join(
                self.approved_internal_reviewer_ids.mapped("display_name")
            )
            return f"""
                Approved by: {reviewers}
            """
        return ""
