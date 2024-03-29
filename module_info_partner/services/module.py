# Copyright 2020 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class ExternalTaskService(Component):
    _inherit = "base.rest.service"
    _name = "external.module.service"
    _collection = "partner.module"
    _usage = "module"

    @property
    def partner(self):
        return self.work.partner

    def _validator_synchronize_installed_module_info(self):
        return {"modules_info": {"type": "dict"}, "context": {"type": "dict"}}

    def synchronize_installed_module_info(self, modules_info):
        version = modules_info.get("version")
        module_partner_obj = self.env["module.partner"]
        partner_modules = self.env["module.partner"]
        for module_info in modules_info.get("modules", []):
            partner_modules |= module_partner_obj.update_or_create(
                self.partner, version, module_info
            )

        # delete modules not used anymore by partner
        obsolete_partner_modules = module_partner_obj.search(
            [
                ("partner_id", "=", self.partner.id),
                ("id", "not in", partner_modules.ids),
            ]
        )
        obsolete_partner_modules.unlink()
        return
