# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class ContractType(models.Model):
    _name = 'hr.contract.type'
    _description = 'Contract Type'
    _order = 'sequence, id'

    name = fields.Char(string='Name', required=True, help="Name of the contract")
    block_type = fields.Selection([
        ('product', 'Công nhân sản xuất'),
        ('technical', 'Công nhân kỹ thuật'),
        ('officer', 'Nhân viên văn phòng')
    ], string='Khối làm việc')
    sequence = fields.Integer(help="Gives the sequence when displaying a list of Contract.", default=10)
    hra = fields.Integer(string='Trợ cấp nhà ở')
    travel_allowance = fields.Integer(string="Trợ cấp đi lại ")
    da = fields.Integer(string="Thưởng chuyên cần")
    mobile_allowance = fields.Integer(string="Phụ cấp điện thoại")
    car_allowance = fields.Integer(string="Phụ cấp xăng xe")
    kpi_allowance = fields.Integer(string="Lương KPI(năng suất)", help="Lương KPI(năng suất)")
    other_allowance = fields.Integer(string="Lương cơ bản ", help="Lương cơ bản ")
