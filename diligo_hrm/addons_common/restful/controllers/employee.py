"""Part of odoo. See LICENSE file for full copyright and licensing details."""
import logging

import pytz
from odoo.addons.restful.common import (
    invalid_response,
)
from odoo.addons.restful.common import (
    valid_response,
)
from odoo.addons.restful.controllers.main import (
    validate_token
)
from werkzeug import urls

from odoo import http
from odoo.http import request
from datetime import date
_logger = logging.getLogger(__name__)


class EmployeeController(http.Controller):

    def get_url_base(self):
        config = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if config:
            return config
        return 'https://test.diligo.vn:15000'

    @validate_token
    @http.route("/api/v1/employee-info", type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def get_employee_infor(self, **payload):
        base_url = EmployeeController.get_url_base(self)
        values = []
        list_employee = request.env['hr.employee'].sudo().search(
            [('user_id', '=', request.uid)])  #
        # data = {}
        for rec in list_employee:
            data = {
                'id': rec.id,
                'employee_code': rec.employee_id,
                'avatar': urls.url_join(base_url,
                                        '/web/image?model=hr.employee.public&id={0}&field=image_1920'.format(
                                            rec.id)),
                'name': rec.name or '',
                'gender': rec.gender or '',
                'dob': rec.birthday or '',
                'born': rec.address_home or '',
                'address': rec.apartment_number or '',
                'province': {'id': rec.res_country_state.id, 'name': rec.res_country_state.name} or '',
                'district': {'id': rec.res_country_district.id, 'name': rec.res_country_district.name} or '',
                'town': {'id': rec.res_country_ward.id, 'name': rec.res_country_ward.name} or '',
                'phone': rec.phone or '',
                'email': rec.email or '',
            }
            inforPerson = []
            inforWork = []
            inforAccount = []
            identification = []
            visa = []
            passport = []
            workPermit = []
            curriculumVitae = []
            inforStudy = []
            inforWork.append({
                'channel': {'id': rec.channel_id.id, 'name': rec.channel_id.name} or '',
                'department': {'id': rec.department_id.id, 'name': rec.department_id.name} or '',
                'position': {'id': rec.job_id.id, 'name': rec.job_id.name} or '',
                'group_job': {'id': rec.group_job.id, 'name': rec.group_job.name} or '',
                'manage': {'id': rec.parent_id.id, 'name': rec.parent_id.name} or '',
            })
            inforAccount.append({
                'bank': rec.bank or '',
                'bank_brand': rec.bank_branch or '',
                'bank_account': rec.bank_account or '',
            })
            identification.append({
                'number': rec.identification_id or '',
                'dateProvide': rec.issue_date or '',
                'addressProvide': rec.id_issue_place or '',
            })
            visa.append({
                'number': rec.visa_no,
                'dateOut': rec.visa_expire,
            })
            passport.append({
                'number': rec.passport_id,
            })
            workPermit.append({
                'number': rec.permit_no,
                'toDate': rec.work_permit_expiration_date,
            })
            curriculumVitae.append({
                'numberTax': "",
                'nationality': {'id': rec.country_id.id, 'name': rec.country_id.name} or '',
                'status': rec.marital or '',
                'peopleContact': rec.emergency_phone,
                'phoneCompany': rec.work_phone,
                'addressWork': rec.address_id,
            })
            inforStudy.append({
                'school': rec.study_school,
                'certificate': rec.certificate or '',
                'rank': rec.classification,
            })
            family = []
            for fam in rec.fam_ids:
                family.append({
                    'id': fam.id,
                    'name': fam.member_name,
                    'birth': fam.birth_date,
                    'relation': {'id': fam.relation_id.id, 'name': fam.relation_id.name} or '',
                })
            data['inforPerson'] = inforPerson
            data['inforWork'] = inforWork
            data['inforAccount'] = inforAccount
            data['identification'] = identification
            data['visa'] = visa
            data['passport'] = passport
            data['workPermit'] = workPermit
            data['curriculumVitae'] = curriculumVitae
            data['inforStudy'] = inforStudy
            data['family'] = family
            values.append(data)
        return valid_response(values)


    @validate_token
    @http.route("/api/v1/employee", type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def get_employee(self, **payload):
        base_url = EmployeeController.get_url_base(self)
        values = []
        list_employee = request.env['hr.employee'].sudo().search(
            [])  # ('user_id.token_ids.token', '=', headers.get("access_token"))
        # data = {}
        for rec in list_employee:
            data = {
                'id': rec.id,
                'employee_code': rec.employee_id,
                'avatar': urls.url_join(base_url,
                                        '/web/image?model=hr.employee.public&id={0}&field=image_1920'.format(
                                            rec.id)),
                'name': rec.name or '',
                'gender': rec.gender or '',
                'dob': rec.birthday or '',
                'born': rec.address_home or '',
                'address': rec.apartment_number or '',
                'province': {'id': rec.res_country_state.id, 'name': rec.res_country_state.name} or '',
                'district': {'id': rec.res_country_district.id, 'name': rec.res_country_district.name} or '',
                'town': {'id': rec.res_country_ward.id, 'name': rec.res_country_ward.name} or '',
                'phone': rec.phone or '',
                'email': rec.email or '',
            }
            inforPerson = []
            inforWork = []
            inforAccount = []
            identification = []
            visa = []
            passport = []
            workPermit = []
            curriculumVitae = []
            inforStudy = []
            inforWork.append({
                'channel': {'id': rec.channel_id.id, 'name': rec.channel_id.name} or '',
                'department': {'id': rec.department_id.id, 'name': rec.department_id.name} or '',
                'position': {'id': rec.job_id.id, 'name': rec.job_id.name} or '',
                'group_job': {'id': rec.group_job.id, 'name': rec.group_job.name} or '',
                'manage': {'id': rec.parent_id.id, 'name': rec.parent_id.name} or '',
            })
            inforAccount.append({
                'bank': rec.bank or '',
                'bank_brand': rec.bank_branch or '',
                'bank_account': rec.bank_account or '',
            })
            identification.append({
                'number': rec.identification_id or '',
                'dateProvide': rec.issue_date or '',
                'addressProvide': rec.id_issue_place or '',
            })
            visa.append({
                'number': rec.visa_no,
                'dateOut': rec.visa_expire,
            })
            passport.append({
                'number': rec.passport_id,
            })
            workPermit.append({
                'number': rec.permit_no,
                'toDate': rec.work_permit_expiration_date,
            })
            curriculumVitae.append({
                'numberTax': "",
                'nationality': {'id': rec.country_id.id, 'name': rec.country_id.name} or '',
                'status': rec.marital or '',
                'peopleContact': rec.emergency_phone,
                'phoneCompany': rec.work_phone,
                'addressWork': rec.address_id,
            })
            inforStudy.append({
                'school': rec.study_school,
                'certificate': rec.certificate or '',
                'rank': rec.classification,
            })
            family = []
            for fam in rec.fam_ids:
                family.append({
                    'id': fam.id,
                    'name': fam.member_name,
                    'birth': fam.birth_date,
                    'relation': {'id': fam.relation_id.id, 'name': fam.relation_id.name} or '',
                })
            data['inforPerson'] = inforPerson
            data['inforWork'] = inforWork
            data['inforAccount'] = inforAccount
            data['identification'] = identification
            data['visa'] = visa
            data['passport'] = passport
            data['workPermit'] = workPermit
            data['curriculumVitae'] = curriculumVitae
            data['inforStudy'] = inforStudy
            data['family'] = family
            values.append(data)
        return valid_response(values)

    @http.route("/api/it/employee", type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def get_employee_department_it(self, **payload):
        values = []
        base_url = EmployeeController.get_url_base(self)
        data = request.env['hr.employee'].sudo().search(
            [('state', '=', 'working'), ('department_id.root_code', '=', 'CN')])
        for rec in data:
            list_data = {
                'id': rec.id,
                'employee_code': rec.employee_id,
                'name': rec.name or '',
                'avatar': urls.url_join(base_url,
                                        '/web/image?model=hr.employee.public&id={0}&field=image_1920'.format(
                                            rec.id)),
                'vote': [],
            }
            values.append(list_data)
        return valid_response(values)

    # hr nghỉ phép
    @validate_token
    @http.route("/api/it/hr/leave", type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def hr_leave(self, **payload):
        values = []
        base_url = EmployeeController.get_url_base(self)

        domain = []
        if payload.get('date_from'):
            domain.append(('date_from', '=', payload.get('date_from')))
        if payload.get('date_to'):
            domain.append(('date_to', '=', payload.get('date_to')))
        if payload.get('employee_id'):
            domain.append(('employee_id', '=', int(payload.get('employee_id'))))

        leave = request.env['hr.leave'].sudo().search(domain)
        for rec in leave:
            tz = pytz.timezone('Asia/Ho_Chi_Minh')
            data = {'id': rec.id,
                    'employee': rec.employee_id.name or '',
                    'number_of_days': rec.number_of_days or '',
                    'describe': rec.name or '',
                    'supported_attachment_ids': rec.supported_attachment_ids or '',
                    'holiday_type': rec.holiday_type or ''
                    }
            if rec.date_from:
                data['date_from'] = rec.date_from.astimezone(tz).strftime('%d-%m-%Y %H:%M:%S')
            else:
                data['date_from'] = '',

            if rec.date_to:
                data['date_to'] = rec.date_to.astimezone(tz).strftime('%d-%m-%Y %H:%M:%S')
            else:
                data['date_to'] = '',
            values.append(data)
        return valid_response(values)


    @validate_token
    @http.route("/api/it/hr/type_leave", type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def get_type_leave(self, **payload):
        values = []
        leave = request.env['hr.leave.type'].sudo().search([])
        for rec in leave:
            dates = {'id': rec.id,
                     'code': rec.code,
                     'name': rec.name,
                     }
            values.append(dates)
        return valid_response(values)

    @validate_token
    @http.route("/api/it/hr/add-leave", type="http", auth="public", methods=["POST"], csrf=False, cors='*')
    def hr_add_leave(self, **payload):
        values = {}
        for k, v in payload.items():
            values[k] = v
        field_require = [
            'date_from',
            'date_to',
            'type_leave',
            'description',
        ]
        for field in field_require:
            if field not in payload.keys():
                return invalid_response(
                    "Missing",
                    "The parameter %s is missing!!!" % field)
        leave = request.env['hr.leave.type'].sudo().search([('code', '=', payload.get('type_leave'))])
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.uid)])
        if payload.get('type_leave') == 'NP':
            if employee.allocation_display - employee.leaves_count <= 0:
                return invalid_response("Het phep")
            else:
                hr_leave = request.env['hr.leave'].with_user(employee.user_id).create({
                    'holiday_status_id': leave.id,
                    'date_from': date.fromisoformat(payload.get('date_from')),
                    'date_to': date.fromisoformat(payload.get('date_to')),
                    'holiday_type': 'employee',
                    'employee_id': employee.id,
                    'name': payload.get('description'),
                })
        elif payload.get('type_leave') == 'Ro':
            hr_leave = request.env['hr.leave'].with_user(employee.user_id).create({
                'holiday_status_id': leave.id,
                'date_from': date.fromisoformat(payload.get('date_from')),
                'date_to': date.fromisoformat(payload.get('date_to')),
                'holiday_type': 'employee',
                'employee_id': employee.id,
                'name': payload.get('description'),
            })
        elif payload.get('type_leave') == 'DM':
            hr_leave = request.env['hr.leave'].with_user(employee.user_id).create({
                'holiday_status_id': leave.id,
                'date_from': date.today(),
                'date_to': date.today(),
                'holiday_type': 'employee',
                'employee_id': employee.id,
                'name': payload.get('description'),
            })
        hr_leave.state = 'validate'

        return valid_response(hr_leave)



    @validate_token
    @http.route('/api/v1/employee/put-employee-info', type='http', auth='public', method=['PUT'], csrf=False)
    def update_employee_info(self, **payload):
        values = {}
        domain = []

        put_employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.uid)])
        if not put_employee:
            return invalid_response(
                "invalid object model \nThe model is not available in the registry."
            )

        if payload.get('gender'):
            values['gender'] = payload.get('gender')
        if payload.get('dob'):
            values['birthday'] = payload.get('dob')
        if payload.get('born'):
            values['address_home'] = payload.get('born')
        if payload.get('apartment_number'):
            values['apartment_number'] = payload.get('apartment_number')
        if payload.get('phone'):
            values['mobile_phone'] = payload.get('phone')
        #inforWork
        if payload.get('manage'):
            put_employee.parent_id.name = payload.get('manage')
        #bank
        if payload.get('bank'):
            values['bank'] = payload.get('bank')
        if payload.get('bank_account'):
            values['bank_account'] = payload.get('bank_account')
        #cmnd
        if payload.get('number'):
            values['identification_id'] = payload.get('number')
        if payload.get('dateProvide'):
            values['issue_date'] = payload.get('dateProvide')
        if payload.get('addressProvide'):
            values['id_issue_place'] = payload.get('addressProvide')
        #visa
        if payload.get('number_visa'):
            values['visa_no'] = payload.get('number_visa')
        if payload.get('dateOut'):
            values['visa_expire'] = payload.get('dateOut')
        #passport
        if payload.get('passport_id'):
            values['passport_id'] = payload.get('passport_id')
        #work permit
        if payload.get('number_work_permit'):
            values['permit_no'] = payload.get('number_work_permit')
        if payload.get('toDate'):
            values['work_permit_expiration_date'] = payload.get('toDate')
        #school
        if payload.get('school'):
            values['study_school'] = payload.get('school')
        if payload.get('certificate'):
            values['certificate'] = payload.get('certificate')
        if payload.get('rank'):
            values['classification'] = payload.get('rank')
        #sơ yếu lý lịch
        if payload.get('status'):
            values['marital'] = payload.get('status')
        if payload.get('nationality'):
            put_employee.country_id.name = payload.get('nationality')
        if payload.get('peopleContact'):
            values['emergency_phone'] = payload.get('peopleContact')
        if payload.get('phoneCompany'):
            values['work_phone'] = payload.get('phoneCompany')
        #thông tin gia đình
        if payload.get('member_name'):
            put_employee.fam_ids.member_name = payload.get('member_name')
        if payload.get('birth_date'):
            put_employee.fam_ids.birth_date = payload.get('birth_date')
        if payload.get('relation'):
            put_employee.fam_ids.relation_id.name = payload.get('relation')

        put_employee.update(values)
        return valid_response('You have successfully updated')

    @validate_token
    @http.route("/api/it/hr/type_leave/get_remaining_leaves", type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def get_remaining_leaves(self, **payload):
        values = []
        leave = request.env['hr.employee'].sudo().search([('user_id', '=', request.uid)])
        for rec in leave:
            dates = {'id': rec.id,
                     'code': int(rec.remaining_leaves),
                     'name': rec.name,
                     }
            values.append(dates)
        return valid_response(values)

