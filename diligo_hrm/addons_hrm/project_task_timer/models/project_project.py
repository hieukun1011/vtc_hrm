# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
##############################################################################
from collections import defaultdict
from lxml import etree
from lxml.html import builder as html

from odoo import api, fields, models, _,tools
from odoo.exceptions import ValidationError
from datetime import timedelta
from odoo.exceptions import UserError

class ProjectPhase(models.Model):
    _name = 'project.task.phase'
    _description = 'Task Phase'
    _order = 'sequence'
    
    name = fields.Char(string='Phase Name')
    sequence = fields.Integer(string='Sequence')
    project_id = fields.Many2one('project.project',string='Project',default=lambda self: self.env.context.get('default_project_id'))
    start_date = fields.Date(string='Start Date', copy=False)
    end_date = fields.Date(string='End Date', copy=False)
    company_id = fields.Many2one('res.company',string='Company',default=lambda self: self.env['res.company']._company_default_get())
    user_id = fields.Many2one('res.users', string='Assignees', default=lambda self: self.env.uid)
    task_count = fields.Integer(compute="get_task",string='Count')
    notes = fields.Text(string='Notes')

    def action_project_phase_task(self):
        self.ensure_one()
        return {
            'name': 'Tasks',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'project.task',
            'domain': [('phase_id', '=', self.id)],
        }

    def get_task(self):
        for rec in self:
            records = self.env['project.task'].search([('phase_id','=',rec.id)])
            rec.task_count = len(records)

class Task(models.Model):
    _inherit = 'project.task'    
    
    phase_id = fields.Many2one('project.task.phase', string='Project Phase')
    user_id = fields.Many2one('res.users', string='Assignee', default=lambda self: self.env.uid)
    date_start = fields.Datetime(string='Start Date')
    date_end = fields.Datetime(string='Ending Date', index=True, copy=False)
    date_deadline = fields.Date(string='Deadline', index=True, copy=False, tracking=True, task_dependency_tracking=True, required=True)
    child_ids = fields.One2many('project.task', 'parent_id', string="Sub-tasks", readonly=0)
    user_assigned = fields.Many2many("res.users", related="user_ids")
    end_date = fields.Date(string='Ending Date')
    manager_ids = fields.Many2many('res.users', column1='task_id', column2='manager_id',
        string='Project Manager', default=lambda self: self.env.user, context={'active_test': False})
    create_date = fields.Date(readonly=True)

    def _message_auto_subscribe_followers(self, updated_values, default_subtype_ids):
        if 'user_ids' and 'manager_ids' not in updated_values:
            return []
        # Since the changes to user_ids becoming a m2m, the default implementation of this function
        #  could not work anymore, override the function to keep the functionality.
        new_followers = []
        # Normalize input to tuple of ids
        value = self._fields['user_ids'].convert_to_cache(updated_values.get('user_ids', []), self.env['project.task'],
                                                          validate=False)
        value2 = self._fields['manager_ids'].convert_to_cache(updated_values.get('manager_ids', []), self.env['project.task'],
                                                          validate=False)
        users = self.env['res.users'].browse(value)
        for user in users:
            try:
                if user.partner_id:
                    # The you have been assigned notification is handled separately
                    new_followers.append((user.partner_id.id, default_subtype_ids, False))
            except:
                pass
        users2 = self.env['res.users'].browse(value2)
        for user in users:
            try:
                if users2.partner_id:
                    # The you have been assigned notification is handled separately
                    new_followers.append((users2.partner_id.id, default_subtype_ids, False))
            except:
                pass
        return new_followers

    @api.constrains('date_start', 'date_deadline')
    def check_end_date_and_start_date(self):
        for record in self:
            if record.date_deadline and record.date_start:
                if record.date_deadline < record.date_start.date():
                    raise UserError('Ngày hạn chót không thể bé hơn ngày bắt đầu.')


class ProjectProject(models.Model):
    _inherit = 'project.project'

    project_phase_count = fields.Integer('Job Note', compute='_get_project_phase_count')
    project_priority_count = fields.Integer(compute='_compute_priority_count', string="Task Count")
    project_priority_count_with_subtasks = fields.Integer(compute='_compute_task_count')
    deadline_count = fields.Integer(compute='_compute_deadline_count', string="DeadLine")
    deadline_count_with_subtasks = fields.Integer(compute='_compute_deadline_count')
    user_id2 = fields.Many2many('res.users', string='Project Manager', default=lambda self: self.env.user,
                                tracking=True)
    department_ids = fields.Many2one('hr.department', string='Phòng ban', compute='_compute_department_id', store=True)
    # total_task_complete = fields.Integer('Total task complete', compute='calculate_task_compute', store=True)
    #
    # @api.depends('task_ids')
    # def calculate_task_compute(self):
    #     for record in self:
    #         record.total_task_complete = self.env['project.task'].sudo().search_count([('project_id', '=', record.id), ('state')])

    @api.depends('user_id')
    def _compute_department_id(self):
        for item in self.filtered('user_id.department_id'):
            item.department_ids = item.user_id.department_id

    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Number of documents attached")
    follow_count = fields.Integer(compute='_compute_follower_count')

    def _compute_follower_count(self):
        for item in self:
            follow = self.env['mail.followers'].search_read([('res_model', '=', 'project.task'), ('res_id', 'in', item.task_ids.ids)], ['partner_id'])
            lst = []
            for key in follow:
                if key['partner_id'][0] not in lst:
                    lst.append(key['partner_id'][0])
            item.follow_count = len(lst)

    def _compute_attached_docs_count(self):
        Attachment = self.env['ir.attachment']
        for project in self:
            project.doc_count = Attachment.search_count([
                '|',
                '&',
                ('res_model', '=', 'project.project'), ('res_id', '=', project.id),
                '&',
                ('res_model', '=', 'project.task'), ('res_id', 'in', project.task_ids.ids)
            ])


    def _compute_priority_count(self):
        task_data = self.env['project.task'].read_group(
            [('project_id', 'in', self.ids),
             '|',
             ('stage_id.fold', '=', False),
             ('stage_id', '=', False),
             ('priority', '=', '1')],
            ['project_id', 'display_project_id:count'], ['project_id'])
        result_wo_subtask = defaultdict(int)
        result_with_subtasks = defaultdict(int)
        for data in task_data:
            result_wo_subtask[data['project_id'][0]] += data['display_project_id']
            result_with_subtasks[data['project_id'][0]] += data['project_id_count']
        for project in self:
            project.project_priority_count = result_wo_subtask[project.id]
            project.project_priority_count_with_subtasks = result_with_subtasks[project.id]


    def _compute_deadline_count(self):
        days = fields.Date.today() + timedelta(days=2)
        task_data = self.env['project.task'].read_group(
            [('project_id', 'in', self.ids),
             '|',
             ('stage_id.fold', '=', False),
             ('stage_id', '=', False),
             ('date_deadline', '<', days),
             ('date_deadline', '>', fields.Date.today())],
            ['project_id', 'display_project_id:count'], ['project_id'])
        result_wo_subtask = defaultdict(int)
        result_with_subtasks = defaultdict(int)
        for data in task_data:
            result_wo_subtask[data['project_id'][0]] += data['display_project_id']
            result_with_subtasks[data['project_id'][0]] += data['project_id_count']
        for project in self:
            project.deadline_count = result_wo_subtask[project.id]
            project.deadline_count_with_subtasks = result_with_subtasks[project.id]

    # @api.depends('date_deadline')
    # def _cal_task_deadline(self):
    #     task_dateline = self.env('project.task')
    #     for date_deadline in task_dateline:
    #         if


    def _get_project_phase_count(self):
        for project_phase in self:
            project_phase_ids = self.env['project.task.phase'].search([('project_id','=',project_phase.id)])
            project_phase.project_phase_count = len(project_phase_ids)

    def action_project_phase(self):
        self.ensure_one()
        return {
            'name': 'Phases',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'project.task.phase',
            'domain': [('project_id', '=', self.id)],
        }
        

class ReportProjectTaskUser(models.Model):
    _inherit = "report.project.task.user"
    _description = "Tasks Analysis"

    phase_id = fields.Many2one('project.task.phase', string='Project Phase', readonly=True)


    def _select(self):
        select_str = """
             SELECT
                    (select 1 ) AS nbr,
                    t.id as id,
                    t.id as task_id,
                    t.create_date as create_date,
                    t.date_assign as date_assign,
                    t.date_end as date_end,
                    t.date_last_stage_update as date_last_stage_update,
                    t.date_deadline as date_deadline,
                    t.project_id,
                    t.phase_id,
                    t.priority,
                    t.name as name,
                    t.company_id,
                    t.partner_id,
                    t.stage_id as stage_id,
                    t.kanban_state as state,
                    NULLIF(t.rating_last_value, 0) as rating_last_value,
                    t.working_days_close as working_days_close,
                    t.working_days_open  as working_days_open,
                    t.working_hours_open as working_hours_open,
                    t.working_hours_close as working_hours_close,
                    (extract('epoch' from (t.date_deadline-(now() at time zone 'UTC'))))/(3600*24)  as delay_endings_days
        """
        return select_str


    def _group_by(self):
        group_by_str = """
                GROUP BY
                    t.id,
                    t.create_date,
                    t.write_date,
                    t.date_assign,
                    t.date_end,
                    t.date_deadline,
                    t.date_last_stage_update,
                    t.project_id,
                    t.phase_id,
                    t.priority,
                    t.name,
                    t.company_id,
                    t.partner_id,
                    t.stage_id
        """
        return group_by_str

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE view %s as
              %s
              FROM project_task t
              LEFT JOIN project_task_user_rel tu on t.id=tu.task_id
                WHERE t.active = 'true'
                %s
        """ % (self._table, self._select(), self._group_by()))
    


