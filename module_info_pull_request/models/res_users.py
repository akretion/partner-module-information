from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    github_user = fields.Char()
    github_user_ids = fields.One2many("github.user", "user_id", "Github Users")
