import re

from odoo import api, fields, models


class ModuleRepo(models.Model):
    _name = "module.repo"
    _rec_name = "name"
    _description = "List of all module repository"

    name = fields.Char(string="Repository Name", index=True)
    organization = fields.Char(string="Organization Name")
    url = fields.Char()
    module_ids = fields.One2many(
        "module.information", "repo_id", string="Module information"
    )
    module_nbr = fields.Integer(compute="_compute_module_nbr", string="# of Modules")

    _sql_constraints = [
        (
            "uniq_orga_repo",
            "unique(name, organization)",
            "the pair repo name and organization must be unique",
        )
    ]

    @api.depends("module_ids")
    def _compute_module_nbr(self):
        for record in self:
            record.module_nbr = len(record.module_ids)

    def _get_or_create_repo_from_url(self, url):
        url = url.lower()
        match = re.match(r"https?://[^/]+/([^/]+)/([^/]+)", url)
        if match:
            orga_name, repo_name = match.groups()
            repo = self.env["module.repo"].search(
                [("name", "=", repo_name), ("organization", "=", orga_name)]
            )
            if not repo:
                repo = self.env["module.repo"].create(
                    {
                        "name": repo_name,
                        "organization": orga_name,
                        "url": url,
                    }
                )
        else:
            repo = self.env["module.repo"]
        return repo
