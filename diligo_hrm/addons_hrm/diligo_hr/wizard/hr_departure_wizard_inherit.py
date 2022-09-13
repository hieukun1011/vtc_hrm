# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import date
from odoo import api, fields, models


class HrDepartureWizard(models.TransientModel):
    _inherit = 'hr.departure.wizard'


    def action_register_departure(self):
        employee = self.employee_id
        if self.env.context.get('toggle_active', False) and employee.active:
            employee.with_context(no_wizard=True).toggle_active()
        employee.departure_reason_id = self.departure_reason_id
        employee.departure_description = self.departure_description
        employee.departure_date = self.departure_date
        employee.stages_history += self.env['hr.employee.status.history'].sudo().create({
                        'state': employee.state,
                        'start_date': employee.joining_date,
                        'end_date': date.today(),
                        'duration': employee.work_duration
                    })
        employee.state = 'terminated'
        employee.work_email = None
        if employee.user_id:
            employee.user_id.sudo().write({
                'active': False
            })
            employee.user_id = None
        if self.archive_private_address:
            # ignore contact links to internal users
            private_address = employee.address_home_id
            if private_address and private_address.active and not self.env['res.users'].search([('partner_id', '=', private_address.id)]):
                private_address.toggle_active()
