"""Part of odoo. See LICENSE file for full copyright and licensing details."""

import logging

from odoo.addons.restful.common import (
    invalid_response,
)
from odoo.addons.restful.common import (
    valid_response_once,
)
from odoo.addons.restful.common import (
    invalid_response,
    valid_response,
    valid_response_once,
)
from odoo.addons.restful.controllers.main import (
    validate_token
)
from werkzeug import urls

from odoo import fields
from odoo import http
from odoo.http import request
import pytz

_logger = logging.getLogger(__name__)


class BlogController(http.Controller):

    def get_url_base(self):
        config = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if config:
            return config
        return 'https://test.diligo.vn:15000'

    @http.route("/api/v1/blog", type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def get_blog(self, **payload):
        values = []
        base_url = BlogController.get_url_base(self)
        uid = request.uid
        user = request.env['res.users'].browse(int(uid))
        if user.tz:
            tz = pytz.timezone(user.tz)
        else:
            tz = pytz.timezone('Asia/Ho_Chi_Minh')
        list_blog = request.env['blog'].sudo().search(
            ['|', ('website_published', '=', True), ('date_push', '<=', fields.date.today())])
        for rec in list_blog:
            rec.website_published = True
            data = {'id': rec.id,
                    'title': rec.name,
                    'avatar': urls.url_join(base_url,
                                            '/web/image?model=blog&id={0}&field=image_1920'.format(
                                                rec.id)),
                    'create_date': rec.create_date.astimezone(tz=tz) or '',
                    'create_by': {'id': rec.create_uid.id, 'name': rec.create_uid.name, 'avatar': urls.url_join(base_url,
                                            '/web/image?model=res.users&id={0}&field=image_1920'.format(
                                                rec.create_uid.id))} or '',
                    # 'content': rec.content or '',
                    'url': rec.url or '',
                    'description': rec.description or '',
                    }
            blog = []
            for tg in rec.tag_ids:
                blog.append({
                    'id': tg.id or '',
                    'name': tg.name or '',
                })
            data['quiz_ids'] = blog
            meta = []
            for mt in rec.meta:
                meta.append({
                    'id': mt.id or '',
                    'name': mt.tag or '',
                })
            data['meta'] = meta
            values.append(data)
        if list_blog:
            return valid_response(values)
        else:
            return valid_response_once({})

    @http.route("/api/v1/blog-by-id", type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def get_blog_by_id(self, **payload):
        values = []
        if not payload.get('blog_id', False):
            return invalid_response(
                "Missing",
                "The parameter blog_id is missing!!!")
        base_url = BlogController.get_url_base(self)
        uid = request.uid
        user = request.env['res.users'].browse(int(uid))
        if user.tz:
            tz = pytz.timezone(user.tz)
        else:
            tz = pytz.timezone('Asia/Ho_Chi_Minh')
        list_blog = request.env['blog'].sudo().search([('id', '=', payload.get('blog_id'))])
        for rec in list_blog:
            rec.website_published = True
            data = {'id': rec.id,
                    'title': rec.name,
                    'avatar': urls.url_join(base_url,
                                            '/web/image?model=blog&id={0}&field=image_1920'.format(
                                                rec.id)),
                    'create_date': rec.create_date.astimezone(tz=tz) or '',
                    'create_by': {'id': rec.create_uid.id, 'name': rec.create_uid.name} or '',
                    'content': rec.content or '',
                    'url': rec.url or '',
                    'description': rec.description or '',
                    }
            blog = []
            for tg in rec.tag_ids:
                blog.append({
                    'id': tg.id or '',
                    'name': tg.name or '',
                })
            data['quiz_ids'] = blog
            meta = []
            for mt in rec.meta:
                meta.append({
                    'id': mt.id or '',
                    'name': mt.tag or '',
                })
            data['meta'] = meta
            values.append(data)
        if list_blog:
            return valid_response(values)
        else:
            return valid_response_once({})

    @validate_token
    @http.route("/api/v1/update-total-view", type="http", auth="public", methods=["POST"], csrf=False, cors='*')
    def update_total_view_blog(self, **payload):
        # headers = request.httprequest.headers
        # user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        values = {}
        for k, v in payload.items():
            values[k] = v
        field_require = [
            'id',
            'total_view',
        ]
        for field in field_require:
            if field not in payload.keys():
                return invalid_response(
                    "Missing",
                    "The parameter %s is missing!!!" % field)
        blog = request.env['blog'].sudo().search([('id', '=', payload.get('id'))])
        if blog:
            blog.write({
                'total_view': blog.total_view + payload.get('total_view')
            })
