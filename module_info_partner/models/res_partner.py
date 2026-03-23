from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    module_auth_api_key_id = fields.Many2one("auth.api.key", string="Module API KEY")
    version_id = fields.Many2one("odoo.version", string="Current Odoo version")
    module_nbr = fields.Integer(compute="_compute_module_nbr")

    def get_action_module_information_tree(self):
        modules = self.env["module.partner"].search([("partner_id", "=", self.id)])
        modules = modules.mapped("module_id.id")
        return {
            "type": "ir.actions.act_window",
            "res_model": "module.information",
            "name": f"Modules used by {self.name}",
            "views": [],
            "view_mode": "list,form",
            "domain": [["id", "in", modules]],
        }

    def _compute_module_nbr(self):
        for record in self:
            record.module_nbr = self.env["module.partner"].search_count(
                [("partner_id", "=", record.id)]
            )
