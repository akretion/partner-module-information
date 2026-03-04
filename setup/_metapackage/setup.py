import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-akretion-partner-module-information",
    description="Meta package for akretion-partner-module-information Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-module_info_import>=16.0dev,<16.1dev',
        'odoo-addon-module_info_import_odoo_repository>=16.0dev,<16.1dev',
        'odoo-addon-module_info_migration>=16.0dev,<16.1dev',
        'odoo-addon-module_info_partner>=16.0dev,<16.1dev',
        'odoo-addon-module_info_pull_request>=16.0dev,<16.1dev',
        'odoo-addon-module_info_pull_request_migration>=16.0dev,<16.1dev',
        'odoo-addon-module_info_pull_request_task_link>=16.0dev,<16.1dev',
        'odoo-addon-module_info_pull_request_timesheet>=16.0dev,<16.1dev',
        'odoo-addon-module_info_push>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
