from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    subtotal_ecotaxe = fields.Float(
        compute="_compute_subtotal_ecotaxe",
        store=True,
    )
    ecotaxe_unit = fields.Float(
        string="Ecotaxe Unit.",
        store=True,
        compute="_compute_ecotaxe_unit",
        readonly=False,
    )

    @api.depends("order_id.currency_id", "product_id")
    def _compute_ecotaxe_unit(self):
        for line in self:
            ecotaxe_unit = line.product_id.fixed_ecotaxe
            if line.order_id.currency_id:
                ecotaxe_unit = line.order_id.currency_id.round(ecotaxe_unit)
            line.update(
                {
                    "ecotaxe_unit": ecotaxe_unit,
                }
            )

    @api.depends("order_id.currency_id", "product_qty", "ecotaxe_unit")
    def _compute_subtotal_ecotaxe(self):
        for line in self:
            ecotaxe_unit = line.ecotaxe_unit
            if line.order_id.currency_id:
                ecotaxe_unit = line.order_id.currency_id.round(ecotaxe_unit)
            line.update(
                {
                    "subtotal_ecotaxe": ecotaxe_unit * line.product_qty,
                }
            )

    def _prepare_account_move_line(self, move=False):
        res = super()._prepare_account_move_line(move)
        res.update({"ecotaxe_unit": self.ecotaxe_unit})
        return res