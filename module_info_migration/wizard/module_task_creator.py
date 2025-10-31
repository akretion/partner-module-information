from odoo import _, exceptions, fields, models


class ModuleInformation(models.TransientModel):
    _name = "module.task.creator"
    _description = "Wizard to create task in mass from the module of a partner"

    def _get_default_partner(self):
        modules = self.env["module.partner"].browse(self.env.context.get("active_ids"))
        partners = modules.mapped("partner_id")
        if len(partners) > 1:
            raise exceptions.UserError(
                _("You should create task for one partner at a time")
            )
        return partners

    prefix_task_name = fields.Char()
    project_id = fields.Many2one("project.project", required=True)
    partner_id = fields.Many2one(
        "res.partner", required=True, default=_get_default_partner
    )

    def validate(self):
        module_partner_ids = self.env.context.get("active_ids")
        modules = self.env["module.partner"].browse(module_partner_ids)
        prefix = self.prefix_task_name or ""
        for module in modules:
            task_vals = {
                "project_id": self.project_id.id,
                "name": f"{prefix}{module.module_id.name}",
                "module_partner_ids": [(6, 0, [module.id])],
            }
            self.env["project.task"].create(task_vals)
