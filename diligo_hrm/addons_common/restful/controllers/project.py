"""Part of odoo. See LICENSE file for full copyright and licensing details."""
import logging
from datetime import datetime

from odoo.addons.restful.common import (
    invalid_response,
    valid_response,
    valid_response_once,
)
from odoo.addons.restful.controllers.main import (
    validate_token
)
from werkzeug import urls

from odoo import http
from odoo.http import request
from werkzeug import urls
import json
import pytz

_logger = logging.getLogger(__name__)


class ProjectController(http.Controller):

    def get_url_base(self):
        config = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if config:
            return config
        return 'https://test.diligo.vn:15000'

    @validate_token
    @http.route("/api/v1/project", type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def get_project(self, **payload):
        values = []
        base_url = ProjectController.get_url_base(self)
        list_project = request.env['project.project'].search([])
        for rec in list_project:
            data = {'id': rec.id,
                    'title': rec.name or '',
                    'description': rec.description or '',
                    'date_start': rec.date_start or '',
                    'date': rec.date or '',
                    }
            favorite_user_ids = []
            for favorite in rec.task_ids:
                for u in favorite.user_ids:
                    favorite_user_ids.append({
                        'id': u.id,
                        'name': u.name,
                        'avatar': urls.url_join(base_url,
                                                '/web/image?model=res.users&id={0}&field=image_1920'.format(
                                                    u.id)),
                    })
            data['member'] = favorite_user_ids
            # list_jobs = []
            # for task in rec.task_ids:
            #     project_task = {
            #         'id': task.id,
            #         'title': task.name,
            #         'description': task.description,
            #         'phase': {'id': task.phase_id.id, 'name': task.phase_id.name} or '',
            #         'date': {'start': task.date_start, 'end': task.date_end, 'date_deadline': task.date_deadline} or '',
            #         'status': {'id': task.stage_id.id, 'name': task.stage_id.name} or '',
            #     }
            #     list_jobs.append(project_task)
            #     member_ids = []
            #     for user in task.user_ids:
            #         member_ids.append({
            #             'id': user.id,
            #             'name': user.name,
            #             'avatar': urls.url_join(base_url,
            #                                     '/web/image?model=res.users&id={0}&field=image_1920'.format(
            #                                         user.id)),
            #         })
            #     project_task['member'] = member_ids
            #     manager = []
            #     for mng in task.manager_ids:
            #         manager.append({
            #             'id': mng.id,
            #             'name': mng.name,
            #             'avatar': urls.url_join(base_url,
            #                                     '/web/image?model=res.users&id={0}&field=image_1920'.format(
            #                                         mng.id)),
            #         })
            #     project_task['manager'] = manager
            data['total_member'] = rec.follow_count

            # data['project_management'] = {
            #     'id': rec.user_id.id,
            #     'name': rec.user_id.name,
            #     'avatar': urls.url_join(base_url,
            #                                     '/web/image?model=res.users&id={0}&field=image_1920'.format(
            #                                         rec.user_id.id)),
            # }
            # data['list_jobs'] = list_jobs
            project_management = []
            for user in rec.user_id:
                project_management.append({
                    'id': user.id,
                    'name': user.name,
                    'avatar': urls.url_join(base_url,
                                                '/web/image?model=res.users&id={0}&field=image_1920'.format(
                                                    user.id)),
                })
                data['project_management'] = project_management
                data['department'] = rec.partner_id.name
            values.append(data)
        return valid_response(values)

    @validate_token
    @http.route("/api/v1/project-task", type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def get_project_task(self, **payload):
        """
            payload = {
                'project_id': 123,
            }
        """
        uid = request.uid
        user = request.env['res.users'].browse(int(uid))
        if user.tz:
            tz = pytz.timezone(user.tz)
        else:
            tz = pytz.timezone('Asia/Ho_Chi_Minh')
        values = dict()
        try:
            for key, value in payload.items():
                values[key] = value
            project_id = int(values.get('project_id'))
        except Exception as e:
            return invalid_response("invalid object name", "Project ID phai la kieu du lieu INT")

        values = []
        base_url = ProjectController.get_url_base(self)
        domain = [('project_id', '=', project_id)]
        list_project_task = request.env['project.task'].sudo().search(domain)
        list_jobs = list()
        data = dict()
        for task in list_project_task:
            if task.date_start:
                date_start = task.date_start.astimezone(tz=tz)
            else:
                date_start = None
            if task.date_end:
                date_end = task.date_end.astimezone(tz=tz)
            else:
                date_end = None
            if task.date_deadline:
                date_deadline = datetime.combine(task.date_deadline, datetime.min.time())
            else:
                date_deadline = None
            project_task = {
                'id': task.id,
                'title': task.name,
                'description': task.description,
                'phase': {'id': task.phase_id.id, 'name': task.phase_id.name} or None,
                'date': {'start': date_start, 'end': date_end, 'date_deadline': date_deadline},
                'status': {'id': task.stage_id.id, 'name': task.stage_id.name} or None,
            }
            member_ids = list()
            # Get info user_ids<many2many>: nguoi giao viec
            for user in task.user_ids:
                member_ids.append({
                    'id': user.id,
                    'name': user.name,
                    'avatar': urls.url_join(base_url,
                                            '/web/image?model=res.users&id={0}&field=image_1920'.format(
                                                user.id)),
                })
            project_task['member'] = member_ids
            manager = list()
            # Get info manager_ids<many2many>: nguoi quan ly
            for mng in task.manager_ids:
                manager.append({
                    'id': mng.id,
                    'name': mng.name,
                    'avatar': urls.url_join(base_url,
                                            '/web/image?model=res.users&id={0}&field=image_1920'.format(
                                                mng.id)),
                })
            project_task['manager'] = manager
            list_jobs.append(project_task)
        data['list_jobs'] = list_jobs
        values.append(data)
        return valid_response(values)

    @validate_token
    @http.route("/api/v1/project/create_project", type="http", auth="public", methods=["POST"], csrf=False)
    def recording_candidate_data(self, **payload):
        headers = request.httprequest.headers
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        values = {}
        for k, v in payload.items():
            values[k] = v
        field_require = [
            'name',
            'project_id',
            'user_ids',
            'manager_ids',
            'partner_id',
            'date_start',
            'date_end',
            'date_deadline',
            'description',
            'email_cc',
        ]
        for field in field_require:
            if field not in payload.keys():
                return invalid_response(
                    "Missing",
                    "The parameter %s is missing!!!" % field)

        project = request.env['project.task'].with_user(user).create({
            'name': payload['name'] or '',
            'project_id': int(payload.get('project_id')),
            'partner_id': payload.get('partner_id'),
            'description': payload.get('description'),
            'email_cc': payload.get('email_cc'),
            'date_start': payload.get('date_start') if payload.get('date_start') else datetime.today(),
            'date_end': payload.get('date_end') if payload.get('date_end') else datetime.today(),
            'date_deadline': payload.get('date_deadline') if payload.get('date_deadline') else datetime.today(),
        })
        if payload.get('user_ids'):
            users = eval(values['user_ids'])
            project.user_ids = users
        if payload.get('manager_ids'):
            manager_ids = eval(values['manager_ids'])
            project.manager_ids = manager_ids
        if payload.get('child_ids'):
            child = eval(values['child_ids'])
            for data in child:
                project.timesheet_ids += request.env['account.analytic.line'].sudo().create({
                    'task_id': project.id,
                    'project_id': project.project_id.id,
                    'employee_id': data.get('employee'),
                    'name': data.get('des'),
                    'user_id': user.id,
                    'date_end': data.get('end_date'),
                    'date_start': data.get('start_date'),
                    'date': data.get('date'),
                })

    @validate_token
    @http.route("/api/v1/project/create_sub_task", type="http", auth="public", methods=["POST"], csrf=False)
    def create_sub_task(self, **payload):
        headers = request.httprequest.headers
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        values = {}
        for k, v in payload.items():
            values[k] = v
        if payload.get('task_id'):
            task = request.env['project.task'].sudo().search([('id', '=', payload.get('task_id'))])
            if payload.get('name'):
                task.name = payload.get('name')

            if payload.get('partner_id'):
                task.name = payload.get('partner_id')

            if payload.get('description'):
                task.name = payload.get('description')

            if payload.get('email_cc'):
                task.name = payload.get('email_cc')

            if payload.get('date_start'):
                task.name = payload.get('date_start')

            if payload.get('date_end'):
                task.name = payload.get('date_end')

            if payload.get('date_deadline'):
                task.name = payload.get('date_deadline')

            if payload.get('description'):
                task.name = payload.get('date_deadline')

            if payload.get('user_ids'):
                users = eval(values['user_ids'])
                task.user_ids = users

            if payload.get('manager_ids'):
                manager_ids = eval(values['manager_ids'])
                task.manager_ids = manager_ids

            if payload.get('child_ids'):
                child = eval(values['child_ids'])
                for data in child:
                    task.timesheet_ids += request.env['account.analytic.line'].sudo().create({
                        'task_id': task.id,
                        'project_id': task.project_id.id,
                        'employee_id': data.get('employee'),
                        'name': data.get('des'),
                        'user_id': user.id,
                        'date_end': data.get('end_date'),
                        'date_start': data.get('start_date'),
                        'date': data.get('date'),
                    })

    @validate_token
    @http.route("/api/v1/status-my-mission", type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def get_status_my_mission(self, **payload):
        values = []
        data = request.env['project.task.type'].sudo().search([])
        print(data)
        for rec in data:
            dates = {'id': rec.id,
                     'name': rec.name,
                     }
            values.append(dates)
        return valid_response(values)

    # @validate_token
    # @http.route("/api/v1/update-my-mission", type="http", auth="public", methods=["POST"], csrf=False, cors='*')
    # def update_status_my_mission(self, **payload):
    #     values = []
    #     data = request.env['project.task.type'].sudo().search([])
    #     print(data)
    #     for rec in data:
    #         dates = {'id': rec.id,
    #                  'name': rec.name,
    #                  }
    #         values.append(dates)
    #     return valid_response(values)

    @validate_token
    @http.route("/api/v1/project/get-my-mision", type="http", auth="none", methods=["GET"], csrf=False, cors='*')
    def get_my_mision(self, **payload):
        values = []
        base_url = ProjectController.get_url_base(self)
        domain = []

        if payload.get('user_ids'):
            domain.append(('user_ids', '=', int(payload.get('user_ids'))))

        list_mission = request.env['project.task'].sudo().search(['|', ('user_ids', 'in', request.uid), ('manager_ids', 'in', request.uid)])
        for miss in list_mission:
            data = {
                'name': miss.name or '',
                'priority': miss.priority or '',
                'project': miss.project_id.name or '',
                'customer': miss.partner_id.name or '',
                'plan_date': miss.date_start or '',
                'date_deadline': miss.date_deadline or '',
            }
            manager = []
            for mng in miss.manager_ids:
                manager.append({
                    'id': mng.id,
                    'name': mng.name,
                    'avatar': urls.url_join(base_url,
                                            '/web/image?model=res.users&id={0}&field=image_1920'.format(
                                                mng.id)),
                })
            data['manager'] = manager
            data['status'] = {
                'id': miss.stage_id.id,
                'name': miss.stage_id.name
            }

            assigned_person = []
            for ass in miss.user_ids:
                assigned_person.append({
                    'id': ass.id,
                    'name': ass.name,
                    'avatar': urls.url_join(base_url,
                                            '/web/image?model=res.users&id={0}&field=image_1920'.format(
                                                ass.id)),
                })
            data['assigned_person'] = assigned_person

            manager_person = []
            for mar in miss.manager_ids:
                manager_person.append({
                    'id': mar.id,
                    'name': mar.name,
                    'avatar': urls.url_join(base_url,
                                            '/web/image?model=res.users&id={0}&field=image_1920'.format(
                                                mar.id)),
                })
            data['manager_person'] = manager_person

            data['description'] = miss.description or ''

            subsidiary_mision = []
            for sub in miss.timesheet_ids:
                subsidiary_mision.append({
                    'date': sub.date or '',
                    'staff': sub.employee_id.name or '',
                    'description': sub.name or ''
                })
            data['subsidiary_mision'] = subsidiary_mision
            data['email_cc'] = miss.email_cc or ''

            values.append(data)
        return valid_response(values)

    @validate_token
    @http.route('/api/v1/project/get-stage-task', type='http', auth='public', method=['GET'], csrf=False)
    def get_stage_task(self, **payload):
        values = {}
        stage = request.env['project.task.type'].sudo().search([])
        for record in stage:
            data = {
                'id': record.id,
                'name': record.name,
            }
            values.append(data)
        return valid_response(values)

    @validate_token
    @http.route('/api/v1/project/put-mission', type='http', auth='public', method=['POST'], csrf=False)
    def put_mission(self, **payload):
        values = {}

        mission = request.env['project.task'].sudo().search([('id', '=', payload.get('task_id'))])
        print(mission.stage_id)
        if not mission:
            return invalid_response(
                "invalid object model \nThe model is not available in the registry."
            )
        else:
            if payload.get('description'):
                values['description'] = payload.get('description')
            if payload.get('stage_id'):
                values['stage_id'] = int(payload.get('stage_id'))
            if payload.get('user_ids'):
                # mission.user_ids = eval(payload.get('user_ids'))
                for u in mission.user_ids:
                    if u not in eval(payload.get('user_ids')):
                        eval(payload.get('user_ids')).append(u)
                mission.user_ids = eval(payload.get('user_ids'))
            if payload.get('manager_ids'):
                for m in mission.manager_ids:
                    if m not in eval(payload.get('manager_ids')):
                        eval(payload.get('manager_ids')).append(m)
                mission.manager_ids = eval(payload.get('manager_ids'))
        mission.update(values)
