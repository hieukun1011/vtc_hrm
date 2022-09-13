"""Part of odoo. See LICENSE file for full copyright and licensing details."""
import logging
from datetime import datetime

from odoo.addons.restful.common import (
    invalid_response,
    valid_response,
)
from odoo.addons.restful.controllers.main import (
    validate_token
)
from werkzeug import urls

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class ApprovalsController(http.Controller):

    def get_url_base(self):
        config = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if config:
            return config
        return 'https://test.diligo.vn:15000'

    @validate_token
    @http.route("/api/v1/approvals", type="http", auth="public", methods=['GET'], csrf=False, cors="*")
    def get_approvals(self, **payload):
        base_url = ApprovalsController.get_url_base(self)
        values = []
        category = request.env['approval.category'].sudo().search([])
        for record in category:
            data = {
                'id': record.id,
                'name': record.name,
                'image': urls.url_join(base_url, '/web/image?model=approval.category&id={0}&field=image'.format(
                        record.id)),
                'total_request': record.request_to_validate_count,
            }
            values.append(data)
        return valid_response(values)

    @validate_token
    @http.route("/api/v1/approvals-by-id", type="http", auth="public", methods=['GET'], csrf=False, cors="*")
    def get_approvals_request(self, **payload):
        base_url = ApprovalsController.get_url_base(self)
        values = []
        list_approval_request = request.env['approval.request'].search([('category_id', '=', payload.get('category_id'))])
        for record in list_approval_request:
            approval = {
                'title': record.name,
                'category': {'id': record.category_id.id, 'name': record.category_id.name} or '',
                'request_owner': record.request_owner_id or '',

                'department_employee_request': {'id': record.department.id, 'name': record.department.name} or '',
                'date_start': record.date_start or '',
                'date_end': record.date_end or '',
                'partner': record.partner_id or '',
                'vehicle': record.vehicle or '',
                'description_request': record.reason or '',
                'time_need': record.time_need or '',
                'proposed_date': record.proposed_date or '',
                'intended_use': record.intended_use or '',
                'resource': record.resource or '',
                'quantity': record.quantity or '',
                'state': record.request_status or '',
            }
            users_approval = []
            for user in record.approver_ids:
                user_approval = {
                    'id': user.id,
                    'avatar': urls.url_join(base_url, '/web/image?model=res.users&id={0}&field=image'.format(
                        user.id)) if user else '',
                    'name': {'id': user.user_id.id, 'name': user.user_id.name} or '',
                    'status': user.status or '',
                }
                users_approval.append(user_approval)
            approval['users_approval'] = users_approval
            products = []
            for prd in record.product_line_ids:
                product_line = {
                    'id_product': prd.product_id.id,
                    'name_product': prd.product_id.name,
                    'description': prd.description,
                    'quantity': prd.quantity,
                }
                products.append(product_line)
            approval['products'] = products
            values.append(approval)
        return valid_response(values)

    @validate_token
    @http.route("/api/v1/approvals-by-state", type="http", auth="public", methods=['GET'], csrf=False, cors="*")
    def get_approvals_request_by_state(self, **payload):
        values = []
        list_approval_request = request.env['approval.request'].search(
            [('request_status', '=', payload.get('status'))])
        for record in list_approval_request:
            approval = {
                'title': record.name,
                'request_owner': record.request_owner_id or '',

                'department_employee_request': {'id': record.department.id, 'name': record.department.name} or '',
                'state': record.request_status or '',
            }
            values.append(approval)
        return valid_response(values)

    @validate_token
    @http.route("/api/v1/approvals/suggest", type="http", auth="public", methods=["POST"], csrf=False, cors="*")
    def create_approvals_api(self, **payload):
        values = {}
        for k, v in payload.items():
            values[k] = v
        field_require = [
            'category_id',
            'requirer_document',
            'user_ids',
            'user_request',
            'title',
            'description_request',
        ]
        categ = request.env['approval.category'].sudo().search([('id', '=', payload['category_id'])])
        if categ.has_vehicle != 'no':
            field_require.append('vehicle')
        if categ.has_time_need != 'no':
            field_require.append('time_need')
        if categ.has_proposed_date != 'no':
            field_require.append('proposed_date')
        if categ.has_intended_use != 'no':
            field_require.append('intended_use')
        if categ.has_resource != 'no':
            field_require.append('resource')
        if categ.has_partner != 'no':
            field_require.append('partner')
        if categ.has_date_start != 'no':
            field_require.append('date_start')
        if categ.has_department != 'no':
            field_require.append('department')
        if categ.has_partner != 'no':
            field_require.append('partner')
        if categ.has_job != 'no':
            field_require.append('job')
        if categ.has_employee_id != 'no':
            field_require.append('employee')
        if categ.has_period != 'no':
            field_require.append('period')
        if categ.has_product != 'no':
            field_require.append('product')
        if categ.has_quantity != 'no':
            field_require.append('quantity')
        if categ.has_amount != 'no':
            field_require.append('amount')
        if categ.has_reference != 'no':
            field_require.append('reference')
        if categ.has_payment_method != 'no':
            field_require.append('payment_method')
        if categ.has_location != 'no':
            field_require.append('location')

        for field in field_require:
            if field not in payload.keys():
                return invalid_response(
                    "Missing",
                    "The parameter %s is missing!!!" % field)

        employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.uid)])
        approval = request.env['approval.request'].with_user(employee.user_id).create({
            'category_id': categ.id,
            'request_owner_id': request.uid,
            'name': payload.get('title'),
            # 'employee_id': employee,
            # 'job': employee.job_id,
            'department': employee.department_id.id,
            'amount': payload.get('amount'),
            'date_start': payload.get('date_start'),
            'date_end': payload.get('date_end'),
            'partner_id': payload.get('partner'),
            'vehicle': payload.get('vehicle'),
            'reason': payload.get('description_request'),
            'time_need': payload.get('time_need') if payload.get('time_need') else datetime.today(),
            'proposed_date': payload.get('proposed_date') if payload.get('proposed_date') else datetime.today(),
            'intended_use': payload.get('intended_use'),
            'resource': payload.get('resource'),
            'quantity': payload.get('quantity'),
            'location': payload.get('location'),
        })
        if payload.get("approver_ids"):
            approver = eval(values['approver_ids'])
            for data in approver:
                user_approver = request.env['res.users'].sudo().search([('id', '=', data.get('user_id'))])
                approval.approver_ids += request.env['approval.approver'].sudo().create({
                    'user_id': user_approver.id,
                    'request_id': approval.id,
                    'status': data.get('status'),
                })
        if payload.get("product_line_ids"):
            line_ids = eval(values['product_line_ids'])
            for data in line_ids:
                # line = request.env['approval.product.line'].sudo().search([('id', '=', data.get('user_id'))])
                approval.product_line_ids += request.env['approval.product.line'].sudo().create({
                    'product_id': data.get('product_id'),
                    'description': data.get('description'),
                    'quantity': data.get('quantity'),
                    'approval_request_id': approval.id,
                })

    @validate_token
    @http.route("/api/v1/partner", type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def get_partner(self, **payload):
        values = []
        data = request.env['res.partner'].sudo().search([])
        for rec in data:
            dates = {'id': rec.id,
                     'name': rec.name,
                     }
            values.append(dates)
        return valid_response(values)

    @validate_token
    @http.route("/api/v1/get-category-approval", type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def get_category_approval(self, **payload):
        values = []
        data = request.env['approval.category'].sudo().search([])

        for rec in data:
            if rec.name == "Đăng ký đi muộn - về sớm":
                continue
            else:
                field_require = ['description_request']
                if rec.has_vehicle == 'required':
                    field_require.append('vehicle')
                if rec.has_time_need == 'required':
                    field_require.append('time_need')
                if rec.has_proposed_date == 'required':
                    field_require.append('proposed_date')
                if rec.has_intended_use == 'required':
                    field_require.append('intended_use')
                if rec.has_resource == 'required':
                    field_require.append('resource')
                if rec.has_partner == 'required':
                    field_require.append('partner')
                if rec.has_date_start == 'required':
                    field_require.append('date_start')
                if rec.has_department == 'required':
                    field_require.append('department')
                if rec.has_partner == 'required':
                    field_require.append('partner')
                if rec.has_job == 'required':
                    field_require.append('job')
                if rec.has_employee_id == 'required':
                    field_require.append('employee')
                if rec.has_period == 'required':
                    field_require.append('period')
                if rec.has_product == 'required':
                    field_require.append('product')
                if rec.has_quantity == 'required':
                    field_require.append('quantity')
                if rec.has_amount == 'required':
                    field_require.append('amount')
                if rec.has_reference == 'required':
                    field_require.append('reference')
                if rec.has_payment_method == 'required':
                    field_require.append('payment_method')
                if rec.has_location == 'required':
                    field_require.append('location')
                dates = {'id': rec.id,
                         'name': rec.name,
                         'field_require': field_require,
                         }
            values.append(dates)
        return valid_response(values)

    @validate_token
    @http.route("/api/v1/product", type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def get_product(self, **payload):
        values = []
        print()
        request.env.user.has_group('mail_group.group_mail_group_manager'),
        base_url = ApprovalsController.get_url_base(self)
        data = request.env['approval.product'].sudo().search([])
        for rec in data:
            dates = {'key': rec.id,
                     'name': rec.name,
                     'description': rec.description,
                     'price': rec.price,
                     'category': {'id': rec.category.id, 'name': rec.category.name},
                     'avatar': urls.url_join(base_url, '/web/image?model=approval.product&id={0}&field=image'.format(
                         rec.id)) if rec else '',
                     }
            values.append(dates)
        return valid_response(values)




