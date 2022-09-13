"""Part of odoo. See LICENSE file for full copyright and licensing details."""
import logging

import pytz
from odoo.addons.restful.common import (
    valid_response,
)
from werkzeug import urls

from odoo import http
from odoo.http import request

from datetime import datetime

_logger = logging.getLogger(__name__)


class DeviceController(http.Controller):

    def get_url_base(self):
        config = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if config:
            return config
        return 'https://test.diligo.vn:15000'

    @http.route("/api/v1/device", type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def get_device(self, **payload):
        """ API 1.13 Danh sách tin tuyển dụng"""
        values = []
        uid = request.uid
        user = request.env['res.users'].browse(int(uid))
        if user.tz:
            tz = pytz.timezone(user.tz)
        else:
            tz = pytz.timezone('Asia/Ho_Chi_Minh')
        base_url = DeviceController.get_url_base(self)
        device = request.env['sci.device.main'].sudo().search([])
        for rec in device:
            data = {'id': rec.id,
                    'name': rec.name or '',
                    'code': rec.default_code or '',
                    'area': rec.area or '',
                    'channel': {'id': rec.channel.id, 'name': rec.channel.name} or '',
                    'category': {'id': rec.category_id.id, 'name': rec.category_id.name} or '',
                    'team_id': {'id': rec.team_id.id, 'name': rec.team_id.name} or '',
                    'department': {'id': rec.department_id.id, 'name': rec.department_id.name} or '',
                    'parent': {'id': rec.parent_id.id, 'name': rec.parent_id.name} or '',
                    'employee': {'id': rec.employee_id.id, 'name': rec.employee_id.name} or '',
                    'serial': rec.serial_no or '',
                    'date_import': datetime.combine(rec.date_import, datetime.min.time()).astimezone(tz=tz).strftime('%Y-%m-%d') or '',
                    'first_date_use': datetime.combine(rec.first_date_use, datetime.min.time()).astimezone(tz=tz).strftime('%Y-%m-%d') or '',
                    'period': rec.period or '',
                    'location': rec.location or '',
                    'partner': rec.partner_id or '',
                    'description': rec.description or '',
                    'maintenance_deadline': rec.maintenance_deadline or '',
                    'last_maintenance': rec.last_maintenance or '',
                    'maintenance_expire_date': rec.maintenance_expire_date or '',
                    'maintenance_status': rec.maintenance_status or '',
                    }
            img = [{
                'img': urls.url_join(base_url,
                                 '/web/image?model=sci.device.main&id={0}&field=image_1920'.format(
                                     rec.id))
                    }]
            for images in rec.description_images_ids:
                img.append({
                    'img': urls.url_join(base_url, '/web/image?model=sci.device.image&id={0}&field=image'.format(
                        images.id)),
                })
            data['image_device'] = img
            # ____________________________________________________
            device_extra = []
            for extra in rec.extra_device_ids:
                extra_device = {
                    'id': extra.id,
                    'name': extra.name,
                    'code': extra.code,
                    'amount': extra.amount,
                    'price': extra.price,
                    'date_import': datetime.combine(extra.date_import, datetime.min.time()).astimezone(tz=tz).strftime('%Y-%m-%d') or '',
                    'first_date_use': datetime.combine(extra.first_date_use, datetime.min.time()).astimezone(tz=tz).strftime('%Y-%m-%d') or '',
                    'period': extra.period or '',
                    'partner': extra.partner or '',
                    'description': extra.description or '',
                }
                device_extra.append(extra_device)
                image = []
                for img in extra.description_images_ids:
                    imgs = {
                        'id': img.id,
                        'name': img.name,
                        'description': img.description,
                        'img': urls.url_join(base_url,
                                             '/web/image?model=sci.device.image&id={0}&field=image'.format(
                                                 img.id)),
                    }
                    image.append(imgs)
                extra_ids = []
                for ex in extra.parts_in_device_ids:
                    exs = {
                        'id': ex.id,
                        'name': ex.name,
                        'code': ex.code,
                        'amount': ex.amount,
                        'price': ex.price,
                        'date_import': datetime.combine(ex.date_import, datetime.min.time()).astimezone(tz=tz).strftime('%Y-%m-%d') or '',
                        'first_date_use': datetime.combine(ex.first_date_use, datetime.min.time()).astimezone(tz=tz).strftime('%Y-%m-%d') or '',
                        'period': ex.period or '',
                        'partner': ex.partner or '',
                        'description': ex.description or '',
                    }
                    extra_ids.append(exs)
                    images = []
                    for ig in ex.description_images_ids:
                        igs = {
                            'id': ig.id,
                            'name': ig.name,
                            'description': ig.description,
                            'img': urls.url_join(base_url,
                                                 '/web/image?model=sci.device.image&id={0}&field=image'.format(
                                                     ig.id)),
                        }
                        images.append(igs)
                    extra_ids.append(images)
                extra_device['extra_ids'] = extra_ids
                extra_device['image'] = image
            data['device_extra'] = device_extra
            values.append(data)
        return valid_response(values)

    @http.route('/api/v1/device/get-by', type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def get_by_device(self, **payload):
        values = []
        uid = request.uid
        user = request.env['res.users'].browse(int(uid))
        if user.tz:
            tz = pytz.timezone(user.tz)
        else:
            tz = pytz.timezone('Asia/Ho_Chi_Minh')
        base_url = DeviceController.get_url_base(self)
        device_list = request.env['sci.device.main'].sudo().search([('default_code', '=', payload.get('default_code'))])
        for rec in device_list:
            data = {
                'id': rec.id,
                'name': rec.name or '',
                'code': rec.default_code or '',
                'area': rec.area or '',
                'channel': {'id': rec.channel.id, 'name': rec.channel.name} or '',
                'category': {'id': rec.category_id.id, 'name': rec.category_id.name} or '',
                'team_id': {'id': rec.team_id.id, 'name': rec.team_id.name} or '',
                'department': {'id': rec.department_id.id, 'name': rec.department_id.name} or '',
                'parent': {'id': rec.parent_id.id, 'name': rec.parent_id.name} or '',
                'employee': {'id': rec.employee_id.id, 'name': rec.employee_id.name} or '',
                'serial': rec.serial_no or '',
                'date_import': rec.date_import or '',
                'first_date_use': rec.first_date_use or '',
                'period': rec.period or '',
                'location': rec.location or '',
                'partner': rec.partner_id or '',
                'description': rec.description or '',
                'maintenance_deadline': rec.maintenance_deadline or '',
                'last_maintenance': rec.last_maintenance or '',
                'maintenance_expire_date': rec.maintenance_expire_date or '',
                'maintenance_status': rec.maintenance_status or '',
            }
            img = [{
                'img': urls.url_join(base_url,
                                 '/web/image?model=sci.device.main&id={0}&field=image_1920'.format(
                                     rec.id))
            }]
            for images in rec.description_images_ids:
                img.append({
                    'img': urls.url_join(base_url, '/web/image?model=sci.device.image&id={0}&field=image'.format(
                        images.id)),
                })
            data['image_device'] = img
            # ____________________________________________________
            device_extra = []
            for extra in rec.extra_device_ids:
                extra_device = {
                    'id': extra.id,
                    'name': extra.name,
                    'code': extra.code,
                    'amount': extra.amount,
                    'price': extra.price,
                    'date_import': extra.date_import or '',
                    'first_date_use': extra.first_date_use or '',
                    'period': extra.period or '',
                    'partner': extra.partner or '',
                    'description': extra.description or '',
                }
                device_extra.append(extra_device)
                image = []
                for img in extra.description_images_ids:
                    imgs = {
                        'id': img.id,
                        'name': img.name,
                        'description': img.description,
                        'img': urls.url_join(base_url,
                                             '/web/image?model=sci.device.image&id={0}&field=image'.format(
                                                 img.id)),
                    }
                    image.append(imgs)
                extra_ids = []
                for ex in extra.parts_in_device_ids:
                    exs = {
                        'id': ex.id,
                        'name': ex.name,
                        'code': ex.code,
                        'amount': ex.amount,
                        'price': ex.price,
                        'date_import': ex.date_import or '',
                        'first_date_use': ex.first_date_use or '',
                        'period': ex.period or '',
                        'partner': ex.partner or '',
                        'description': ex.description or '',
                    }
                    extra_ids.append(exs)
                    images = []
                    for ig in ex.description_images_ids:
                        igs = {
                            'id': ig.id,
                            'name': ig.name,
                            'description': ig.description,
                            'img': urls.url_join(base_url,
                                                 '/web/image?model=sci.device.image&id={0}&field=image'.format(
                                                     ig.id)),
                        }
                        images.append(igs)
                    extra_ids.append(images)
                extra_device['extra_ids'] = extra_ids
                extra_device['image'] = image
            data['device_extra'] = device_extra
            values.append(data)
        return valid_response(values)


    @http.route('/api/v1/device/get-by-area', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_device_by_area(self, area=None, **payload):
        values = []
        base_url = DeviceController.get_url_base(self)

        domain, fields, offset, limit, order = extract_arguments(**payload)
        device_list = request.env['sci.device.main'].search(domain, offset=offset, limit=limit)
        if area:
            domain = [("area", "=", area)]
            device_list = request.env['sci.device.main'].search(domain,offset=offset, limit=limit)

        for rec in device_list:
            data = {'id': rec.id,
                    'name': rec.name or '',
                    'code': rec.default_code or '',
                    'category': {'id': rec.channel.id, 'name': rec.channel.name} or '',
                    'team_id': {'id': rec.team_id.id, 'name': rec.team_id.name} or '',
                    'department': {'id': rec.department_id.id, 'name': rec.department_id.name} or '',
                    'parent': {'id': rec.parent_id.id, 'name': rec.parent_id.name} or '',
                    'employee': {'id': rec.employee_id.id, 'name': rec.employee_id.name} or '',
                    'serial': rec.serial_no or '',
                    'area': rec.area or '',
                    'date_import': rec.date_import or '',
                    'first_date_use': rec.first_date_use or '',
                    'period': rec.period or '',
                    'location': rec.location or '',
                    'partner': rec.partner_id or '',
                    'description': rec.description or '',
                    'maintenance_deadline': rec.maintenance_deadline or '',
                    'last_maintenance': rec.last_maintenance or '',
                    'maintenance_expire_date': rec.maintenance_expire_date or '',
                    'maintenance_status': rec.maintenance_status or '',
                    }
            img = [{
                'img': urls.url_join(base_url,
                                     '/web/image?model=sci.device.main&id={0}&field=image_1920'.format(
                                         rec.id))
            }]
            for images in rec.description_images_ids:
                img.append({
                    'img': urls.url_join(base_url,
                                         '/web/image?model=sci.device.image&id={0}&field=image'.format(
                                             images.id)),
                })
            data['image_device'] = img
            # ____________________________________________________
            device_extra = []
            for extra in rec.extra_device_ids:
                extra_device = {
                    'id': extra.id,
                    'name': extra.name,
                    'code': extra.code,
                    'amount': extra.amount,
                    'price': extra.price,
                    'date_import': extra.date_import or '',
                    'first_date_use': extra.first_date_use or '',
                    'period': extra.period or '',
                    'partner': extra.partner or '',
                    'description': extra.description or '',
                }
                device_extra.append(extra_device)
                image = []
                for img in extra.description_images_ids:
                    imgs = {
                        'id': img.id,
                        'name': img.name,
                        'description': img.description,
                        'img': urls.url_join(base_url,
                                             '/web/image?model=sci.device.image&id={0}&field=image'.format(
                                                 img.id)),
                    }
                    image.append(imgs)
                extra_ids = []
                for ex in extra.parts_in_device_ids:
                    exs = {
                        'id': ex.id,
                        'name': ex.name,
                        'code': ex.code,
                        'amount': ex.amount,
                        'price': ex.price,
                        'date_import': ex.date_import or '',
                        'first_date_use': ex.first_date_use or '',
                        'period': ex.period or '',
                        'partner': ex.partner or '',
                        'description': ex.description or '',
                    }
                    extra_ids.append(exs)
                    images = []
                    for ig in ex.description_images_ids:
                        igs = {
                            'id': ig.id,
                            'name': ig.name,
                            'description': ig.description,
                            'img': urls.url_join(base_url,
                                                 '/web/image?model=sci.device.image&id={0}&field=image'.format(
                                                     ig.id)),
                        }
                        images.append(igs)
                    extra_ids.append(images)
                extra_device['extra_ids'] = extra_ids
                extra_device['image'] = image
            data['device_extra'] = device_extra
            values.append(data)
        if device_list:
            return valid_response(values)
        else:
            return valid_response({})