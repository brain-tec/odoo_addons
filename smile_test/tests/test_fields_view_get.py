# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase


class TestFieldsViewGet(TransactionCase):
    def test_check_fields_view_get(self):
        """I check all fields_view_get."""
        errors = []
        models = self.env["ir.model"].search([])
        for model in models:
            if getattr(model, "_abstract", False):
                continue
            for view_type in ["form", "tree"]:
                try:
                    self.env[model.model].fields_view_get(view_type=view_type)
                except Exception as e:
                    err_info = (model.model, view_type, repr(e))
                    errors.append(err_info)
        err_details = "\n".join(
            "(%s, %s): %s" % (model, view_type, err)
            for model, view_type, err in errors
        )
        error_msg = (
            "Error in fields_view_get for models/view_type "
            "and error:\n%s" % err_details
        )
        self.assertEqual(len(errors), 0, error_msg)
