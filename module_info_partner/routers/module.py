# Copyright 2016 Akretion (http://www.akretion.com)
# Benoit Guillot <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from typing import Annotated

############
from fastapi import APIRouter, Depends

from odoo import api

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)

from ..schemas.module import ModuleInstalledInfo

_logger = logging.getLogger(__name__)

partner_module_api_router = APIRouter()


@partner_module_api_router.post(
    "/module/synchronize_installed_module_info",
)
def synchronize_module_info(
    data: ModuleInstalledInfo,
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
):
    module_info_data = data.modules_info
    version = module_info_data.version
    module_partner_obj = env["module.partner"]
    partner_modules = env["module.partner"]
    for module_info in module_info_data.modules:
        partner_modules |= module_partner_obj.update_or_create(
            partner, version, module_info.model_dump()
        )

    # delete modules not used anymore by partner
    obsolete_partner_modules = module_partner_obj.search(
        [
            ("partner_id", "=", partner.id),
            ("id", "not in", partner_modules.ids),
        ]
    )
    obsolete_partner_modules.unlink()
