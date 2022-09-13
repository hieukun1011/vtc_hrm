# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ApprovalProductLine(models.Model):
    _name = 'approval.product.line'
    _description = 'Product Line'

    approval_request_id = fields.Many2one('approval.request', required=True)
    description = fields.Char("Description", required=True)
    product_id = fields.Many2one('approval.product', string="Products")
    quantity = fields.Float("Quantity", default=1.0)
    company_id = fields.Many2one(
        string='Company', related='approval_request_id.company_id',
        store=True, readonly=True, index=True)

