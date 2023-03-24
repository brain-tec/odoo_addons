# -*- encoding: utf-8 -*-
##############################################################################
#
# -*- coding: utf-8 -*-
# (C) 2019 Smile (<http://www.smile.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models, fields


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    website_published = fields.Boolean(string="Publish on website")
