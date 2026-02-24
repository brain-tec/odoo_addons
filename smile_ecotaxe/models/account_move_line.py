from odoo import api, fields, models


class AcountMoveLine(models.Model):
    _inherit = "account.move.line"

    subtotal_ecotaxe = fields.Float(
        compute="_compute_subtotal_ecotaxe",
        store=True,
    )
    ecotaxe_unit = fields.Float(
        string="Ecotaxe Unit.",
        store=True,
        compute="_compute_ecotaxe_unit",
        readonly=False,
        precompute=True,
    )

    @api.depends("move_id.currency_id", "product_id")
    def _compute_ecotaxe_unit(self):
        for line in self:
            ecotaxe_unit = line.product_id.fixed_ecotaxe
            if line.move_id.currency_id:
                ecotaxe_unit = line.move_id.currency_id.round(ecotaxe_unit)
            line.update(
                {
                    "ecotaxe_unit": ecotaxe_unit,
                }
            )

    @api.depends("move_id.currency_id", "quantity", "ecotaxe_unit")
    def _compute_subtotal_ecotaxe(self):
        for line in self:
            ecotaxe_unit = line.ecotaxe_unit
            if line.move_id.currency_id:
                ecotaxe_unit = line.move_id.currency_id.round(ecotaxe_unit)
            line.update(
                {
                    "subtotal_ecotaxe": ecotaxe_unit * line.quantity,
                }
            )
