# -*- coding: utf-8 -*-
import datetime
from datetime import datetime, timedelta, date
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

date_format = "%Y-%m-%d"
RESIGNATION_TYPE = [('resigned', 'Nghỉ phép'),
                    ('fired', 'Từ chức')]


class HrResignation(models.Model):
    _name = 'hr.resignation'
    _inherit = 'mail.thread'
    _rec_name = 'employee_id'

    date_from = fields.Date('From date')
    date_to = fields.Date('To date')
    date_fired = fields.Date('Fired')

    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee', string="Employee", default=lambda self: self.env.user.employee_id.id,
                                  states={'draft': [('readonly', False)]}, readonly = True,
                                  help='Name of the employee for whom the request is creating')
    department_id = fields.Many2one('hr.department', string="Department", related='employee_id.department_id',
                                    help='Department of the employee')
    resign_confirm_date = fields.Date(string="Confirmed Date",
                                      help='Date on which the request is confirmed by the employee.',
                                      tracking=True)
    approved_revealing_date = fields.Date(string="Approved Last Day Of Employee",
                                          help='Date on which the request is confirmed by the manager.',
                                          tracking=True)
    joined_date = fields.Date(string="Join Date", store=True, states={'draft': [('readonly', False)]}, readonly=True,
                              help='Joining date of the employee.i.e Start date of the first contract')

    expected_revealing_date = fields.Date(string="Last Day of Employee", states={'draft': [('readonly', False)]}, readonly = True,
                                          help='Employee requested date on which he is revealing from the company.')
    reason = fields.Text(string="Reason", required=True, states={'draft': [('readonly', False)]}, readonly=True,
                         help='Specify reason for leaving the company')
    notice_period = fields.Char(string="Notice Period")
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirm'), ('approved', 'Approved'), ('cancel', 'Rejected')],
        string='Status', default='draft', tracking=True)
    resignation_type = fields.Selection(selection=RESIGNATION_TYPE, states={'draft': [('readonly', False)]}, readonly=True,
                                        help="Select the type of resignation: normal "
                                                                         "resignation or fired by the company")
    read_only = fields.Boolean(string="check field")
    employee_contract = fields.Char(String="Contract")
    job = fields.Many2one('hr.job', 'Chức vụ', related='employee_id.job_id', store=True)


    @api.constrains('date_from', 'date_to', 'date_fired', 'resignation_type')
    def _constrains_time_on_leave(self):
        for rec in self:
            if rec.resignation_type == 'resigned':

                if rec.date_from and rec.date_to:
                    if rec.date_from > rec.date_to:
                        raise ValidationError(_('Từ ngày phải nhỏ hơn đến ngày.'))
                else:
                    if not rec.date_from or not rec.date_to:
                        raise ValidationError(_('Bạn cần cung cấp đầy đủ thời gian bắt đầu và kết thúc của kì nghỉ.'))
            else:
                if not rec.date_fired:
                    raise ValidationError(_('Bạn cần cung cấp ngày nghỉ việc'))

    @api.onchange('employee_id')
    @api.depends('employee_id')
    def _compute_read_only(self):
        """ Use this function to check weather the user has the permission to change the employee"""
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.has_group('hr.group_hr_user'):
            self.read_only = True
        else:
            self.read_only = False

    @api.onchange('employee_id')
    def set_join_date(self):
        # self.joined_date = self.employee_id.joining_date if self.employee_id.joining_date else ''
        self.joined_date = self.employee_id.joining_date

    # @api.depends('employee_id')
    # def compute_join_date(self):
    #     # self.joined_date = self.employee_id.joining_date if self.employee_id.joining_date else ''
    #     if employee_id.joining_date :
    #         self.joined_date = self.employee_id.joining_date
    #     else :
    #         self.joined_date = False

    @api.model
    def create(self, vals):
        # assigning the sequence for the record
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.resignation') or _('New')
        res = super(HrResignation, self).create(vals)
        return res

    @api.constrains('employee_id')
    def check_employee(self):
        # Checking whether the user is creating leave request of his/her own
        for rec in self:
            if not self.env.user.has_group('hr.group_hr_user'):
                if rec.employee_id.user_id.id and rec.employee_id.user_id.id != self.env.uid:
                    raise ValidationError(_('You cannot create request for other employees'))

    @api.onchange('employee_id')
    @api.depends('employee_id')
    def check_request_existence(self):
        # Check whether any resignation request already exists
        for rec in self:
            if rec.employee_id:
                resignation_request = self.env['hr.resignation'].search([('employee_id', '=', rec.employee_id.id),
                                                                         ('state', 'in', ['confirm', 'approved'])])
                if resignation_request:
                    raise ValidationError(_('There is a resignation request in confirmed or'
                                            ' approved state for this employee'))
                if rec.employee_id:
                    no_of_contract = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)])
                    for contracts in no_of_contract:
                        if contracts.state == 'open':
                            rec.employee_contract = contracts.name
                            rec.notice_period = contracts.notice_days

    @api.constrains('joined_date')
    def _check_dates(self):
        # validating the entered dates
        for rec in self:
            resignation_request = self.env['hr.resignation'].search([('employee_id', '=', rec.employee_id.id),
                                                                     ('state', 'in', ['confirm', 'approved'])])
            if resignation_request:
                raise ValidationError(_('There is a resignation request in confirmed or'
                                        ' approved state for this employee'))

    def confirm_resignation(self):
        if self.resignation_type == 'resigned':
            if self.date_from and self.date_to:
                if abs(date.today() - self.date_from).days < 7:
                    raise ValidationError(_('Từ ngày phải cách ngày hiện tại ít nhất 7 ngày'))
            else:
                raise ValidationError(_('Bạn cần cung cấp đầy đủ thời gian bắt đầu và kết thúc của kì nghỉ.'))
        else:
            if self.date_fired:
                if abs(date.today() - self.date_fired).days < 45:
                    raise ValidationError(_('Thời gian nghỉ việc phải cách ngày hiện tại ít nhất 45 ngày'))
            else:
                raise ValidationError(_('Bạn cần cung cấp ngày nghỉ việc'))

        if self.joined_date:
            if self.joined_date >= self.expected_revealing_date:
                raise ValidationError(_('Last date of the Employee must be anterior to Joining date'))
            for rec in self:
                rec.state = 'confirm'
                rec.resign_confirm_date = str(datetime.now())

                #Tạo yêu cầu thu hồi thiết bị nếu có
                custody_ids = self.env['sci.device.main'].sudo().search([('employee_id', '=', rec.employee_id.id)])
                flag = False
                device_ids = []
                des_id = '<h3>Thu hồi thiết bị của nhân viên nghỉ việc: \n</h3>'
                for data in custody_ids:
                    flag = True
                    device_ids.append((4, data.id))
                    emp_id = data.category_id.technician_user_id.id if data.category_id.technician_user_id else None
                    cate_id = data.category_id.id if data.category_id else None
                    des_id += '<div>\n Tên thiết bị: </div>' + data.name + '<div> Mã thiết bị: </div>' + data.default_code
                if flag:
                    payload = {
                        'name': "Thu hồi thiết bị nhân viên nghỉ việc: " + '[' + rec.employee_id.employee_id + '] ' + rec.employee_id.name,
                        'maintenance_type': 'corrective',
                        'category_id': cate_id,
                        'channel': 'other',
                        'emp_id': emp_id,
                        'request_date': datetime.now(),
                        'person_name': self.env.user.employee_id.id,
                        'type': 'odoo',
                        'description': des_id
                    }
                    self.env['sci.maintenance.request'].create(payload)
                for item in custody_ids:
                    device_ids.append((4, item.id))
                    emp_ids = item.category_id.technician_user_id.id if item.category_id.technician_user_id else None
                    cate_ids = item.category_id.id if item.category_id else None
                if flag:
                    payload = {
                        'type': 'import',
                        'state': 'approved',
                        'department_id': self.department_id.id,
                        'parent_id': emp_ids,
                        'employee_id': self.env.user.employee_id.id,
                        'employee_use': self.employee_id.id,
                        'category_id': cate_ids,
                        'device_ids': device_ids,
                    }
                    self.env['ems.equipment.export'].create(payload)
        else:
            raise ValidationError(_('Please set joining date for employee'))

    def cancel_resignation(self):
        for rec in self:
            rec.state = 'cancel'

    def reject_resignation(self):
        for rec in self:
            rec.state = 'cancel'

    def reset_to_draft(self):
        for rec in self:
            rec.state = 'draft'
            rec.employee_id.active = True
            rec.employee_id.resigned = False
            rec.employee_id.fired = False

    def approve_resignation(self):
        for rec in self:
            if rec.expected_revealing_date and rec.resign_confirm_date:
                no_of_contract = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)])
                for contracts in no_of_contract:
                    if contracts.state == 'open':
                        rec.employee_contract = contracts.name
                        rec.state = 'approved'
                        rec.approved_revealing_date = rec.resign_confirm_date + timedelta(days=contracts.notice_days)
                    else:
                        rec.approved_revealing_date = rec.expected_revealing_date
                # Changing state of the employee if resigning today
                if rec.expected_revealing_date <= fields.Date.today() and rec.employee_id.active:
                    rec.employee_id.active = False
                    # Changing fields in the employee table with respect to resignation
                    rec.employee_id.resign_date = rec.expected_revealing_date
                    if rec.resignation_type == 'resigned':
                        rec.employee_id.resigned = True
                    else:
                        rec.employee_id.fired = True
                    # Removing and deactivating user
                    if rec.employee_id.user_id:
                        rec.employee_id.user_id.active = False
                        rec.employee_id.user_id = None
            else:
                raise ValidationError(_('Please enter valid dates.'))

    def update_employee_status(self):
        resignation = self.env['hr.resignation'].search([('state', '=', 'approved')])
        for rec in resignation:
            if rec.expected_revealing_date <= fields.Date.today() and rec.employee_id.active:
                rec.employee_id.active = False
                # Changing fields in the employee table with respect to resignation
                rec.employee_id.resign_date = rec.expected_revealing_date
                if rec.resignation_type == 'resigned':
                    rec.employee_id.resigned = True
                else:
                    rec.employee_id.fired = True
                # Removing and deactivating user
                if rec.employee_id.user_id:
                    rec.employee_id.user_id.active = False
                    rec.employee_id.user_id = None
                rec.employee_id.stages_history.sudo().create({'start_date': rec.expected_revealing_date,
                                                     'employee_id': rec.employee_id.id,
                                                     'state': 'terminated'})


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    resign_date = fields.Date('Resign Date', readonly=True, help="Date of the resignation")
    resigned = fields.Boolean(string="Resigned", default=False, store=True,
                              help="If checked then employee has resigned")
    fired = fields.Boolean(string="Fired", default=False, store=True, help="If checked then employee has fired")
