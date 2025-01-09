# -*- coding: utf-8 -*-
# (C) 2024 Smile (<http://www.smile.fr>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AttributesMapping(models.Model):
    _name = 'attributes.mapping'
    _description = 'Attribute mapping'

    name = fields.Char(string="Attribute name")
    field_name = fields.Selection(string="Odoo Field", 
        selection="_field_name_selection", required=True)
    cas_parameter_id = fields.Many2one('cas.parameter')
    creation_requirement = fields.Boolean('Required to create user')

    _sql_constraints = [
        ('field_name_parameter_uniq',
         'unique (field_name, cas_parameter_id)',
         'An Odoo field can be use only one time.')
    ]

    @api.model
    def _field_name_selection(self):
        user_fields = self.env["res.users"].fields_get().items()

        def valid_field(f, d):
            return d.get("type") == "char" and not d.get("readonly")

        result = [(f, d.get("string")) for f, d in user_fields 
                    if valid_field(f, d)]
        result.sort(key=lambda r: r[1])

        return result
