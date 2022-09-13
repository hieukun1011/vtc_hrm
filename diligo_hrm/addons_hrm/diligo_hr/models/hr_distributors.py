from odoo import fields, models, api

class HrDistributors(models.Model):
    _name = 'hr.distributors'
    _description = 'Apply Distributors'

    name = fields.Char('Name')
    res_country_state = fields.Many2one('res.country.state', string='Country state',
                                        domain="[('country_id', '=', 'VN')]")
    res_country_ward = fields.Many2one('res.country.ward', string='Country ward')
    res_country_district = fields.Many2one('res.country.district', string='Country district')
    address_distributors = fields.Char('Address distributors')
    document_type = fields.Many2many('document.type', string='Document')
    partner_id = fields.Many2one('res.partner', string='Partner')
    employee_id = fields.Many2one('hr.employee', string='Instructor employee')
    phone = fields.Char('Phone')
