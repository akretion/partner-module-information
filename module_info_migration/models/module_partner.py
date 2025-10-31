from odoo import _, api, exceptions, fields, models


class ModulePartner(models.Model):
    _inherit = "module.partner"

    migration_status = fields.Selection(
        selection=[
            ("obsolete", "Obsolete"),
            ("ongoing_pr", "Ongoing"),
            ("done", "Done"),
        ],
        compute="_compute_migrated",
        store=True,
    )
    task_ids = fields.Many2many("project.task", string="tasks")

    @api.depends(
        "module_id.available_version_ids",
        "partner_id.target_odoo_version_id",
        "module_id.wip_version_ids",
        "module_id.obsolete_version_id",
        "task_ids.stage_id",
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
            if record.task_ids:
                if any(
                    [task.state not in ("done", "cancel") for task in record.task_ids]
                ):
                    record.migration_status = "ongoing_pr"
                else:
                    record.migration_status = "done"
            elif target_version in record.module_id.wip_version_ids:
                record.migration_status = "ongoing_pr"
            elif target_version.id in obsolete_version_ids:
                record.migration_status = "obsolete"
            elif target_version in record.module_id.available_version_ids:
                record.migration_status = "done"
            else:
                record.migration_status = False

    def open_pull_request(self):
        self.ensure_one()
        dest_module_version = self.env["module.version"].search(
            [
                ("version_id", "=", self.partner_id.target_odoo_version_id.id),
                ("url_pull_request", "!=", False),
                ("module_id", "=", self.module_id.id),
                ("state", "=", "pending"),
            ]
        )
        if not dest_module_version:
            raise exceptions.UserError(_("No known migration PR for this module."))
        client_action = {
            "type": "ir.actions.act_url",
            "name": "Migration PR",
            "target": "new",
            "url": dest_module_version.url_pull_request,
        }
        return client_action

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
