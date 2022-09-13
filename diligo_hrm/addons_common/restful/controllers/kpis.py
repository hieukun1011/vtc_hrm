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


class EmployeeKPIController(http.Controller):

    def get_url_base(self):
        config = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if config:
            return config
        return 'https://test.diligo.vn:15000'

    @validate_token
    @http.route("/api/v1/kpi", type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def get_pki_employee(self, **payload):
        values = []
        base_url = EmployeeKPIController.get_url_base(self)
        headers = request.httprequest.headers
        data = request.env['sh.employee.kpi'].sudo().search(
            [('employee_name.user_id', '=', request.uid)])
        for rec in data:
            dates = {'id': rec.id,
                     'employee': rec.name,
                     'nv_complete': rec.nv_complete,
                     'nv_point': rec.nv_point,
                     'ld_complete': rec.ld_complete,
                     'ld_point': rec.ld_point,
                     'date_start': rec.payroll_kpi_id.date_start,
                     'date_end': rec.payroll_kpi_id.date_end,
                     'file': urls.url_join(base_url, "web/content2/?model=ir.attachment&id=" + str(
                         rec.attachment_id.id) + "&filename_field=name&field=datas&download=true&name=" + rec.attachment_id.name) if rec.attachment_id else '-',
                     }
            values.append(dates)
        return valid_response(values)
