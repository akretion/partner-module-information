from odoo import fields, models


class ModuleVersion(models.Model):
    _name = "module.version"
    _description = "Available module in a specific Odoo version"

    version_id = fields.Many2one(
        "odoo.version", required=True, index=True, ondelete="cascade"
    )
    module_id = fields.Many2one(
        "module.information", required=True, index=True, ondelete="cascade"
    )
    state = fields.Selection(
        [("pending", "Pending"), ("done", "Done")],
        default="pending",
        help="Indicates if module is available or has to be migrated.",
    )

    _sql_constraints = [
        (
            "module_version_uniq",
            "unique(module_id, version_id)",
            "Not possible to have twice the same module for the same version!",
        )
    ]
