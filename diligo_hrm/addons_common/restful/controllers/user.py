"""Part of odoo. See LICENSE file for full copyright and licensing details."""
import logging

from odoo.addons.restful.common import (
    valid_response,
)
from odoo.addons.restful.controllers.main import (
    validate_token
)

from werkzeug import urls
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class ResUsersController(http.Controller):

    def get_url_base(self):
        config = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if config:
            return config
        return 'https://test.diligo.vn:15000'

    @validate_token
    @http.route("/api/v1/res_users", type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def get_res_users(self, **payload):
        values = []
        base_url = ResUsersController.get_url_base(self)
        data = request.env['res.users'].sudo().search([])
        for rec in data:
            dates = {'id': rec.id,
                     'name': rec.name,
                     'avatar': urls.url_join(base_url,
                                            '/web/image?model=res.users&id={0}&field=image_1920'.format(
                                                rec.id)),
                     }
            values.append(dates)
        return valid_response(values)
