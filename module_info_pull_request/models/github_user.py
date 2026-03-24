# Copyright 2025 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, tools


class GithubUser(models.Model):
    _name = "github.user"
    _description = "Github Users"

    name = fields.Char(readonly=True)
    login = fields.Char(readonly=True)
    company = fields.Char(readonly=True)
    github_ext_id = fields.Integer(readonly=True)
    user_id = fields.Many2one("res.users", "User")

    @tools.ormcache("github_ext_id")
    def _get_from_ext_id(self, github_ext_id):
        return self.search([("github_ext_id", "=", github_ext_id)]).id

    def _get_or_create(self, gh_user):
        if gh_user:
            user_id = self._get_from_ext_id(gh_user.id)
            if user_id:
                return self.browse(user_id)
            else:
                return self.create(
                    {
                        "name": gh_user.name or gh_user.login,
                        "company": gh_user.company,
                        "login": gh_user.login,
                        "github_ext_id": gh_user.id,
                    }
                )
        else:
            # If there is not user this mean that the user have been deleted
            # github replace this "deleted" user in the website with the ghost user
            # but in the API it's not replaced, the gh_user is None
            return self.env.ref("module_info_pull_request.ghost_user")

    @api.model_create_multi
    def create(self, vals_list):
        self.env.registry.clear_cache()
        return super().create(vals_list)

    def write(self, vals):
        self.env.registry.clear_cache()
        return super().write(vals)
