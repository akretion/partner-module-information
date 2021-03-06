# coding: utf-8

{
    "name": "Module Info Partner",
    "description": "Information about odoo modules used by your partners",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "Akretion, Odoo Community Association (OCA)",
    "category": "Tools",
    "depends": ["base_rest"],
    "data": [
        "security/ir.model.access.csv",
        "views/module_information.xml",
        "views/res_partner.xml",
        "data/odoo_version.xml",
        "views/module_partner.xml",
        "views/module_version.xml",
    ],
    "installable": True,
}
