{
    "name": "Module Info Migration",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/akretion/partner-module-information",
    "category": "Tools",
    "depends": ["module_info_partner", "project", "project_task_stage_state"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner.xml",
        "views/module_partner.xml",
        "views/module_information.xml",
        "wizard/module_task_creator.xml",
    ],
    "installable": True,
}
