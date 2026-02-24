# © 2014-2016 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    amount_ecotaxe = fields.Monetary(
        string="Ecotaxe", store=True, compute="_compute_ecotaxe"
    )

    @api.depends("invoice_line_ids.subtotal_ecotaxe")
    def _compute_ecotaxe(self):
        for move in self:
            move.amount_ecotaxe = sum(
                move.invoice_line_ids.mapped("subtotal_ecotaxe")
            )
