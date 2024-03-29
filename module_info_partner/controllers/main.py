# Copyright 2020 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _
from odoo.exceptions import AccessError
from odoo.http import request

from odoo.addons.base_rest.controllers import main

_logger = logging.getLogger(__name__)


class ExternalModuleController(main.RestController):
    _root_path = "/module-api/"
    _collection_name = "partner.module"
    _default_auth = "api_key"

    @classmethod
    def _get_partner_from_request(cls):
        auth_api_key_id = getattr(request, "auth_api_key_id", None)
        if auth_api_key_id:
            partner = request.env["res.partner"].search(
                [("module_auth_api_key_id", "=", auth_api_key_id)]
            )
            if partner:
                return partner
        raise AccessError(_("No partner match the API KEY"))

    def _get_component_context(self, collection):
        res = super(ExternalModuleController, self)._get_component_context(collection)
        res["partner"] = self._get_partner_from_request()
        return res
