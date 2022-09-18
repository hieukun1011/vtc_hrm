from odoo import api, fields, models
from odoo.exceptions import ValidationError
import datetime
# import time

class ProjectMission(models.Model):

    _inherit = "project.task"

    _sql_constraints = [
        ('check_date',
         'CHECK (date_start <= date_end)',
         'Rule date start can not larger than date end!'),
    ]

    note_bug = fields.Text(string='Note bug')
    mission_status = fields.Text(string='Mission status')
    date_start = fields.Datetime(string='Start Date')
    date_deadline = fields.Date(string='Deadline', index=True, copy=False, tracking=True, task_dependency_tracking=True,
                                help='Date deadline must larger than date end')
    date_receive = fields.Datetime(string='Date receive', default=fields.Datetime.now)
    child_2_ids = fields.One2many('project.task', 'parent_id',
                                    help='Use to view tab')
    description1 = fields.Text('Description')




