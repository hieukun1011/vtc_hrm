import base64
import logging
from datetime import date, datetime
from io import BytesIO

from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
from openpyxl import load_workbook
from odoo.tools import config, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat

from odoo import fields, api, models, _

try:
    import xlrd

    try:
        from xlrd import xlsx
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None

try:
    from . import odf_ods_reader
except ImportError:
    odf_ods_reader = None

_logger = logging.getLogger(__name__)

class HrEmployeeKPI(models.Model):
    _inherit = 'hr.employee'

    kpi_ids = fields.One2many('sh.employee.kpi', 'employee_name', string="KPI")

class SHEmployeeKPI(models.Model):
    _name = 'sh.employee.kpi'
    _description = "Chi tiết kpi nhân viên"

    name = fields.Char("Tên")
    employee_name = fields.Many2one('hr.employee', string='Nhân viên')
    payroll_kpi_id = fields.Many2one('payroll.kpi', 'Kỳ KPI')
    date_start = fields.Date(related='payroll_kpi_id.date_start', store=True)
    date_end = fields.Date(related='payroll_kpi_id.date_end', store=True)
    nv_complete = fields.Float('NV_hoàn thành(%)')
    nv_point = fields.Float('NV_điểm(%)')
    ld_complete = fields.Float('LĐ_hoàn thành(%)')
    ld_point = fields.Float('LĐ_điểm(%)')
    attachment_id = fields.Many2many('ir.attachment', 'employee_kpi_rel', 'employee_kpi_id', 'attach_kpi',
                                     string="Tệp đính kèm", help='You can attach the copy of your Letter')

    @api.onchange('employee_name')
    def onchange_employee_name(self):
        if self.employee_name:
            self.name = self.employee_name.name

class PayrollKPI(models.Model):
    _name = 'payroll.kpi'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    STATES = [
        ('Draft', 'Nháp'),
        ('Confirmed', 'Đã xác nhận'),
    ]
    name = fields.Char(string='Kỳ KPI #', size=64, required=True, default=lambda *a: '/')
    date_start = fields.Date(string='Date From', required=True, readonly=True,
                             states={'draft': [('readonly', False)]},
                             default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
    date_end = fields.Date(string='Date To', required=True, readonly=True,
                           states={'draft': [('readonly', False)]},
                           default=lambda self: fields.Date.to_string(
                               (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))
    info = fields.Text(string='Mô tả', readonly=True, states={'Draft': [('readonly', False)]}, tracking=True)
    state = fields.Selection(STATES, 'Trạng thái', readonly=True, default=lambda *a: 'Draft', tracking=True)
    department_ids = fields.Many2many('hr.department', string='Phòng ban', readonly=False,
                                      states={'Confirmed': [('readonly', True)]}, tracking=True)
    business_results = fields.Float('Business results')
    total_profit = fields.Float('Total profit')

    sh_employee_kpi = fields.One2many('sh.employee.kpi', 'payroll_kpi_id', string='Chi tiết KPI nhân viên', ondelete="cascade")

    _sql_constraints = [
        ('date_start_date_end_uniq', 'unique (date_start,date_end)', 'Chu kỳ KPI tháng 4 đã có!.')
    ]

    @api.onchange('department_ids')
    def _onchange_department_ids(self):
        self.sh_employee_kpi = False
        data_recheck = []
        for service_done in self.department_ids:
            data_reexam = self.env['hr.employee'].search([('department_id', 'in', service_done.ids)])
            for item in data_reexam:
                data_recheck.append((0, 0, {
                    'name': item.name,
                    'employee_name': item.id,
                }))
        self.sh_employee_kpi = data_recheck

    def action_confirm(self):
        return self.write({'state': 'Confirmed'})

    def render_kpi_employee(self):
        for record in self.sh_employee_kpi:
            if record.attachment_id:
                walkin_attachment = record.attachment_id
                decode = base64.b64decode(walkin_attachment.datas)
                book = xlrd.open_workbook(file_contents=decode or b'')
                if book.nsheets < 2:
                    raise UserError(_("File PP bị sai cấu trúc, xin vui lòng kiểm tra lại file PP trước khi upload KPI"))
                else:
                    sh = book.sheet_by_index(1)
                    record.nv_complete = sh.cell_value(14, 5)
                    record.nv_point = sh.cell_value(14, 6)
                    record.ld_complete = sh.cell_value(14, 7)
                    record.ld_point = sh.cell_value(14, 8)
