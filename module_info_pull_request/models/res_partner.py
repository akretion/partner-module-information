from odoo import fields, models
from odoo.osv import expression

OPEN_PR = [("state", "not in", ("done", "cancel"))]


class ResPartner(models.Model):
    _inherit = "res.partner"

    current_pr_nbr = fields.Integer(compute="_compute_current_pr_nbr")
    higher_pr_nbr = fields.Integer(compute="_compute_higher_pr_nbr")

    def _get_domain_current_pr(self):
        return [
            ("module_ids.module_partner_ids.partner_id", "=", self.id),
            ("version_id", "=", self.version_id.id),
        ]

    def _get_domain_higher_pr(self):
        return [
            ("module_ids.module_partner_ids.partner_id", "=", self.id),
            ("version_id", ">", self.version_id.id),
        ]

    def _compute_current_pr_nbr(self):
        for record in self:
            record.current_pr_nbr = self.env["pull.request"].search_count(
                expression.AND([record._get_domain_current_pr(), OPEN_PR])
            )

    def _compute_higher_pr_nbr(self):
        for record in self:
            record.higher_pr_nbr = self.env["pull.request"].search_count(
                expression.AND([record._get_domain_higher_pr(), OPEN_PR])
            )

    def _get_action_pr(self, name, domain):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "module_info_pull_request.pull_request_action"
        )
        action.update({"name": name, "domain": domain})
        return action

    def get_action_pr_tree_current(self):
        return self._get_action_pr(
            f"Current Pull Request for {self.name}", self._get_domain_current_pr()
        )

    def get_action_pr_tree_higher(self):
        return self._get_action_pr(
            f"Higher version Pull Request for {self.name}",
            self._get_domain_higher_pr(),
        )
