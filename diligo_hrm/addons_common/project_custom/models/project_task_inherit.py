from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import datetime
from datetime import timedelta
# import time

class ProjectMission(models.Model):

    _inherit = "project.task"

    _sql_constraints = [
        ('check_date',
         'CHECK (date_start <= date_end)',
         'Rule date start can not larger than date end!'),
    ]

    # description_detail = fields.Text(string='Mission detail',)
    # user_id = fields.Many2one('hr.employee', string='Dev')
    # dev_id = fields.Many2one('hr.employee', string='Dev')
    # tester_id = fields.Many2one('hr.employee', string='Tester')
    # task_recipient_ids = fields.Many2many('', string='Task recipient')
    note_bug = fields.Text(string='Note bug')
    mission_status = fields.Text(string='Mission status')
    # is_dev= fields.Boolean(string='Is dev or not', default=False)

    date_start = fields.Datetime(string='Start Date')
    date_deadline = fields.Date(string='Deadline', index=True, copy=False, tracking=True, task_dependency_tracking=True, default=fields.Date.today,
                                help='Date deadline must larger than date end')
    date_receive = fields.Datetime(string='Date receive', default=fields.Datetime.now)

    child_2_ids = fields.One2many('project.task', 'parent_id',
                                    help='Use to view tab')
    is_due_soon = fields.Boolean('Is due soon', default=False, compute='_compute_is_due_soon',)
    user_ids = fields.Many2many('res.users', relation='project_task_user_rel', column1='task_id', column2='user_id',
                                string='Assignees',
                                context={'active_test': False}, tracking=True, compute='_compute_user_ids', store=True)

    # child_dev_ids= fields.One2many('project.task', 'parent_id', string='Child dev', domain=[('is_dev', '=', True)], help='Use to view dev tab')
    # child_tester_ids = fields.One2many('project.task', 'parent_id', string='Child tester',
    #                                 help='Use to view tester tab')  #domain=[('is_dev', '=', False)],

    # người được giao onchange theo người nhận nhiệm vụ
    @api.depends('child_2_ids.user_id')
    def _compute_user_ids(self):
        if self.child_2_ids:
            self.user_ids = self.child_2_ids.user_id

    # ràng buộc ngày hạn chót phải không được nhỏ hơn ngày kết thúc kế hoạch
    @api.constrains('date_end', 'date_deadline')
    def _constrains_date_end_and_date_dealine(self):
        for rec in self:
            if rec.date_end and rec.date_deadline:
                if rec.date_deadline < rec.date_end.date():
                    raise ValidationError("Date deadline is not less than end date")

    # chỉ người đc phân công và người quản lý, admin được phép thay đổi trạng thái dự án
    @api.onchange('stage_id')
    def rule_change_stage(self):
        if not self.env.user.has_group('base.group_system'):
            if self.env.uid not in self.user_ids.ids and self.env.uid not in self.manager_ids.ids and self.env.uid != self.user_id.id:
                raise ValidationError(_('Bạn không được quyền thay đổi trạng thái công việc này.'))

    @api.depends('date_deadline')
    def _compute_is_due_soon(self):
        days = fields.Date.today() + timedelta(days=1)
        for rec in self:
            if rec.date_deadline == days:
                rec.is_due_soon = True
            else:
                rec.is_due_soon = False

    # @api.model
    # def create(self, vals):
    #     if 'date_end' and 'date_deadline' in vals:
    #         print('tao date end and date deadline')
    #         if vals['date_deadline'] < vals['date_end'].date():
    #             raise ValidationError("Date deadline is not less than end date")
    #
    #     return super(ProjectMission, self).create(vals)

    def write(self, vals):
        model_id = self.env['ir.model'].sudo().search([('model', '=', 'project.task')]).id
        for rec in self:
            res_id = rec.id
            if 'user_ids' in vals:
                users = vals['user_ids'][0][2]
            else:
                users = rec.user_ids.ids
            if 'manager_ids' in vals:
                managers = vals['manager_ids'][0][2]
            else:
                managers = rec.manager_ids.ids
            if 'date_deadline' in vals:
                deadline = vals['date_deadline']
            else:
                deadline = rec.date_deadline
            if 'name' in vals:
                summary_user = 'You are a assignee in project {}'.format(vals['name'])
                summary_manager = 'You are a manager in project {}'.format(vals['name'])
            else:
                summary_user = 'You are a assignee in project {}'.format(rec.name)
                summary_manager = 'You are a manager in project {}'.format(rec.name)

            mails = self.env['mail.activity'].search([('res_model_id', '=', model_id), ('res_id', '=', res_id)])
            # tạo mail nếu chưa có mail
            if not mails:
                # tạo mail cho users
                for user in users:
                    self.env['mail.activity'].create({
                        'res_model_id': model_id,
                        'res_id': res_id,
                        'activity_type_id': 4,
                        'user_id': user,
                        'date_deadline': deadline,
                        'summary': summary_user,
                    })
                # tạo mail cho managers
                for manager in managers:
                    self.env['mail.activity'].create({
                        'res_model_id': model_id,
                        'res_id': res_id,
                        'activity_type_id': 4,
                        'user_id': manager,
                        'date_deadline': deadline,
                        'summary': summary_manager,
                    })

            # nếu đã có mail rồi thì sửa mail
            else:
                if 'date_deadline' in vals:
                    # print('date deadline', vals['date_deadline'])
                    deadline = vals['date_deadline']
                    mails.write({
                        'date_deadline': deadline
                    })

                if 'user_ids' in vals:
                    all_users = vals['user_ids'][0][2]
                    # tìm kiếm users chưa được tạo mail
                    # have_mails = mails.filtered(lambda all_users: 'user_id' in all_users)
                    has_mails = mails.user_id
                    users_no_mail = [x for x in all_users if x not in set(has_mails.ids)]
                    # print('user no mail', users_no_mail)
                    for user in users_no_mail:
                        self.env['mail.activity'].create({
                            'res_model_id': model_id,
                            'res_id': res_id,
                            'activity_type_id': 4,
                            'user_id': user,
                            'date_deadline': deadline,
                            'summary': summary_user,
                        })

                if 'manager_ids' in vals:
                    all_managers = vals['manager_ids'][0][2]
                    has_mails = mails.user_id
                    managers_no_mail = [x for x in all_managers if x not in set(has_mails.ids)]
                    # print('user no mail', managers_no_mail)
                    for manager in all_managers:
                        self.env['mail.activity'].create({
                            'res_model_id': model_id,
                            'res_id': res_id,
                            'activity_type_id': 4,
                            'user_id': manager,
                            'date_deadline': deadline,
                            'summary': summary_manager,
                        })

        return super(ProjectMission, self).write(vals)

    def send_mail_to_users(self):
        users = self.user_ids.ids + self.manager_ids.ids
        # print('users    ', type(users), users)
        return {
            'type': 'ir.actions.act_window',
            'name': _('Send mail'),
            'res_model': 'project.task.send.mail',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_user_ids': users, 'default_project_name': self.name,'active_test': False},
            'views': [[False, 'form']]
        }

# class ResUsersInherit(models.Model):
#     _name = "res.users"
#
#     _inherit = ['res.users', 'mail.thread']

