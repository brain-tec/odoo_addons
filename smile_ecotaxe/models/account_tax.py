from odoo import api, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    @api.model
    def _get_tax_totals_summary(
        self, base_lines, currency, company, cash_rounding=None
    ):
        """Include Ecotax when this method is called upon a single order"""
        res = super()._get_tax_totals_summary(
            base_lines, currency, company, cash_rounding=cash_rounding
        )
        if base_lines:
            record_line = base_lines[0].get("record")
            if record_line._name == "account.move.line":
                base_amt = record_line.move_id.amount_total
                ecotax_amt = record_line.move_id.amount_ecotaxe
            elif record_line._name == "purchase.order.line":
                base_amt = record_line.order_id.amount_total
                ecotax_amt = record_line.order_id.amount_ecotaxe
            else:
                base_amt = ecotax_amt = 0.0

            if not ecotax_amt:
                return res

            data = res["subtotals"][0] or {}
            data.get("tax_groups").insert(0, {
                "group_name": self.env._("Untaxed Eco-participation"),
                "tax_amount": ecotax_amt,
                "tax_amount_currency": ecotax_amt,
                "base_amount": base_amt,
                "base_amount_currency": base_amt,
                "tax_group_id": False,
                "id": False,
                "group_key": "included_ecotaxe",
            })
            res["subtotals"][0] = data
        return res

    @api.model
    def _add_tax_details_in_base_line(
        self, base_line, company, rounding_method=None
    ):  # noqa: -n
        price_unit_after_discount = base_line["price_unit"] * (
            1 - (base_line["discount"] / 100.0)
        )
        # SMILE CHANGE :
        # Get the unit ecotaxe amount from the line record
        ecotaxe_unit = 0
        if base_line.get("record"):
            ecotaxe_unit = base_line.get("record").ecotaxe_unit
        # end change
        taxes_computation = base_line["tax_ids"]._get_tax_details(
            # SMILE CHANGE :
            # Include the unit ecotaxe in computing the tax amounts
            price_unit=price_unit_after_discount + ecotaxe_unit,
            # end change
            quantity=base_line["quantity"],
            precision_rounding=base_line["currency_id"].rounding,
            rounding_method=rounding_method
            or company.tax_calculation_rounding_method,  # noqa: -n
            product=base_line["product_id"],
            special_mode=base_line["special_mode"],
            manual_tax_amounts=base_line["manual_tax_amounts"],
        )
        rate = base_line["rate"]
        tax_details = base_line["tax_details"] = {
            "raw_total_excluded_currency": taxes_computation["total_excluded"],
            "raw_total_excluded": taxes_computation["total_excluded"] / rate
            if rate
            else 0.0,
            "raw_total_included_currency": taxes_computation["total_included"],
            "raw_total_included": taxes_computation["total_included"] / rate
            if rate
            else 0.0,
            "taxes_data": [],
        }
        if company.tax_calculation_rounding_method == "round_per_line":
            tax_details["raw_total_excluded"] = company.currency_id.round(
                tax_details["raw_total_excluded"]
            )
            tax_details["raw_total_included"] = company.currency_id.round(
                tax_details["raw_total_included"]
            )
        for tax_data in taxes_computation["taxes_data"]:
            tax_amount = tax_data["tax_amount"] / rate if rate else 0.0
            base_amount = tax_data["base_amount"] / rate if rate else 0.0
            if company.tax_calculation_rounding_method == "round_per_line":
                tax_amount = company.currency_id.round(tax_amount)
                base_amount = company.currency_id.round(base_amount)
            tax_details["taxes_data"].append(
                {
                    **tax_data,
                    "raw_tax_amount_currency": tax_data["tax_amount"],
                    "raw_tax_amount": tax_amount,
                    "raw_base_amount_currency": tax_data["base_amount"],
                    "raw_base_amount": base_amount,
                }
            )
