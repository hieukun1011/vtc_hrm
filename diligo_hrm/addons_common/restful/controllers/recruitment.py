"""Part of odoo. See LICENSE file for full copyright and licensing details."""
import base64
import logging

from odoo.addons.restful.common import (
    invalid_response,
    valid_response,
    valid_response_once,
)

from odoo import SUPERUSER_ID
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class RecruitmentController(http.Controller):

    @http.route("/api/v1/recruitment", type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def get_recruitment(self, **payload):
        values = []
        list_job = request.env['hr.job'].sudo().search([])
        for rec in list_job:
            data = {
                'id': rec.id,
                'name': rec.name,
                'department': {'id': rec.department_id.id, 'name': rec.department_id.name} or '',
                'category': rec.work_address or '',
                'industry': rec.job_industry.name or '',
                'time_work': rec.time_work or '',
                'status': rec.highlight or '',
                'state': rec.state or '',
            }
            if rec.periods:
                data['deadline'] = rec.periods[-1].end_date
                data['start'] = rec.periods[-1].start_date
                data['number'] = rec.periods[-1].expected_recruitment
            city = []
            for ct in rec.city_id:
                city.append({
                    'id': ct.id,
                    'name': ct.name,
                })
            data['city'] = city
            if rec.salary_type == 'ltt' or rec.salary_type == 'lct':
                data['salary'] = rec.salary_type,
            else:
                if rec.salary_type == 'usd':
                    data['salary'] = str(rec.salary_proposed) + ' USD - ' + str(rec.salary_proposed_extra) + ' USD'
                else:
                    data['salary'] = str(rec.salary_proposed) + ' VND - ' + str(rec.salary_proposed_extra) + ' VND'
            if rec.experience == '1':
                data['exp'] = str(rec.experience_from) + ' Đến ' + str(rec.experience_to) + ' Năm'
            elif rec.experience == '0':
                data['exp'] = {'key': '0', 'value': 'Chưa có kinh nghiệm'},
            else:
                data['exp'] = {'key': '2', 'value': 'Không yêu cầu kinh nghiệm'},
            values.append(data)
        return valid_response(values)

    @http.route("/api/v1/recruitment-by-id", type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def get_recruitment_by_id(self, **payload):
        """ API 1.13 Danh sách tin tuyển dụng"""
        values = []
        list_job = request.env['hr.job'].sudo().search([('id', '=', payload.get('recruitment_id'))])
        for rec in list_job:
            # print(rec.city_id)
            data = {'id': rec.id,
                    'name': rec.name,
                    'state': rec.state or '',
                    # 'address': {'id': rec.city_id.id, 'name': rec.city_id.name} or '',
                    'department': {'id': rec.department_id.id, 'name': rec.department_id.name} or '',
                    'degree': {'id': rec.type_id.id, 'name': rec.type_id.name} or '',
                    'status': rec.highlight or '',
                    'link': rec.website_url or '',
                    'time_work': rec.time_work or '',
                    'require': rec.req_job or '',
                    'description': rec.description or '',
                    'category': rec.work_address or '',
                    'recruiter': {'id': rec.user_id.id, 'name': rec.user_id.name} or '',
                    'industry': rec.job_industry.name or '',
                    }
            if rec.periods:
                data['deadline'] = rec.periods[-1].end_date
                data['start'] = rec.periods[-1].start_date
                data['number'] = rec.periods[-1].expected_recruitment
            tag_ids = []
            for tag in rec.categ_ids:
                tag_ids.append({
                    'id': tag.id,
                    'name': tag.name,
                })
            city = []
            for ct in rec.city_id:
                city.append({
                    'id': ct.id,
                    'name': ct.name,
                })
            data['city'] = city
            welfare = []
            for wel in rec.welfare_ids:
                welfare.append({
                    'id': wel.id,
                    'name': wel.name,
                })
            data['welfare'] = welfare
            if rec.salary_type == 'ltt' or rec.salary_type == 'lct':
                data['salary'] = rec.salary_type,
            else:
                if rec.salary_type == 'usd':
                    data['salary'] = str(rec.salary_proposed) + ' USD - ' + str(rec.salary_proposed_extra) + ' USD'
                else:
                    data['salary'] = str(rec.salary_proposed) + ' VND - ' + str(rec.salary_proposed_extra) + ' VND'
            if rec.experience == '1':
                data['exp'] = str(rec.experience_from) + ' Đến ' + str(rec.experience_to) + ' Năm'
            elif rec.experience == '0':
                data['exp'] = {'key': '0', 'value': 'Chưa có kinh nghiệm'},
            else:
                data['exp'] = {'key': '2', 'value': 'Không yêu cầu kinh nghiệm'},
            values.append(data)
        if list_job:
            return valid_response(values)
        else:
            return valid_response_once({})

    @http.route("/api/v1/recruitment/apply", type='http', auth="public", methods=["POST", "OPTIONS"], website=True,
                csrf=False, cors="*")
    def recording_candidate_data(self, **payload):
        field_require = [
            'name',
            'job_id',
            'phone',
            'email',
            'user',
            'cv',
        ]
        for field in field_require:
            if field not in payload.keys():
                return invalid_response(
                    "Missing",
                    "The parameter %s is missing!!!" % field)
        domain = {
            'name': payload.get('name'),
            'partner_name': payload.get('name'),
            'job_id': payload.get('job_id'),
            'partner_phone': payload.get('phone'),
            'email_from': payload.get('email'),
            'marital': payload.get('status'),
            'stage_id': 1,
            'gender': payload.get('gender'),
            'birthday': payload.get('dob'),
            'address': payload.get('address'),
            'social_facebook': payload.get('facebook'),
            'qualification': payload.get('exp'),
            # 'description': payload.get('skill') + ' ' + payload.get('skill_other'),
        }
        if payload.get('skill') or payload.get('skill_other'):
            domain['description'] = payload.get('skill') + ' ' + payload.get('skill_other'),
        applicant = request.env['hr.applicant'].with_user(SUPERUSER_ID).create(domain)
        if payload.get('cv'):
            attachment_value = {
                'name': payload.get('cv').filename,
                'datas': base64.encodebytes(payload.get('cv').read()),
                'res_model': 'hr.applicant',
                'res_id': applicant.id,
            }
            attachment_id = request.env['ir.attachment'].sudo().create(attachment_value)
        return invalid_response("Bạn đã ứng tuyển thành công vào vị trí %s." % payload.get('job_name'))

    @http.route("/api/v1/result-recruitment", type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def get_states(self, **payload):
        """ API 1.10 Tra cứu kết quả phỏng vấn"""
        field_require = [
            'phone',
            'email',
        ]
        for field in field_require:
            if field not in payload.keys():
                return invalid_response(
                    "Missing",
                    "The parameter %s is missing!!!" % field)

        applicant = request.env['hr.applicant'].sudo().search(['|', ('partner_phone', '=', payload.get('phone')),
                                                               ('email_from', '=', payload.get('email'))], limit=1)
        if applicant:
            data = {
                'name': applicant.name,
                'position': applicant.job_id.name,
                'department': applicant.department_id.name,
                'state': applicant.stage_id.name,
            }
            if applicant.applicant_state:
                data['result'] = applicant.applicant_state[0].result if applicant.applicant_state[
                                                                            0].result != False else 'Chưa có kết quả'
            return valid_response(data)
