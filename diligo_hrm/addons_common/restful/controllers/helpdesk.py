"""Part of odoo. See LICENSE file for full copyright and licensing details."""
import base64
import logging

from odoo.addons.restful.common import (
    invalid_response,
)
from odoo.addons.restful.common import (
    valid_response,
    valid_response_once,
)
from odoo.addons.restful.controllers.main import (
    validate_token
)
from werkzeug import urls

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class HelpdeskController(http.Controller):

    def get_url_base(self):
        config = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if config:
            return config
        return 'https://test.diligo.vn:15000'

    @validate_token
    @http.route("/api/v1/helpdesk", type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def get_helpdesk(self, **payload):
        values = []
        base_url = HelpdeskController.get_url_base(self)
        list_helpdesk = request.env['sci.maintenance.request'].search([], offset=payload.get('offset'), limit=100)
        for rec in list_helpdesk:
            data = {'id': rec.id,
                    'title': rec.name or '',
                    'code': rec.code or '',
                    'person_name': {'id': rec.person_name.id, 'name': rec.person_name.name,
                                    'avatar': urls.url_join(base_url,
                                                            '/web/image?model=hr.employee.public&id={0}&field=image_1920'.format(
                                                                rec.person_name.id))} or '',
                    'department_person': rec.department or '',
                    'email': rec.email or '',
                    'phone': rec.phone or '',
                    'priority': rec.priority or '',
                    'channel': rec.channel or '',
                    'type': rec.type or '',
                    'state': rec.state or '',
                    'type_maintenance_request': {'id': rec.type_maintenance_request.id,
                                                 'name': rec.type_maintenance_request.name} or '',
                    'area_type_maintenance_request': {'id': rec.area_type_maintenance_request.id,
                                                      'name': rec.area_type_maintenance_request.name} or '',
                    'category': {'id': rec.category_id.id, 'name': rec.category_id.name} or '',
                    'maintenance_team_id': {'id': rec.maintenance_team_id.id,
                                            'name': rec.maintenance_team_id.name} or '',
                    'emp_id': {'id': rec.emp_id.id, 'name': rec.emp_id.name, 'avatar': urls.url_join(base_url,
                                                                                                     '/web/image?model=hr.employee.public&id={0}&field=image_1920'.format(
                                                                                                         rec.emp_id.id))} or '',
                    'request_date': rec.request_date,
                    'close_date': rec.close_date,
                    'completion_time': rec.completion_time,
                    'the_average_time': rec.the_average_time,
                    'description': rec.description,

                    # hiện trạng/nguyên nhân
                    'tools_description': rec.tools_description,
                    # giải pháp/khắc phục
                    'operations_description': rec.operations_description,
                    # 'message_follower_ids': rec.message_follower_ids,
                    }
            message = []
            for mess in rec.message_ids:
                message.append({
                    'body': mess.body
                })
            data['message'] = message
            # danh sách nhân sự hỗ trợ
            supervisors = []
            for supervisor in rec.supervisor_ids:
                supervisors.append({
                    'id': supervisor.id,
                    'name': supervisor.name,
                    'work_phone': supervisor.work_phone,
                    'department': {'id': supervisor.department_id.id, 'name': supervisor.department_id.name} or '',
                    'position': {'id': supervisor.job_id.id, 'name': supervisor.job_id.name} or '',
                    'parent': {'id': supervisor.parent_id.id, 'name': supervisor.parent_id.name,
                               'avatar': urls.url_join(base_url,
                                                       '/web/image?model=hr.employees&id={0}&field=image_1920'.format(
                                                           supervisor.id))} or '',

                })
            data['supervisors'] = supervisors
            attachment = []
            for att in rec.attachment_ids:
                attachment.append({
                    'id': att.id,
                    'file_name': att.name,
                    'user_id': att.create_uid,
                    # 'description': att.description,
                    'date': att.create_date,
                    'file': urls.url_join(base_url, "web/content2/?model=ir.attachment&id=" + str(
                        att.id) + "&filename_field=name&field=datas&download=true&name=" + att.name),

                })
            data['attachment'] = attachment

            # mô tả yêu cầu
            email_list = []
            if rec.default_cc:
                vl = str(rec.default_cc).split('\n')
                for em in vl:
                    email_list.append(em)

            email_list_bcc = []
            if rec.default_bcc:
                vl_bcc = str(rec.default_cc).split('\n')
                for bcc in vl_bcc:
                    email_list_bcc.append(bcc)

            data['request_description'] = {
                'default_cc': email_list or '',
                'default_bcc': email_list_bcc or '',
            }

            values.append(data)
        if list_helpdesk:
            return valid_response(values)
        else:
            return valid_response_once({})

    @validate_token
    @http.route("/api/v1/helpdesk/create_helpdesk", type="http", auth="public", methods=["POST"], csrf=False, cors='*')
    def post_helpdesk(self, **payload):
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        values = {}
        for k, v in payload.items():
            values[k] = v
        field_require = [
            'name',
            # 'person_name',
            'category',
        ]
        for field in field_require:
            if field not in payload.keys():
                return invalid_response(
                    "Missing",
                    "The parameter %s is missing!!!" % field)
        person_name = request.env['hr.employee'].sudo().search([('user_id', '=', request.uid)])
        helpdesk = request.env['sci.maintenance.request'].with_user(user).create({
            'name': payload.get('name'),
            'person_name': person_name.id,
            'type': payload.get('type'),
            'type_maintenance_request': int(payload.get('type_maintenance_request')),
            'area_type_maintenance_request': (request.env['area.type.maintenance.request'].sudo().search(
                [('id', '=', payload.get("area_type_maintenance_request"))])).id,
            'maintenance_team_id': int(payload.get('maintenance_team_id')),
            'description': payload.get('description'),
            'tools_description': payload.get('tools_description'),
            'operations_description': payload.get('operations_description'),
            'channel': 'phone',
            'category_id': int(payload.get('category')),
            'attachment_ids': payload.get('attachment_ids'),
        })
        if payload.get('default_cc'):
            mail_cc = eval(values['default_cc'])
            email_cc = ''
            for mail in mail_cc:
                email_cc += ' ' + mail
            helpdesk.default_cc = email_cc
        if payload.get('default_bcc'):
            mail_bcc = eval(values['default_bcc'])
            email_bcc = ''
            for bcc in mail_bcc:
                email_bcc += ' ' + bcc
            helpdesk.default_bcc = email_bcc
        if not helpdesk.emp_id:
            emp = request.env['hr.employee'].sudo().search([('id', '=', payload.get("emp_id"))])
            helpdesk.write({
                'emp_id': emp
            })

        if helpdesk.person_name:
            helpdesk.department = person_name.department_id.name
            helpdesk.email = person_name.work_email
            helpdesk.phone = person_name.work_phone
            # helpdesk.emp_id = person_name
        if helpdesk.area_type_maintenance_request:
            helpdesk.the_average_time = request.env['area.type.maintenance.request'].sudo().search(
                [('id', '=', payload.get("area_type_maintenance_request"))]).the_average_time

        data_supervisor_ids = []
        if payload.get('supervisor_ids'):
            supervisor = eval(values['supervisor_ids'])
            for data in supervisor:
                data_supervisor_ids.append(int(data))
            helpdesk.supervisor_ids = data_supervisor_ids
        if payload.get('attachment'):
            attachment_value = {
                'file_name': payload.get('attachment').filename,
                'file': base64.encodebytes(payload.get('attachment').read()),
                'support_ticket_id': helpdesk.id,
            }
            attachment_id = request.env['ir.attachment'].sudo().create(attachment_value)

        # return invalid_response("Bạn đã ứng tuyển thành công vào vị trí %s." % payload.get('job_name'))

    @validate_token
    @http.route("/api/v1/type_maintenance", type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def get_pki_employee(self, **payload):
        values = []
        headers = request.httprequest.headers
        data = request.env['type.maintenance.request'].sudo().search([])
        for rec in data:
            dates = {'id': rec.id,
                     'type': rec.type,
                     'name': rec.name,
                     }
            area = []
            for are in rec.area:
                area.append({
                    'id': are.id,
                    'name': are.name,
                    'the_average_time': are.the_average_time or '',
                })
            dates['area'] = area
            values.append(dates)
        return valid_response(values)

    @validate_token
    @http.route("/api/v1/category-helpdesk", type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def get_category_helpdesk(self, **payload):
        values = []
        data = request.env['sci.maintenance.equipment.category'].sudo().search([])
        for rec in data:
            dates = {'id': rec.id,
                     'department': rec.department_id.name,
                     'name': rec.name,
                     'email': rec.email,
                     'manager': rec.technician_user_id.name,
                     }
            main_team = []
            for team in rec.team_ids:
                team_ids = {
                    'name': team.name,
                    'manager': rec.technician_user_id.name,
                }
                main_team.append(team_ids)
                member_ids = []
                for mem in team.member_ids:
                    member = {
                        'id': mem.id,
                        'name': mem.name,
                    }
                    member_ids.append(member)
                team_ids['member'] = member_ids
            dates['team'] = main_team
            values.append(dates)
        return valid_response(values)

    @http.route('/api/v1/helpdesk/update-helpdesk', type='http', auth='public', method=['PUT'], csrf=False)
    def func_update_helpdesk(self, **payload):
        values = {}

        get_helpdesk = request.env['sci.maintenance.request'].sudo().search([('id', '=', int(payload.get('id')))])
        if not get_helpdesk:
            return valid_response({
                "invalid object model \nThe model is not available in the registry."
            })

        if payload.get('state'):
            values['state'] = payload.get('state')
        if payload.get('type'):
            values['type'] = payload.get('type')
        # người gửi yêu cầu
        if payload.get('person_name'):
            get_person = request.env['hr.employee'].sudo().search([('id', '=', int(payload.get('person_name')))])
            values['person_name'] = payload.get('person_name')
            values['department'] = get_person.department_id.name
            values['email'] = get_person.work_email
            values['phone'] = get_person.work_phone
        # danh sách nhân sự hỗ trợ
        if payload.get('supervisor_ids'):
            values['supervisor_ids'] = [int(i) for i in eval(payload.get('supervisor_ids'))]
        # hiện trạng/nguyên nhân
        if payload.get('tools_description'):
            values['tools_description'] = payload.get('tools_description')
        # giải pháp khắc phục
        if payload.get('operations_description'):
            values['operations_description'] = payload.get('operations_description')

        get_helpdesk.update(values)
