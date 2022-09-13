# -*- coding: utf-8 -*-

from odoo import fields, api, models
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
from odoo import fields, api, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import date, datetime, time
from calendar import monthrange
import base64
from io import BytesIO
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
from collections import defaultdict
from odoo.tools.misc import get_lang
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from base64 import b64decode
from xlrd import open_workbook
from odoo import fields, api, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import date, datetime, time
from calendar import monthrange
from openpyxl import load_workbook
from openpyxl.styles import Font, borders, Alignment
import base64
from io import BytesIO
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import re
try:
    import xlrd
    try:
        from xlrd import xlsx
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None

try:
    from . import odf_ods_reader
except ImportError:
    odf_ods_reader = None

from odoo.addons.base.models.res_partner import _tz_get

class Applicant(models.Model):
    _inherit = "hr.applicant"

    priority = fields.Selection(
        [('0', 'Rất thấp'), ('1', 'Thấp'), ('2', 'Bình thường'), ('3', 'Tốt'), ('4', 'Rất tốt'),
         ('5', 'Tuyệt vời')], "Appreciation", default='0')
    recruit_period = fields.Many2one('hr.recruitment.period', 'Recruitment period', compute='_get_recruit_period',
                                     store=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')], string='Giới tính',
                              default="male")
    birthday = fields.Date('Ngày sinh')
    address = fields.Char('Địa chỉ')
    qualification = fields.Char('Trình độ(kinh nghiệm)')
    college = fields.Char('Trường học')
    last_workplace = fields.Char('Nơi làm việc gần nhất')
    workplace = fields.Char('Tỉnh/thành muốn làm việc')
    social_facebook = fields.Char('Facebook')
    applicant_state = fields.One2many('hr.applicant.state', 'applicant_id', 'Giai đoạn')
    marital = fields.Selection([
        ('single', 'Chưa kết hôn'),
        ('married', 'Đã kết hôn'),
        ('divorced', 'Ly hôn')
    ], string='Tình trạng hôn nhân', groups="hr.group_hr_user", default='single')
    salary_expected = fields.Integer("Mức lương mong đợi", help="Salary Expected by Applicant")
    salary_proposed = fields.Integer("Mức lương đề xuất", help="Salary Proposed by the Organisation")
    created_date = fields.Datetime("Ngày tạo", default=fields.Datetime.now())

    @api.model
    def create(self, vals):
        res = super(Applicant, self).create(vals)
        template = self.env.ref('diligo_hr.email_template_data_applicant')
        self.env['mail.thread'].message_post_with_template(
            template.id,
            res_id=res.id,
            model=res._name,
            composition_mode='comment',
        )
        return res

    @api.onchange('partner_phone', 'partner_mobile')
    def validate_phone(self):
        if self.partner_phone:
            match = re.match("^[0-9]\d{9}$", self.partner_phone)
            if match == None:
                raise ValidationError(_('Please enter the correct phone number!'))
        if self.partner_mobile:
            match = re.match("^[0-9]\d{9}$", self.partner_mobile)
            if match == None:
                raise ValidationError(_('Please enter the correct phone number!'))


    @api.depends('job_id')
    def _compute_department(self):
        for applicant in self:
            if not applicant.department_id:
                applicant.department_id = applicant.job_id.department_id

    @api.depends('job_id', 'department_id')
    def _compute_company(self):
        for applicant in self:
            company_id = False
            if applicant.department_id:
                company_id = applicant.department_id.company_id.id
            else:
                applicant.department_id = applicant.job_id.department_id
            if not company_id and applicant.job_id:
                company_id = applicant.job_id.company_id.id
            applicant.company_id = company_id or self.env.company.id

    @api.onchange('birthday')
    def check_birthday_applicant(self):
        if self.birthday and self.birthday > date.today():
            raise UserError(_('Ngày sinh ứng viên không hợp lệ.'))

    def reset_applicant(self):
        """ Reinsert the applicant into the recruitment pipe in the first stage"""
        default_stage = dict()
        for job_id in self.mapped('job_id'):
            default_stage[job_id.id] = self.env['hr.recruitment.stage'].search(
                ['|',
                    ('job_ids', '=', False),
                    ('job_ids', '=', job_id.id),
                    ('fold', '=', False)
                ], order='sequence asc', limit=1).id
        for applicant in self:
            applicant.write(
                {'stage_id': applicant.job_id.id and default_stage[applicant.job_id.id],
                 'refuse_reason_id': False,
                 'active': True
                 })

    @api.constrains('stage_id')
    def create_hr_applicant_state(self):
        if self.email_from:
            ctx = {
                'default_applicant_id': self.id,
            }
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'hr.applicant.state',
                'views': [[self.env.ref('diligo_hr.hr_applicant_state_view_form').id, 'form']],
                # 'view_mode': 'form',
                'target': 'new',
                'context': ctx,
            }
        else:
            raise UserError(_('Vui lòng nhập email ứng viên.'))


    @api.onchange('applicant_state')
    def action_change_state(self):
        for rec in self.applicant_state:
            if rec.result == 'pass':
                self.stage_id = rec.stage_id

    @api.depends('job_id')
    def _get_recruit_period(self):
        for record in self:
            if record.job_id and not record.emp_id and record.job_id.periods:
                record.recruit_period = record.job_id.periods[-1]
            else:
                record.recruit_period = False


    def create_employee_from_applicant(self):
        """ Create an hr.employee from the hr.applicants """
        employee = False
        for applicant in self:
            contact_name = False
            if applicant.partner_id:
                contact_name = applicant.partner_id.name_get()[0][1]
            else:
                new_partner_id = self.env['res.partner'].create({
                    'name': applicant.name,
                    'email': applicant.email_from,
                    'phone': applicant.partner_phone,
                    'mobile': applicant.partner_mobile
                })
            if applicant.job_id and (applicant.name or contact_name):
                applicant.job_id.write({'no_of_hired_employee': applicant.job_id.no_of_hired_employee + 1})
                employee = self.env['hr.employee'].create({
                    'name': applicant.name,
                    'job_id': applicant.job_id.id,
                    'group_job': applicant.job_id.group_job.id or False,
                    'id_attachment_id': applicant.attachment_ids,
                    'user_partner_id': applicant.user_id.id,
                    'emergency_contact': applicant.address,
                    'department_id': applicant.department_id.id or False,
                    'email': self.email_from,
                    'gender': applicant.gender,
                    'study_school': applicant.college,
                    'study_field': applicant.qualification,
                    'birthday': applicant.birthday,
                    'marital': applicant.marital,
                    'company_id': applicant.company_id.id,
                    'user_partner_id': new_partner_id,
                    'mobile_phone': self.partner_phone})
                applicant.write({'emp_id': employee.id})
                applicant.job_id.message_post(
                    body=_(
                        'New Employee %s Hired') % applicant.partner_name if applicant.partner_name else applicant.name,
                    subtype_xmlid ="hr_recruitment.mt_job_applicant_hired")

            else:
                raise UserError(_('You must define an Applied Job and a Contact Name for this applicant.'))

        dict_act_window = self.env['ir.actions.act_window']._for_xml_id('hr.open_view_employee_list')
        dict_act_window['context'] = {'form_view_initial_mode': 'edit'}
        dict_act_window['res_id'] = employee.id
        return dict_act_window

    def website_form_input_filter(self, request, values):
        if 'partner_name' in values:
            applicant_job = self.env['hr.job'].sudo().search([('id', '=', values['job_id'])]).name if 'job_id' in values else False
            values.setdefault('name', values['partner_name'])
        if values.get('job_id'):
            stage = self.env['hr.recruitment.stage'].sudo().search([
                ('fold', '=', False),
                '|', ('job_ids', '=', False), ('job_ids', '=', values['job_id']),
            ], order='sequence asc', limit=1)
            if stage:
                values['stage_id'] = stage.id
        return values


class ApplicantState(models.Model):
    _name = "hr.applicant.state"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Giai đoạn ứng viên"

    name = fields.Char('Tên kỳ phỏng vấn', compute='_get_name_stage_id', store=True)
    active = fields.Boolean("Active", default=True, related='applicant_id.active')
    applicant_id = fields.Many2one('hr.applicant', string='Ứng viên')
    stage_id = fields.Many2one('hr.recruitment.stage', string="Giai đoạn", domain=[('id', '!=', '1')])
    result = fields.Selection([('fail', 'Loại'), ('wait', 'Chờ xét thêm'), ('pass', 'Đạt')], string='Kết quả')
    partner_ids = fields.Many2many('hr.employee', string='Người phỏng vấn')
    start = fields.Datetime('Ngày bắt đầu', required=True,
                            help="Start date of an event, without time for full days events")
    stop = fields.Datetime('Ngày kết thúc', required=True,
                           help="Stop date of an event, without time for full days events")
    location = fields.Char('Địa điểm', help="Location of Event")
    description = fields.Text('Ghi chú')
    attachment_ids = fields.Many2many('ir.attachment', string='File đính kèm')
    partner_id = fields.Many2one('res.partner', string='Ứng viên', related='applicant_id.partner_id')
    user_id = fields.Many2one('res.users', string='Phụ trách', related='applicant_id.user_id')
    phone_partner = fields.Char(related='applicant_id.partner_phone', string='Số điện thoại ứng viên')
    mail_tz = fields.Selection(_tz_get, compute='_compute_mail_tz',
                               help='Timezone used for displaying time in the mail template')
    job_id = fields.Many2one(related='applicant_id.job_id')

    _sql_constraints = [
        ('applicant_stage_uniq', 'unique(applicant_id, stage_id)',
         'Đã tồn tại giai đoạn phỏng vấn với ứng viên này!!!!'),
    ]

    @api.onchange('start', 'stop')
    def validate_date_start_stop(self):
        if self.start and self.stop:
            if self.stop < self.start:
                raise ValidationError("Ngày bắt đầu không hợp lệ!!!")

    @api.model
    def create(self, vals):
        applicant_state = super(ApplicantState, self).create(vals)
        if applicant_state.result == 'pass':
            applicant_state.applicant_id.stage_id = applicant_state.stage_id
        return applicant_state

    def _compute_mail_tz(self):
        for attendee in self:
            attendee.mail_tz = attendee.partner_id.tz

    @api.depends('stage_id')
    def _get_name_stage_id(self):
        for record in self:
            if record.stage_id:
                record.name = record.stage_id.name


    def send_mail_confirm(self):
        template = self.env.ref('diligo_hr.email_template_aplicant_state')
        # template2 = self.env.ref('diligo_maintenance.email_template_data_maintenance_new')
        for record in self:
            self.env['mail.thread'].message_post_with_template(
                template.id,
                res_id=record.id,
                model=record._name,
            )

    def action_applicant_send(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data._xmlid_lookup('diligo_hr.email_template_aplicant_state')[2]
        except ValueError:
            template_id = False
        try:
            # compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
            compose_form_id = self.env.ref('email_compose_message_wizard_form').id
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'hr.applicant.state',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True
        }

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }




