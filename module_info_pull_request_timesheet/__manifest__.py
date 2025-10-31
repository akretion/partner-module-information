{
    "name": "Module Info Timesheet",
    "summary": "Add timesheet to Pull request",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/akretion/partner-module-information",
    "category": "Tools",
    "depends": [
        "queue_job",
        "module_info_pull_request",
        "analytic",
        "hr_timesheet_sheet",
    ],
    "data": [
        "views/pull_request.xml",
    ],
    "installable": True,
}
