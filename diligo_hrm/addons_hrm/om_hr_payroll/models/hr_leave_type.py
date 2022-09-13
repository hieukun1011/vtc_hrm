# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Copyright (c) 2005-2006 Axelor SARL. (http://www.axelor.com)

from odoo import api, fields, models
from datetime import timedelta


class HrLeave(models.Model):
    _inherit = "hr.leave.type"

    code = fields.Char('Payroll Code')