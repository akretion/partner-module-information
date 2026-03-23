from odoo import api, fields, models, tools


class OdooVersion(models.Model):
    _name = "odoo.version"
    _rec_name = "name"
    _description = "Odoo Version"

    name = fields.Char()

    _sql_constraints = [("name_uniq", "unique(name)", "Name must be unique.")]

    @tools.ormcache("name")
    def _get_id(self, name):
        return self.env["odoo.version"].search([("name", "=", name)]).id

    @api.model_create_multi
    def create(self, vals_list):
        self.env.registry.clear_cache()
        return super().create(vals_list)

    def write(self, vals):
        self.env.registry.clear_cache()
        return super().write(vals)
