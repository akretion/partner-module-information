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

    def _clear_get_version_cache(self):
        self._get_id.clear_cache(self.env[self._name])

    @api.model
    def create(self, vals):
        self._clear_get_version_cache()
        return super().create(vals)

    def write(self, vals):
        self._clear_get_version_cache()
        return super().write(vals)
