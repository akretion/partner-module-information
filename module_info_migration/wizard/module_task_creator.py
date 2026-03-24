from odoo import exceptions, fields, models
from odoo.exceptions import UserError


class ModuleInformation(models.TransientModel):
    _name = "module.task.creator"
    _description = "Wizard to create task in mass from the module of a partner"

    def _get_default_partner(self):
        modules = self.env["module.partner"].browse(self.env.context.get("active_ids"))
        partners = modules.mapped("partner_id")
        if len(partners) > 1:
            raise exceptions.UserError(
                self.env._("You should create task for one partner at a time")
            )
        return partners

    task_name = fields.Char()
    project_id = fields.Many2one(
        "project.project", related="partner_id.migration_project_id", required=True
    )
    partner_id = fields.Many2one(
        "res.partner", required=True, default=_get_default_partner
    )

    def validate(self):
        module_partner_ids = self.env.context.get("active_ids")
        module_partners = self.env["module.partner"].browse(module_partner_ids)
        if module_partners.task_ids:
            raise UserError(self.env._("Some module already have a task"))
        task_vals = {
            "project_id": self.project_id.id,
            "name": self.task_name,
            "module_partner_ids": [(6, 0, module_partner_ids)],
        }
        self.env["project.task"].create(task_vals)
