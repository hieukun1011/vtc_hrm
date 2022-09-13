# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import itertools
import logging
from collections import defaultdict

from odoo import api, fields, models, tools, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, RedirectWarning, UserError
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class ApprovalCategory(models.Model):
    _name = 'approval.product.category'

    name = fields.Char('Name')


class ApprovalProductProduct(models.Model):
    _name = 'approval.product'

    name = fields.Char('Name', index=True, required=True, translate=True)
    description = fields.Html(
        'Description', translate=True)
    price = fields.Float('Price')
    image = fields.Image('Image', max_width=1920, max_height=1920)
    category = fields.Many2one('approval.product.category', string='Category')
    is_sale = fields.Boolean('Can be Sold')

    @api.model
    def create(self, vals_list):
        print(vals_list)
        users = super(ApprovalProductProduct, self).create(vals_list)

        return users