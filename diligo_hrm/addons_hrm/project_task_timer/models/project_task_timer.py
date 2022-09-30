# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2017-TODAY Cybrosys Technologies(<http://www.cybrosys.com>).
#    Author: Jesni Banu(<http://www.cybrosys.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class ProjectTaskTimeSheet(models.Model):
    _inherit = 'account.analytic.line'

    date_start = fields.Datetime(string='Start Date')
    date_end = fields.Datetime(string='End Date', readonly=False)
    timer_duration = fields.Float(invisible=1, string='Time Duration (Minutes)')
    set_time = fields.Many2one('project.task', 'date_end')


class ProjectTaskTimer(models.Model):
    _inherit = 'project.task'

    task_timer = fields.Boolean(string='Timer', default=False)
    is_user_working = fields.Boolean(
        'Is Current User Working', compute='_compute_is_user_working',
        help="Technical field indicating whether the current user is working. ")
    duration = fields.Float(
        'Real Duration', compute='_compute_duration', store=True)
    description = fields.Text('Description', tracking=True)

    def _compute_duration(self):
        self

    def _compute_is_user_working(self):
        """ Checks whether the current user is working """
        for order in self:
            if order.timesheet_ids.filtered(lambda x: (x.user_id.id == self.env.user.id) and (not x.date_end)):
                order.is_user_working = True
            else:
                order.is_user_working = False

    # @api.model
    # @api.constrains('task_timer')
    # def toggle_start(self):
    #     print('vkenivne')
    #     if self.task_timer is True:
    #         self.write({'is_user_working': True})
    #         time_line = self.env['account.analytic.line']
    #         for time_sheet in self:
    #             time_line.create({
    #                 'name': self.env.user.name + ': ' + time_sheet.name,
    #                 'task_id': time_sheet.id,
    #                 'user_id': self.env.user.id,
    #                 'project_id': time_sheet.project_id.id,
    #                 'date_start': datetime.now(),
    #             })
    #     else:
    #         self.write({'is_user_working': False})
    #         time_line_obj = self.env['account.analytic.line']
    #         domain = [('task_id', 'in', self.ids), ('date_end', '=', False)]
    #         for time_line in time_line_obj.search(domain):
    #             time_line.write({'date_end': fields.Datetime.now()})
    #             if time_line.date_end:
    #                 diff = fields.Datetime.from_string(time_line.date_end) - fields.Datetime.from_string(time_line.date_start).replace(microsecond=0)
    #                 time_line.timer_duration = round(diff.total_seconds() / 60.0, 2)
    #                 time_line.unit_amount = round(diff.total_seconds() / (60.0 * 60.0), 2)
    #             else:
    #                 time_line.unit_amount = 0.0
    #                 time_line.timer_duration = 0.0

    @api.model
    def _task_message_auto_subscribe_notify(self, users_per_task):
        # Utility method to send assignation notification upon writing/creation.
        template_id = self.env['ir.model.data']._xmlid_to_res_id('project_task_timer.project_message_user_assigned',
                                                                 raise_if_not_found=False)
        if not template_id:
            return
        view = self.env['ir.ui.view'].browse(template_id)
        task_model_description = self.env['ir.model']._get(self._name).display_name
        for task, users in users_per_task.items():
            if not users:
                continue
            values = {
                'object': task,
                'model_description': task_model_description,
                'access_link': task._notify_get_action_link('view'),
            }
            for user in users:
                values.update(assignee_name=user.sudo().name)
                assignation_msg = view._render(values, engine='ir.qweb', minimal_qcontext=True)
                assignation_msg = self.env['mail.render.mixin']._replace_local_links(assignation_msg)
                task.message_notify(
                    subject=_('Nội dung công việc %s', task.display_name),
                    body=assignation_msg,
                    partner_ids=user.partner_id.ids,
                    record_name=task.display_name,
                    email_layout_xmlid='mail.mail_notification_light',
                    model_description=task_model_description,
                )




