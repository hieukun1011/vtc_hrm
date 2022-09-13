from odoo import fields, models, api

class HRDepartment(models.Model):
    _inherit = 'hr.department'

    # 2 truong đếm số nhan vien va don vi cap duoi
    child_department_count = fields.Integer(string='child nums', compute='count_department', store=True)
    employee_count = fields.Integer(string='emp nums', compute='count_employee')
    root_code = fields.Char(string="Mã(phòng ban)")

    def name_get(self):
        # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
        return [(template.id, '%s%s' % (template.root_code and '[%s] ' % template.root_code or '', template.name))
                for template in self]

    @api.model
    def create(self, vals):
        res = super(HRDepartment, self).create(vals)
        return res

    def write(self, vals):
        if vals.get('company_id'):
            for dep in self.child_ids:
                dep.company_id = vals.get('company_id')
            for emp in self.member_ids:
                emp.company_id = vals.get('company_id')
            lst_job = self.env['hr.job'].search([('department_id', '=', self.id)])
            for item in lst_job:
                item.company_id == vals.get('company_id')

        res = super(HRDepartment, self).write(vals)

        return res

    def _update_employee_manager(self, manager_id):
        employees = self.env['hr.employee']
        if manager_id:
            for department in self:
                employees = employees | self.env['hr.employee'].search([
                    ('id', '!=', manager_id),
                    ('department_id', '=', department.id),
                    ('parent_id', '=', department.manager_id.id)
                ])
                for emp in employees:
                    emp.write({'parent_id': manager_id})

    # ham dem don vi cap duoi
    @api.depends('child_ids')
    def count_department(self):
        for item in self:
            if item.id:
                item.child_department_count = len(item.child_ids)
            else:
                item.child_department_count = 0

    # ham dem nhan vien trong don vi
    @api.depends('member_ids')
    def count_employee(self):
        for item in self:
            if item.id:
                child_list = self.env['hr.department'].search([('parent_id', 'child_of', [item.id])])
                for dep in child_list:
                    item.employee_count += len(dep.member_ids)
            else:
                item.employee_count = 0

    # button to link manager
    def action_get_manager_view(self):
        if self.manager_id:
            return {
                'name': 'Manager',  # Lable
                'res_id': self.manager_id.id,
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'hr.employee',  # your model
                # 'target': 'new',  # if you want popup
                # 'context': ctx,  # if you need
            }
        else:
            return None

class Channels(models.Model):
    _name = 'hr.channel'

    name = fields.Char('Tên kênh')
    code = fields.Char('Mã kênh')
    area = fields.Selection([('factory', 'Nhà máy'), ('office', 'Văn phòng'), ('inventory', 'Kho vận')], default='office', string='Khu vực')
    member_ids = fields.One2many('hr.employee', 'channel_id', string='Member')
