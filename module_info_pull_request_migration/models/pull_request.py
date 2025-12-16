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
