from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime, time


class HolidaysDiligo(models.Model):
    _inherit = 'hr.leave.allocation'

    #accrual configuration
    allocation_type = fields.Selection(
        [
            ('regular', 'Regular Allocation'),
            ('accrual', 'Accrual Allocation'),
            ('cumulative_allocation', 'Cumulative Allocation'),
        ], string="Allocation Type", default="regular", required=True, readonly=True,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    interval_number = fields.Integer("Number of unit between two intervals", readonly=True,
                                     states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
                                     default=1)
    number_per_interval = fields.Float("Number of unit per interval", readonly=True,
                                       states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
                                       default=1)
    accrual_limit = fields.Integer('Balance limit', default=0,
                                   help="Maximum of allocation for accrual; 0 means no maximum.")
    unit_per_interval = fields.Selection([
        ('hours', 'Hours'),
        ('days', 'Days')
    ], string="Unit of time added at each interval", default='hours', readonly=True,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    interval_unit = fields.Selection([
        ('weeks', 'Weeks'),
        ('months', 'Months'),
        ('years', 'Years')
    ], string="Unit of time between two intervals", default='weeks', readonly=True,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})

    @api.model
    def _update_accrual(self):

        today_date = fields.Date.from_string(fields.Date.today())

        holidays = self.search(
            [('allocation_type', '=', 'cumulative_allocation'), ('employee_id.active', '=', True), ('state', '=', 'validate'),
             ('holiday_type', '=', 'employee'),
             '|', ('date_to', '=', False), ('date_to', '>', fields.Datetime.now()),
             '|', ('nextcall', '=', False), ('nextcall', '<=', today_date)])

        for holiday in holidays:
            values = {}

            delta = relativedelta(days=0)

            if holiday.interval_unit == 'weeks':
                delta = relativedelta(weeks=holiday.interval_number)
            if holiday.interval_unit == 'months':
                delta = relativedelta(months=holiday.interval_number)
            if holiday.interval_unit == 'years':
                delta = relativedelta(years=holiday.interval_number)

            values['nextcall'] = (holiday.nextcall if holiday.nextcall else today_date) + delta

            period_start = datetime.combine(today_date, time(0, 0, 0)) - delta
            period_end = datetime.combine(today_date, time(0, 0, 0))

            # We have to check when the employee has been created
            # in order to not allocate him/her too much leaves
            start_date = holiday.employee_id._get_date_start_work()
            # If employee is created after the period, we cancel the computation
            if period_end <= start_date:
                holiday.write(values)
                continue

            # If employee created during the period, taking the date at which he has been created
            if period_start <= start_date:
                period_start = start_date

            employee = holiday.employee_id
            worked = employee._get_work_days_data_batch(
                period_start, period_end,
                domain=[('holiday_id.holiday_status_id.unpaid', '=', True), ('time_type', '=', 'leave')]
            )[employee.id]['days']
            left = employee._get_leave_days_data_batch(
                period_start, period_end,
                domain=[('holiday_id.holiday_status_id.unpaid', '=', True), ('time_type', '=', 'leave')]
            )[employee.id]['days']
            prorata = worked / (left + worked) if worked else 0

            days_to_give = holiday.number_per_interval
            if holiday.unit_per_interval == 'hours':
                # As we encode everything in days in the database we need to convert
                # the number of hours into days for this we use the
                # mean number of hours set on the employee's calendar
                days_to_give = days_to_give / (employee.resource_calendar_id.hours_per_day or HOURS_PER_DAY)

            values['number_of_days'] = holiday.number_of_days + days_to_give * prorata
            if holiday.accrual_limit > 0:
                values['number_of_days'] = min(values['number_of_days'], holiday.accrual_limit)

            holiday.write(values)

    def _prepare_holiday_values(self, employees):
        self.ensure_one()
        return [{
            'name': self.name,
            'holiday_type': 'employee',
            'holiday_status_id': self.holiday_status_id.id,
            'notes': self.notes,
            'number_of_days': self.number_per_interval,
            'parent_id': self.id,
            'employee_id': employee.id,
            'employee_ids': [(6, 0, [employee.id])],
            'state': 'confirm',
            'allocation_type': self.allocation_type,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'accrual_plan_id': self.accrual_plan_id.id,
        } for employee in employees]

    @api.model
    def create(self, vals_list):
        print(vals_list)
        # overridden to automatically invite user to sign up
        users = super(HolidaysDiligo, self).create(vals_list)
        return users

    @api.constrains('holiday_status_id')
    def _onchange_holiday_status_id(self):
        for record in self:
            if record.holiday_status_id.validity_stop and record.date_to:
                new_date_to = datetime.combine(record.holiday_status_id.validity_stop, time.max)
                if new_date_to < record.date_to:
                    record.date_to = new_date_to

            if record.allocation_type == 'cumulative_allocation':
                record.number_of_days = 0

                if record.holiday_status_id.request_unit == 'hour':
                    record.unit_per_interval = 'hours'
                else:
                    record.unit_per_interval = 'days'
            else:
                record.interval_number = 1
                record.interval_unit = 'weeks'
                record.number_per_interval = 1
                record.unit_per_interval = 'hours'

class ValiStop(models.Model):
    _inherit = 'hr.leave.type'

    validity_stop = fields.Date("To")

