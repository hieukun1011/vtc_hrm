# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HrContract(models.Model):
    """
    Employee contract based on the visa, work permits
    allows to configure different Salary structure
    """
    _inherit = 'hr.contract'
    _description = 'Employee Contract'

    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure')
    schedule_pay = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi-annually', 'Semi-annually'),
        ('annually', 'Annually'),
        ('weekly', 'Weekly'),
        ('bi-weekly', 'Bi-weekly'),
        ('bi-monthly', 'Bi-monthly'),
    ], string='Scheduled Pay', index=True, default='monthly',
    help="Defines the frequency of the wage payment.")
    resource_calendar_id = fields.Many2one(required=True, help="Employee's working schedule.")
    hra = fields.Monetary(string='Trợ cấp nhà ở')
    travel_allowance = fields.Monetary(string="Trợ cấp đi lại ")
    da = fields.Monetary(string="Thưởng chuyên cần")
    mobile_allowance = fields.Monetary(string="Phụ cấp điện thoại")
    car_allowance = fields.Monetary(string="Phụ cấp xăng xe")
    kpi_allowance = fields.Monetary(string="Lương KPI(năng suất)", help="Lương KPI(năng suất)")
    other_allowance = fields.Monetary(string="Lương cơ bản ", help="Lương cơ bản ")
    block_type = fields.Selection([
        ('product', 'Công nhân sản xuất'),
        ('technical', 'Công nhân kỹ thuật'),
        ('officer', 'Nhân viên văn phòng')
    ], string='Khối làm việc')

    @api.onchange('hra', 'travel_allowance', 'da', 'mobile_allowance', 'car_allowance', 'kpi_allowance', 'other_allowance')
    def total_salary(self):
        self.wage = self.hra + self.travel_allowance + self.da + self.mobile_allowance + self.car_allowance + self.kpi_allowance + self.other_allowance

    @api.onchange('contract_type_id')
    def _onchange_contract_type_id(self):
        self.other_allowance = self.kpi_allowance = self.mobile_allowance = self.da = self.travel_allowance = self.hra = 0
        if self.contract_type_id:
            self.hra = self.contract_type_id.hra
            self.travel_allowance = self.contract_type_id.travel_allowance
            self.da = self.contract_type_id.da
            self.mobile_allowance = self.contract_type_id.mobile_allowance
            self.car_allowance = self.contract_type_id.car_allowance
            self.kpi_allowance = self.contract_type_id.kpi_allowance
            self.other_allowance = self.contract_type_id.other_allowance

    def get_all_structures(self):
        """
        @return: the structures linked to the given contracts, ordered by hierachy (parent=False first,
                 then first level children and so on) and without duplicata
        """
        structures = self.mapped('struct_id')
        if not structures:
            return []
        # YTI TODO return browse records
        return list(set(structures._get_parent_structure().ids))

    def get_attribute(self, code, attribute):
        return self.env['hr.contract.advantage.template'].search([('code', '=', code)], limit=1)[attribute]

    def set_attribute_value(self, code, active):
        for contract in self:
            if active:
                value = self.env['hr.contract.advantage.template'].search([('code', '=', code)], limit=1).default_value
                contract[code] = value
            else:
                contract[code] = 0.0


class HrContractAdvantageTemplate(models.Model):
    _name = 'hr.contract.advantage.template'
    _description = "Employee's Advantage on Contract"

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    lower_bound = fields.Float('Lower Bound', help="Lower bound authorized by the employer for this advantage")
    upper_bound = fields.Float('Upper Bound', help="Upper bound authorized by the employer for this advantage")
    default_value = fields.Float('Default value for this advantage')