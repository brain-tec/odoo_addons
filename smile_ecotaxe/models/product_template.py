from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    fixed_ecotaxe = fields.Monetary(
        string="Ecotaxe",
        currency_field="currency_id",
        help="Known as ecotaxe, \n"
        "it is an eco-participation supplied by the provider.\n",
    )
