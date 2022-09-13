# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions(odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo import models, fields, api


class EmployeeMasterInherit(models.Model):
    _inherit = 'hr.employee'

    @api.depends('document_checklist_ids')
    def document_checklist(self):
        for each in self:
            total_len = self.env['document.type'].search_count([])
            entry_len = len(each.document_checklist_ids)
            if total_len != 0:
                each.document_checklist = (entry_len * 100) / total_len

    document_checklist_ids = fields.Many2many('document.type', 'hr_employee_ids', string='Danh sách hồ sơ')
    document_checklist = fields.Float(compute=document_checklist, string='Hồ sơ', store=True, default=0.0)
    maximum_rate = fields.Integer(default=100)
    check_list_enable = fields.Boolean(invisible=True, copy=False)

    @api.constrains('document_checklist_ids')
    def create_document(self):
        for ret in self:
            document = self.env["hr.employee.document"].search([
                ('employee_ref', '=', ret.id)
            ])
            for record in ret.document_checklist_ids:
                if record not in document.document_type:
                    self.env["hr.employee.document"].create({
                        "employee_ref": ret.id,
                        "document_type": record.id,
                    })
            for rec in document:
                if rec.document_type not in ret.document_checklist_ids:
                    # rec.write({'active': True})
                    rec.unlink()



class EmployeeChecklistInherit(models.Model):
    _inherit = 'document.type'

    hr_employee_ids = fields.Many2many('hr.employee', 'document_checklist_ids', invisible=1)
