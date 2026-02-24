from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    amount_ecotaxe = fields.Monetary(
        string="Ecotaxe", store=True, compute="_compute_ecotaxe"
    )

    @api.depends("order_line.subtotal_ecotaxe")
    def _compute_ecotaxe(self):
        for order in self:
            order.amount_ecotaxe = sum(
                order.order_line.mapped("subtotal_ecotaxe")
            )
