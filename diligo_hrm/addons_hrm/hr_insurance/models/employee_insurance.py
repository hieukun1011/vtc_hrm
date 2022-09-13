# -*- coding: utf-8 -*-

import time
from datetime import datetime,date
from dateutil import relativedelta
from odoo import models, fields, api, _


class EmployeeInsurance(models.Model):
    _name = 'hr.insurance'
    _description = 'HR Insurance'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, help="Employee")
    policy_id = fields.Selection([('BHXH', 'BHXH'), ('BHYT', 'BHYT'), ('BHTN', 'BHTN')], required=True,
                                 default='BHXH', string='Policy')
    sum_insured = fields.Float(string="Sum Insured", required=True, help="Insured sum")
    amount = fields.Float(string='Premium', required=True, help="Policy amount")
    state = fields.Selection([('active', 'Active'), ('expired', 'Expired')],
                             default='active', string="State")
    company_id = fields.Many2one('res.company', string='Company', required=True, help="Company",
                                 default=lambda self: self.env.user.company_id)
    _sql_constraints = [
        ('employee_policy_uniq', 'unique(employee_id, policy_id)', 'Mã bảo hiểm đã tồn tại !'),
    ]

    @api.constrains('state')
    def check_employee_official(self):
        for record in self:
            if record.state == 'active':
                record.employee_id.is_official = True

    @api.onchange('policy_id')
    def _onchange_policy_id(self):
        if self.policy_id == 'BHXH':
            self.sum_insured = 4730000
            self.amount = 8
        if self.policy_id == 'BHYT':
            self.sum_insured = 4730000
            self.amount = 1.5
        if self.policy_id == 'BHTN':
            self.sum_insured = 4730000
            self.amount = 1

class HrInsurance(models.Model):
    _inherit = 'hr.employee'

    is_insurance = fields.Boolean(string="is insurance", default=True)
    reason_insurance = fields.Text(string="reason insurance")
    insurance = fields.One2many('hr.insurance', 'employee_id', string="Insurance", help="Insurance",
                                domain=[('state', '=', 'active')])

class InsuranceRuleInput(models.Model):
    _inherit = 'hr.payslip'

    def get_inputs(self, contract_ids, date_from, date_to):
        res = super(InsuranceRuleInput, self).get_inputs(contract_ids, date_from, date_to)
        contract_obj = self.env['hr.contract']
        lst_res = []
        for i in contract_ids:
            if contract_ids[0]:
                emp_id = contract_obj.browse(i[0].id).employee_id
                for result in res:
                    if emp_id.insurance and emp_id.is_insurance:
                        for item_insu in emp_id.insurance:
                            if item_insu.state == 'active' and item_insu.policy_id == 'BHXH':
                                if result.get('code') == 'INSUR_BHXH':
                                    result['amount'] = item_insu.sum_insured * (item_insu.amount / 100)
                            if item_insu.state == 'active' and item_insu.policy_id == 'BHYT':
                                if result.get('code') == 'INSUR_BHYT':
                                    result['amount'] = item_insu.sum_insured * (item_insu.amount / 100)
                            if item_insu.state == 'active' and item_insu.policy_id == 'BHTN':
                                if result.get('code') == 'INSUR_BHTN':
                                    result['amount'] = item_insu.sum_insured * (item_insu.amount / 100)
                    if emp_id.kpi_ids:
                        for item_kpi in emp_id.kpi_ids:
                            if result.get('code') == 'KPIs':
                                if item_kpi.ld_point >= 80:
                                    result['amount'] = contract_ids.kpi_allowance
                                elif item_kpi.ld_point >= 70:
                                    result['amount'] = contract_ids.kpi_allowance * 0.95
                                elif item_kpi.ld_point >= 60:
                                    result['amount'] = contract_ids.kpi_allowance * 0.85
                                else:
                                    result['amount'] = contract_ids.kpi_allowance * 0.75
                            if result.get('code') == 'KPIs_Master':
                                #  Lương TN theo KQ PP
                                if item_kpi.ld_point >= 80:
                                    pp = contract_ids.kpi_allowance * 0.92
                                elif item_kpi.ld_point >= 70:
                                    pp = (contract_ids.kpi_allowance * 0.9) * 0.92
                                elif item_kpi.ld_point >= 60:
                                    pp = (contract_ids.kpi_allowance * 0.8) * 0.92
                                else:
                                    pp = (contract_ids.kpi_allowance * 0.7) * 0.92
                                # Lương TN theo KQ DT
                                if item_kpi.payroll_kpi_id.business_results >= 80:
                                    dt = contract_ids.kpi_allowance * 0.05
                                elif item_kpi.payroll_kpi_id.business_results >= 70:
                                    dt = (contract_ids.kpi_allowance * 0.9) * 0.05
                                elif item_kpi.payroll_kpi_id.business_results >= 60:
                                    dt = (contract_ids.kpi_allowance * 0.8) * 0.05
                                else:
                                    dt = (contract_ids.kpi_allowance * 0.75) * 0.05
                                # Lương TN theo KQ LN
                                if item_kpi.payroll_kpi_id.total_profit >= 80:
                                    ln = contract_ids.kpi_allowance * 0.03
                                elif item_kpi.payroll_kpi_id.total_profit >= 70:
                                    ln = (contract_ids.kpi_allowance * 0.9) * 0.03
                                elif item_kpi.payroll_kpi_id.total_profit >= 60:
                                    ln = (contract_ids.kpi_allowance * 0.8) * 0.03
                                else:
                                    ln = (contract_ids.kpi_allowance * 0.75) * 0.03
                                # Tổng lương TN thực nhận
                                result['amount'] = pp + dt + ln
                    lst_res.append(result)

        return lst_res
