import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


HTML_TEMPLATE = """
<table border="1" cellpadding="8" cellspacing="0" width="100%">
  <thead>
    <tr style="border:1px solid black;">
      <th style="border:1px solid black;">id</th>
      <th style="border:1px solid black;">url</th>
      <th style="border:1px solid black;">author</th>
      <th style="border:1px solid black;">title</th>
      <th style="border:1px solid black;">missing_commit</th>
    </tr>
  </thead>
  <tbody>
    {rows}
  </tbody>
</table>
"""

ROW_TEMPLATE = """
    <tr>
      <td style="border:1px solid black;">{id}</td>
      <td style="border:1px solid black;"><a href="{url}">{url}</a></td>
      <td style="border:1px solid black;">{author}</td>
      <td style="border:1px solid black;">{title}</td>
      <td style="border:1px solid black;">{missing_commits}</td>
    </tr>
"""


class ModulePartner(models.Model):
    _inherit = "module.partner"

    migration_status = fields.Selection(
        selection=[
            ("obsolete", "Obsolete"),
            ("todo", "Todo"),
            ("planned", "Planned"),
            ("ongoing_pr", "Ongoing"),
            ("port_commits", "Ported (missing commit)"),
            ("done", "Done"),
        ],
        compute="_compute_migrated",
        store=True,
    )
    task_ids = fields.Many2many(
        "project.task",
        string="Tasks",
        readonly=True,
    )

    missing_commit = fields.Json(
        compute="_compute_missing_commit",
        store=True,
    )
    missing_commit_html = fields.Html(
        compute="_compute_missing_commit_html",
    )
    missing_pr_ids = fields.Many2many(
        comodel_name="missing.pull.request",
        string="Missing Pr",
        compute="_compute_missing_pr_ids",
    )

    @api.depends("module_version_id.missing_pr_ids")
    def _compute_missing_pr_ids(self):
        for record in self:
            record.missing_pr_ids = record.module_version_id.missing_pr_ids.filtered(
                lambda s, record=record: s.target_version_id
                == record.partner_id.target_odoo_version_id
            )

    @api.depends("module_version_id.migrations")
    def _compute_missing_commit(self):
        for record in self:
            migration = record._get_migration_data()
            if migration:
                record.missing_commit = migration["results"]
            else:
                record.missing_commit = []

    @api.depends("module_version_id.migrations")
    def _compute_missing_commit_html(self):
        for record in self:
            rows = []
            if record.missing_commit:
                for pr_id, pr_info in record.missing_commit.items():
                    if not pr_id:
                        rows.append(
                            ROW_TEMPLATE.format(
                                id=pr_id,
                                url=pr_info["url"],
                                author=pr_info["author"],
                                title=pr_info["title"],
                                missing_commits="<br>".join(pr_info["missing_commits"]),
                            )
                        )
            if rows:
                record.missing_commit_html = HTML_TEMPLATE.format(rows="\n".join(rows))
            else:
                record.missing_commit_html = ""

    def _get_migration_data(self):
        migrations = self.module_version_id.migrations or []
        target_version = self.partner_id.target_odoo_version_id
        for migration in migrations:
            if (
                migration["target_branch"] == target_version.name
                and migration["process"] == "port_commits"
            ):
                return migration
        return None

    @api.depends(
        "module_id.available_version_ids",
        "partner_id.target_odoo_version_id",
        "module_id.wip_version_ids",
        "module_id.obsolete_version_id",
        "task_ids.stage_id",
        "missing_commit",
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
                if record.missing_commit:
                    record.migration_status = "port_commits"
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
