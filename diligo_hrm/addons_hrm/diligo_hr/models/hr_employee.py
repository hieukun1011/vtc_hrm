from odoo import fields, models, api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
import re
from odoo.exceptions import UserError

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_id = fields.Char(string='ID Employee')
    employee_code = fields.Char('ID Employee Old')
    state = fields.Selection([
        ('working', 'Đang Làm Việc'),
        ('maternity', 'Nghỉ thai sản'),
        ('terminated', 'Nghỉ Việc'),
        ('unpaid_leave', 'Nghỉ không lương'),
    ], required=True, default='working')
    work_location = fields.Char('Work Location')
    position_id = fields.Many2one('hr.job.position', string='Position')
    position = fields.Char(string='Internal position')
    issue_date = fields.Date(string='Issue date')
    id_issue_place = fields.Char(string='Issue place')
    emergency_address = fields.Char(string='Emergency address')
    mst_account_id = fields.Char(string='Personal tax code')
    bank_number = fields.Char(string='Bank account number')
    # joining_date = fields.Date('Joining Date', default=datetime.now().date())
    work_duration = fields.Char('Thâm niên', compute='_get_work_duration')
    resign_date = fields.Date('Ngày từ chức', readonly=True)
    tz = fields.Selection('_tz_get', string='Timezone', required=True, default='Asia/Ho_Chi_Minh')
    email = fields.Char('Email')
    graduation_year = fields.Char('graduation year')
    classification = fields.Char('classification')
    channel_id = fields.Many2one('hr.channel', string='Kênh')
    work_duration = fields.Char('Seniority', compute='_get_work_duration')
    group_job = fields.Many2one('hr.group.job', string='Bộ phận', help='Chọn bộ phận nhóm vị trí',
                                related='job_id.group_job')
    stages_history = fields.One2many('hr.employee.status.history', 'employee_id', string='Stage History',
                                     help='It shows the duration and history of each stages')
    res_country_state = fields.Many2one('res.country.state', string='Country state', domain="[('country_id', '=', 'VN')]")
    res_country_ward = fields.Many2one('res.country.ward', string='Country ward')
    res_country_district = fields.Many2one('res.country.district', string='Country district')
    apartment_number = fields.Char('Apartment number')
    address_home = fields.Char('Address home')
    bank_account = fields.Char('Bank account ')
    bank = fields.Char('Ngân hàng quân đội MB Bank')
    bank_branch = fields.Char('Chi nhánh')
    bank_account_agri = fields.Char('Bank account')
    bank_agri = fields.Char('Ngân hàng Agribank')
    bank_branch_agri = fields.Char('Bank branch')
    is_official = fields.Boolean('Is official')
    area = fields.Selection(related='channel_id.area', string='Area')
    area_manager = fields.Many2many('hr.channel', string='Area manager')
    _sql_constraints = [
        ('employee_id_uniq', 'unique (employee_id)', 'Employee code already exists!'),
        ('employee_email_uniq', 'unique (work_email)', 'Employees corporate email already exists!')
    ]


    @api.depends('job_id')
    def _compute_job_title(self):
        for employee in self.filtered('job_id'):
            employee.job_title = employee.job_id.position_id.name
            employee.position = employee.job_id.name

    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            '[employee_id]': None,
            '[work_email]': None,
        })
        return super(HrEmployee, self).copy(default)

    @api.depends('department_id', 'job_id')
    def _compute_parent_id(self):
        for employee in self.filtered('department_id.manager_id'):
            employee.parent_id = employee.department_id.manager_id
        for employee in self.filtered('job_id.hr_responsible_id'):
            employee.parent_id = employee.job_id.hr_responsible_id

    @api.constrains('res_country_state', 'res_country_ward', 'res_country_district')
    def render_address_home(self):
        self.address_home = ''
        if self.apartment_number:
            self.address_home += str(self.apartment_number) + ', '
        if self.res_country_ward:
            self.address_home += str(self.res_country_ward.name) + ', '
        if self.res_country_district:
            self.address_home += str(self.res_country_district.name) + ', '
        if self.res_country_state:
            self.address_home += str(self.res_country_state.name)
        self.address_home += ', Việt Nam'

    @api.onchange('department_id')
    def onchange_department_id(self):
        if self.department_id:
            sequence = self.env['ir.sequence'].next_by_code('diligo_employee_code_action')
            if not self.employee_id and self.department_id:
                self.employee_id = 'DC' + str(self.department_id.root_code) + str(sequence)
            self.job_id = False
            return {
                'domain': {'job_id': [('department_id', '=', self.department_id.id)]}
            }

    @api.depends('joining_date', 'resign_date')
    def _get_work_duration(self):
        for item in self:
            if item.resign_date:
                duration = relativedelta(item.resign_date, item.joining_date)
            else:
                duration = relativedelta(date.today(), item.joining_date)
            y = str(duration.years) + (' năm', ' năm')[duration.years > 1]
            m = str(duration.months) + (' tháng', ' tháng')[duration.months > 1]
            d = str(duration.days) + (' ngày', ' ngày')[duration.days > 1]
            item.work_duration = '%s %s %s' % (('', y)[duration.years > 0],
                                               ('', m)[duration.months > 0],
                                               ('', d)[duration.days > 0])

    @api.onchange('email', 'work_email', 'mobile_phone', 'identification_id', 'bank_account',)
    def validate_mail(self):
        if self.email:
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,3})$', self.email)
            if match == None:
                raise ValidationError(_('Enter the wrong email format!'))
        if self.work_email:
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,3})$', self.work_email)
            if match == None:
                raise ValidationError (_('Import bad job email format!'))
        if self.mobile_phone:
            # match = re.match('^[0]*(\.[0-9]\d{8,9})$', self.mobile_phone)
            match = re.match("^[0-9]\d{9}$", self.mobile_phone)
            if match == None:
                raise ValidationError (_('Please enter the correct phone number!'))
        if self.identification_id:
            match = re.match("[0-9]",  self.identification_id)
            if match == None:
                raise ValidationError (_('Please enter the correct ID number!'))
        if self.bank_account:
            match = re.match("[0-9]", self.bank_account)
            if match == None:
                raise ValidationError (_('Please enter the correct bank account number!'))

    @api.onchange('emergency_phone')
    def _emergency(self):
        if self.emergency_phone:
            match = re.match("^[0-9]\d{9}$", self.emergency_phone)
            if match == None:
                raise ValidationError (_('Please enter the correct phone number!'))

    @api.depends('joining_date', 'resign_date')
    def _get_work_duration(self):
        for item in self:
            if item.resign_date:
                duration = relativedelta(item.resign_date, item.joining_date)
            else:
                duration = relativedelta(date.today(), item.joining_date)
            y = str(duration.years) + (' năm', ' năm')[duration.years > 1]
            m = str(duration.months) + (' tháng', ' tháng')[duration.months > 1]
            d = str(duration.days) + (' ngày', ' ngày')[duration.days > 1]
            item.work_duration = '%s %s %s' % (('', y)[duration.years > 0],
                                               ('', m)[duration.months > 0],
                                               ('', d)[duration.days > 0])
    @api.onchange('birthday')
    def _check_day(self):
        if self.birthday and self.birthday > datetime.now().date():
            return {'warning':{
                'title' : _("Warning"),
                'message': _("Please choose the correct date of birth!")
            }}

    @api.onchange('birth_date')
    def _check_date(self):
        if self.birth_date and self.birth_date > datetime.now().date():
            return {'warning': {
                'title': _("Warning"),
                'message': _("You are not allowed to enter more than the current date!")
            }}

    @api.onchange('issue_date')
    def _check_date(self):
        if self.issue_date and self.issue_date > datetime.now().date():
            return {'warning':{
                'title' : _("Warning"),
                'message': _("You are not allowed to enter more than the current date!")
            }}


    # def onchange_channel(self):
    #     sequence = self.env['ir.sequence'].next_by_code('diligo_employee_code_action')
    #     if not self.employee_id and self.channel_id:
    #         self.employee_id = str(self.channel_id.code) + str(sequence)




    @api.model
    def create(self, vals):
        result = super(HrEmployee, self).create(vals)
        result.stages_history.sudo().create({'start_date': date.today(),
                                             'employee_id': result.id,
                                             'state': 'working'})
        if result.work_email:
            partner = self.env['res.partner'].sudo().search([('email', '=', result.work_email)], limit=1)
            if not partner:
                result.user_partner_id.sudo().create({
                    'name': result.name,
                    'email': result.work_email,
                    'phone': result.work_phone,
                    'employee_ids': [result.id],
                })
            else:
                result.user_partner_id = partner
        return result

    @api.constrains('work_email')
    def create_partner_employee(self):
        if self.work_email:
            partner = self.env['res.partner'].sudo().search([('employee_ids', '=', [self.id])])
            if not partner:
                partner_id = self.env['res.partner'].create({
                    'name': self.name,
                    'email': self.work_email,
                    'phone': self.work_phone,
                    'employee_ids': [self.id],
                })
                self.user_partner_id = partner_id
            else:
                if partner.email != self.work_email:
                    partner.write({
                        'email': self.work_email,
                    })

    @api.onchange('km_home_work')
    def _check_value(self):
         if self.km_home_work < 0:
             raise ValidationError (_('You need to enter a positive value!'))

    def write(self, vals):
        if not self.employee_id:
            sequence = self.env['ir.sequence'].next_by_code('diligo_employee_code_action')
            vals['employee_id'] = 'DC' + str(self.department_id.root_code) + str(sequence)
        return super(HrEmployee, self).write(vals)

    def diligo_create(self):
        if not self.user_id:
            if not self.work_email:
                raise UserError (_('Please fill work email address before creating an account.'))
            else:
                user = self.env['res.users'].sudo().create({'name': self.name,
                                                            'image_1920': self.image_1920,
                                                            'login': self.work_email,
                                                            'email': self.work_email})
                self.user_id = user.id
                view = self.env.ref('sh_message.sh_message_wizard')
                view_id = view and view.id or False
                context = dict(self._context or {})
                context['message'] = _('Account has been created successfully!')
                return {
                    'name': 'Success',
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sh.message.wizard',
                    'views': [(view_id, 'form')],
                    'view_id': view.id,
                    'target': 'new',
                    'context': context,
                }
        else:
            return {
                'name': 'User',  # Lable
                'res_id': self.user_id.id,
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': self.env.ref('base.view_users_form').id,
                'res_model': 'res.users',  # your model
                'target': 'new',  # if you want popup
                # 'context': "{'generic_request_id': uid}",  # if you need
            }

class EmployeeStageHistory(models.Model):
    _name = 'hr.employee.status.history'
    _description = 'Status History'

    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    duration = fields.Integer(compute='get_duration', string='Duration(days)')

    def get_duration(self):
        self.duration = 0
        for each in self:
            if each.end_date and each.start_date:
                duration = fields.Date.from_string(each.end_date) - fields.Date.from_string(each.start_date)
                each.duration = duration.days

    state = fields.Selection([
        ('working', 'Đang Làm Việc'),
        ('maternity', 'Nghỉ thai sản'),
        ('terminated', 'Nghỉ Việc'),
        ('unpaid_leave', 'Nghỉ không lương'),
    ], required=True, default='working')
    employee_id = fields.Many2one('hr.employee', invisible=1)

