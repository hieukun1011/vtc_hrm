# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class InheritEmployee(models.Model):
    _inherit = 'hr.employee'

    discipline_count = fields.Integer(compute="_compute_discipline_count")
    laudatory_count = fields.Integer(compute="_compute_laudatory_count")

    def _compute_discipline_count(self):
        for obj in self:
            disciplinary_ids = self.env['disciplinary.action'].sudo().search(['|', '|', ('employee_ids', 'in', [obj.id]),
                                                                          ('department_ids', 'in', self.department_id.id),
                                                                          ('position_ids', 'in', self.job_id.id),
                                                                          ('state', 'in', ['action'])])
            obj.discipline_count = len(disciplinary_ids)

    def _compute_laudatory_count(self):
        for obj in self:
            laudatory_ids = self.env['laudatory.action'].sudo().search(['|','|', ('employee_ids', 'in', [obj.id]),
                                                                          ('department_ids', 'in', self.department_id.id),
                                                                         ('position_ids', 'in', self.job_id.id),
                                                                          ('state', 'in', ['action'])])
            obj.laudatory_count = len(laudatory_ids)

class CategoryDiscipline(models.Model):
    _name = 'discipline.category'
    _description = 'Reason Category'

    # Discipline Categories

    code = fields.Char(string="Code", required=True, help="Category code")
    name = fields.Char(string="Name", required=True, help="Category name")
    description = fields.Text(string="Mô tả", help="Details for this category")


class DisciplinaryAction(models.Model):
    _name = 'disciplinary.action'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Disciplinary Action"

    document = fields.Binary('File upload')
    document_name = fields.Char('File name')

    state = fields.Selection([
        ('draft', 'Dự Thảo'),
        ('explain', 'Giải Thích'),
        ('action', 'Xác nhận'),
        ('cancel', 'Cancelled'),

    ], default='draft', string="Trạng thái", tracking=True)

    name = fields.Char(string='Mã tham chiếu', required=True, copy=False, readonly=True,
                       default=lambda self: _('No.'))

    announcement_type = fields.Selection(
        [('employee', 'Nhân viên'), ('department', 'Phòng ban'), ('job_position', 'Vị trí công việc')],
        string="Loại kỷ luật", states={'draft': [('readonly', False)]}, readonly=True)
    employee_ids = fields.Many2many('hr.employee', 'hr_employee_disciplinary', 'disciplinary', 'employee',
                                    domain="[('company_id', '=', company_id)]", states={'draft': [('readonly', False)]}, readonly=True,
                                    string='Nhân viên')
    department_ids = fields.Many2many('hr.department', 'hr_department_disciplinary', 'disciplinary', 'department',
                                      domain="[('company_id', '=', company_id)]", states={'draft': [('readonly', False)]}, readonly=True,
                                      string='Phòng ban')
    position_ids = fields.Many2many('hr.job', 'hr_job_position_disciplinary', 'disciplinary', 'job_position',
                                    string='Vị trí công việc', states={'draft': [('readonly', False)]}, readonly=True)
    company_id = fields.Many2one('res.company', string='Công ty',
                                 default=lambda self: self.env.user.company_id)
    discipline_reason = fields.Many2one('discipline.category', string='Nhóm kỷ luật', required=True,
                                        help="Choose a disciplinary reason", states={'draft': [('readonly', False)]}, readonly=True)
    explanation = fields.Text(string="Nhân viên giải thích", help='Employee have to give Explanation'
                                                                     'to manager about the violation of discipline')
    read_only = fields.Boolean(compute="get_user", default=True)
    warning_letter = fields.Html(string="Thư cảnh báo", states={'draft': [('readonly', False)]}, readonly=True)
    warning = fields.Integer(default=False)
    action_details = fields.Text(string="Action Details", help="Give the details for this action")
    attachment_ids = fields.Many2many('ir.attachment', string="File đính kèm",
                                      help="Employee can submit any documents which supports their explanation")
    note = fields.Text(string="Ghi chú", states={'draft': [('readonly', False)]}, readonly=True)

    @api.onchange('employee_name')
    def set_join_date(self):
        self.joined_date = self.employee_name.joining_date if self.employee_name.joining_date else ''
        self.department_name = self.employee_name.department_id if self.employee_name.department_id else ''
        self.job = self.employee_name.job_id if self.employee_name.job_id else ''

    # assigning the sequence for the record
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('disciplinary.action')
        return super(DisciplinaryAction, self).create(vals)

    # Check the user is a manager or employee
    @api.depends('read_only')
    def get_user(self):
        if self.env.user.has_group('hr.group_hr_manager'):
            self.read_only = True
        else:
            self.read_only = False

    @api.onchange('employee_name')
    @api.depends('employee_name')
    def onchange_employee_name(self):

        department = self.env['hr.employee'].search([('name', '=', self.employee_name.name)])
        self.department_name = department.department_id.id

        if self.state == 'action':
            raise ValidationError(_('You Can not edit a Validated Action !!'))

    @api.onchange('discipline_reason')
    @api.depends('discipline_reason')
    def onchange_reason(self):
        if self.state == 'action':
            raise ValidationError(_('You Can not edit a Validated Action !!'))

    def assign_function(self):

        for rec in self:
            rec.state = 'explain'

    def cancel_function(self):
        for rec in self:
            rec.state = 'cancel'

    def set_to_function(self):
        for rec in self:
            rec.state = 'draft'

    def action_function(self):
        for rec in self:
            rec.state = 'action'

class LaudatoryEmployee(models.Model):
    _name = 'laudatory.action'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Laudatory Action"

    document = fields.Binary('File upload')
    document_name = fields.Char('File name')

    name = fields.Char(string='name', states={'draft': [('readonly', False)]}, readonly=True)
    announcement_type = fields.Selection(
        [('employee', 'Nhân viên'), ('department', 'Phòng ban'), ('job_position', 'Vị trí công việc')],
        string="Loại khen thưởng", states={'draft': [('readonly', False)]}, readonly=True)
    employee_ids = fields.Many2many('hr.employee', 'hr_employee_laudatory', 'laudatory', 'employee',
                                    domain="[('company_id', '=', company_id)]", states={'draft': [('readonly', False)]}, readonly=True,
                                    string='Nhân viên')
    department_ids = fields.Many2many('hr.department', 'hr_department_laudatory', 'laudatory', 'department',
                                      domain="[('company_id', '=', company_id)]", states={'draft': [('readonly', False)]}, readonly=True,
                                      string='Phòng ban')
    position_ids = fields.Many2many('hr.job', 'hr_job_position_laudatory', 'laudatory', 'job_position',
                                    string='Vị trí công việc', states={'draft': [('readonly', False)]}, readonly=True)
    company_id = fields.Many2one('res.company', string='Công ty',
                                 default=lambda self: self.env.user.company_id)
    reward_reason = fields.Char(string='Reward reason', states={'draft': [('readonly', False)]}, readonly=True)
    attachment_ids = fields.Many2many('ir.attachment', string="File đính kèm",
                                      help="Employee can submit any documents which supports their explanation")
    state = fields.Selection([
        ('draft', 'Dự Thảo'),
        ('action', 'Xác nhận'),
        ('cancel', 'Cancelled'),
    ], default='draft', string="Trạng thái", tracking=True)
    action_information = fields.Html(string="Action Information", states={'draft': [('readonly', False)]}, readonly=True)

    def confirm(self):
        self.state = 'action'

    def cancel(self):
        self.state = 'cancel'









