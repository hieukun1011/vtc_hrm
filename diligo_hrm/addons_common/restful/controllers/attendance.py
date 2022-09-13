"""Part of odoo. See LICENSE file for full copyright and licensing details."""
import logging

import pytz
from odoo.addons.restful.common import (
    invalid_response,
    valid_response
)
from odoo.addons.restful.controllers.main import (
    validate_token, get_access_token
)
from datetime import datetime, date
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class AttendanceController(http.Controller):

    @validate_token
    @http.route("/api/v1/attendance", type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def get_attendance(self, **payload):
        values = []
        if not all([payload.get('date_from', False), payload.get('date_to', False)]):
            return invalid_response(
                "Missing",
                "The parameter is missing!!!")
        # Date format 'YYYY-mm-dd'
        data = request.env['hr.attendance'].sudo().search([
            ('employee_id.user_id', '=', request.uid),
            ('date_attendance', '>=', payload.get('date_from')),
            ('date_attendance', '<=', payload.get('date_to'))])
        for rec in data:
            tz = pytz.timezone(rec.employee_id.tz)
            dates = {'id': rec.id,
                     'employee': rec.employee_id.name,
                     'check_in_device': rec.checkin_device_id.name,
                     'check_out_device': rec.checkout_device_id.name,
                     'state': rec.state,
                     }
            if rec.check_in:
                dates['check_in'] = rec.check_in.astimezone(tz)
            else:
                dates['check_in'] = None,

            if rec.check_out:
                dates['check_out'] = rec.check_out.astimezone(tz)
            else:
                dates['check_out'] = None,

            values.append(dates)

        return valid_response(values)
