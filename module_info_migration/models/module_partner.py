from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ModulePartner(models.Model):
    _inherit = "module.partner"

    migration_status = fields.Selection(
        selection=[
            ("obsolete", "Obsolete"),
            ("planned", "Planned"),
            ("todo", "Todo"),
            ("ongoing_pr", "Ongoing"),
            ("port_commits", "Ported (missing commit)"),
            ("done", "Done"),
        ],
        compute="_compute_migrated",
        store=True,
    )
    task_ids = fields.Many2many("project.task", string="Tasks")

    @api.depends(
        "module_id.available_version_ids",
        "partner_id.target_odoo_version_id",
        "module_id.wip_version_ids",
        "module_id.obsolete_version_id",
        "task_ids.stage_id",
        "module_version_id.migrations",
    )
    def _compute_migrated(self):
        versions = self.env["odoo.version"].search([])
        for record in self:
            target_version = record.partner_id.target_odoo_version_id
            if not target_version:
                record.migration_status = False
                continue
            if record.module_id.obsolete_version_id:
                obsolete_version_ids = versions.filtered(
                    lambda v: float(v.name)
                    >= float(record.module_id.obsolete_version_id.name)  # noqa: B023
                ).ids
            else:
                obsolete_version_ids = []

            if target_version in record.module_id.wip_version_ids:
                record.migration_status = "ongoing_pr"
            elif target_version.id in obsolete_version_ids:
                record.migration_status = "obsolete"
            elif target_version in record.module_id.available_version_ids:
                migrations = record.module_version_id.migrations or []
                for migration in migrations:
                    if (
                        migration["target_branch"] == target_version.name
                        and migration["process"] == "port_commits"
                    ):
                        record.migration_status = "port_commits"
                        break
                else:
                    record.migration_status = "done"
            elif record.task_ids:
                record.migration_status = "planned"
            else:
                record.migration_status = "todo"

    def open_pull_request(self):
        self.ensure_one()
        pulls = self.env["pull.request"].search(
            [
                ("module_ids", "=", self.module_id.id),
                ("version_id", "=", self.partner_id.target_odoo_version_id.id),
            ]
        )
        if len(pulls) == 0:
            raise UserError(_("No known migration PR for this module."))
        elif len(pulls) > 1:
            raise UserError(
                _("Several Pull are open \n: %s")
                % "\n- ".join([pull.url for pull in pulls])
            )
        else:
            return {
                "type": "ir.actions.act_url",
                "name": "Migration PR",
                "target": "new",
                "url": pulls.url,
            }

    def open_task(self):
        tasks = self.task_ids
        action = self.env["ir.actions.actions"]._for_xml_id("project.action_view_task")
        if len(tasks) > 1:
            action["domain"] = [("id", "in", tasks.ids)]
        elif len(tasks) == 1:
            form_view = [(self.env.ref("project.view_task_form2").id, "form")]
            if "views" in action:
                action["views"] = form_view + [
                    (state, view) for state, view in action["views"] if view != "form"
                ]
            else:
                action["views"] = form_view
            action["res_id"] = tasks.id
        else:
            action = {"type": "ir.actions.act_window_close"}

        context = {}
        if len(self) == 1:
            context.update(
                {
                    "default_project_id": tasks.project_id.id,
                }
            )
        action["context"] = context
        return action
