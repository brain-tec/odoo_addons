# -*- coding: utf-8 -*-
# (C) 2025 Smile (<http://www.smile.fr>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase


class TestEcotaxe(TransactionCase):
    def setUp(self):
        super().setUp()
        self.ProductProduct = self.env['product.product']
        self.PurchaseOrder = self.env['purchase.order']
        self.AccountMove = self.env['account.move']
        self.PurchaseOrderLine = self.env['purchase.order.line']
        self.Partner = self.env['res.partner']
        self.TaxGroup = self.env['account.tax.group']
        self.Tax = self.env['account.tax']
        self.tax_group = self.TaxGroup.create({
            'name': 'TVA',
        })
        self.tax_20 = self.Tax.create({
            'name': 'TVA 20%',
            'amount_type': 'percent',
            'amount': 20.0,
            'type_tax_use': 'purchase',
            'tax_group_id': self.tax_group.id,
        })
        self.vendor = self.Partner.create({
            'name': 'Test Vendor',
            'supplier_rank': 1,
        })
        self.product1 = self.ProductProduct.create({
            'name': 'produit 1',
            'list_price': 3.0,
            'fixed_ecotaxe': 6.0,
            'taxes_id': [(6, 0, [self.tax_20.id])],
            'purchase_method': 'purchase'
        })
        self.product2 = self.ProductProduct.create({
            'name': 'produit 2',
            'list_price': 4.0,
            'fixed_ecotaxe': 19.0,
            'taxes_id': [(6, 0, [self.tax_20.id])],
            'purchase_method': 'purchase'
        })

        self.purchase_order = self.PurchaseOrder.create({
            'partner_id': self.vendor.id,
        })
        self.po_line1 = self.PurchaseOrderLine.create({
            'order_id': self.purchase_order.id,
            'product_id': self.product1.id,
            'product_qty': 1.0,
            'price_unit': 3.0,
            'taxes_id': [(6, 0, [self.tax_20.id])],
        })
        self.po_line2 = self.PurchaseOrderLine.create({
            'order_id': self.purchase_order.id,
            'product_id': self.product2.id,
            'product_qty': 1.0,
            'price_unit': 4.0,
            'taxes_id': [(6, 0, [self.tax_20.id])],
        })

    def test_00_ecotaxe_purchase(self):
        """Test ecotaxe calculation on purchase order"""
        self.assertEqual(self.po_line1.ecotaxe_unit, 6.0,
                         "PO line 1 should have ecotaxe of 6.0")
        self.assertEqual(self.po_line2.ecotaxe_unit, 19.0, 
                         "PO line 2 should have ecotaxe of 19.0")
        self.assertEqual(self.purchase_order.amount_ecotaxe, 25.0,
                         "Purchase order should have total ecotaxe of 25.0")
        self.assertEqual(self.purchase_order.amount_tax, 6.4,
                              msg="Purchase order tax total should be 6.4")
        self.assertEqual(self.purchase_order.amount_untaxed, 32,
                              msg="Purchase order untaxed total should be 32.0")
        self.assertEqual(self.purchase_order.amount_total, 38.4,
                              msg="Purchase order total should be 38.4")
