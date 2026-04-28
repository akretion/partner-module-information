# Copyright 2026  Akretion (https://www.akretion.com).
# @author Sébastien Alix <sebastien.alix@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models
from odoo.osv import expression


class ResPartner(models.Model):
    _inherit = "res.partner"

    pull_request_nbr = fields.Integer(
        compute="_compute_pull_request_nbr",
    )

    def _compute_pull_request_nbr(self):
        for record in self:
            record.pull_request_nbr = 0
            if record.target_odoo_version_id:
                base_domain = record._get_pull_request_domain()
                open_domain = [("state", "not in", ["dead", "done"])]
                domain = expression.AND([base_domain, open_domain])
                record.pull_request_nbr = self.env["pull.request"].search_count(domain)

    def _get_pull_request_domain(self):
        self.ensure_one()
        return [
            ("partner_id", "=", self.id),
            ("version_id", "=", self.target_odoo_version_id.id),
        ]

    def get_action_pull_request_tree(self):
        self.ensure_one()
        name = f"Pull Requests {self.name}"
        if self.target_odoo_version_id:
            name = f"Pull Requests {self.target_odoo_version_id.name} {self.name}"
        ctx = dict(self.env.context)
        ctx["search_default_opened"] = True
        return {
            "type": "ir.actions.act_window",
            "res_model": "pull.request",
            "name": name,
            "views": [],
            "view_mode": "tree,form",
            "domain": self._get_pull_request_domain(),
            "context": ctx,
        }
