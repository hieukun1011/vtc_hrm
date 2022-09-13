from odoo import fields, models, api

class HrJobs(models.Model):
    _inherit = 'hr.job'

    work_address = fields.Selection([('office', 'Office'), #van phong
                                     ('factory', 'Factory'), #nha may
                                     ('inventory', 'Inventory'), #kho van
                                     ('south', 'South'), #mien nam
                                     ('distributors', 'Distributors'), #nha phan phoi
                                     ], string='Work address', required=True)
