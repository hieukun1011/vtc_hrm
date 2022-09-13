"""Part of odoo. See LICENSE file for full copyright and licensing details."""
import logging

from odoo.addons.restful.common import (
    extract_arguments,
    valid_response,
)
from odoo.addons.restful.controllers.main import (
    validate_token
)
from werkzeug import urls

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class AnnouncementController(http.Controller):

    def get_url_base(self):
        config = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if config:
            return config
        return 'https://test.diligo.vn:15000'

    @validate_token
    @http.route("/api/v1/announcement", type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def get_announcement(self, **payload):
        values = []
        base_url = AnnouncementController.get_url_base(self)

        employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.uid)])
        domain = ['|', '|', '|', ('is_announcement', '=', True),
                       ('employee_ids', 'in', [employee.id]),
                       ('position_ids', 'in', [employee.job_id.id]),
                       ('department_ids', 'in', [employee.department_id.id])]
        fields = [
            'id', 'name', 'announcement_reason', 'date_start',
            'date_end', 'is_announcement', 'announcement_type',
            'announcement', 'attachment_id'
        ]
        data = request.env['hr.announcement'].sudo().search_read(
            domain=domain, fields=fields, offset=None, limit=None, order=None)
        for rec in data:
            dates = {'id': rec.get('id'),
                     'code': rec.get('name'),
                     'title': rec.get('announcement_reason'),
                     'date_start': rec.get('date_start'),
                     'date_end': rec.get('date_end'),
                     'is_announcement': rec.get('is_announcement'),
                     'announcement_type': rec.get('announcement_type'),
                     'content': rec.get('announcement'),
                     }
            # Có thể có nhiều hơn 1 file đính kèm.
            list_attachment = [urls.url_join(base_url, self.get_url_attachment(att_id)) for att_id in rec.get('attachment_id')]
            dates['file'] = list_attachment
            values.append(dates)
        return valid_response(values)

    def get_url_attachment(self, attachment_id):
        attachment = request.env['ir.attachment'].sudo().browse(attachment_id)
        return "web/content2/?model=ir.attachment&id=" + str(attachment_id) + "&filename_field=name&field=datas&download=true&name=" + attachment.name


