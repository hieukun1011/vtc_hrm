from odoo import fields, models, api

class SlideChannelPartner(models.Model):
    _inherit = 'slide.channel.partner'

    employee_id = fields.Many2one('hr.employee', string='Employee')
    internal_training = fields.Boolean(related='channel_id.internal_training')
    partner_id = fields.Many2one('res.partner', index=True, required=False, ondelete='cascade')
    partner_email = fields.Char(string='Email', readonly=True)
    course_on_off = fields.Selection([
        ('on', 'Online'),
        ('off', 'Offline')
    ], default='on', required=True)
    channel_id2 = fields.Char()
    start_day = fields.Date(string='Ngày bắt đầu')
    end_date = fields.Date(string='Ngày kết thúc')

    @api.onchange('partner_id', 'employee_id')
    def render_email(self):
        if self.employee_id:
            self.partner_email = self.employee_id.work_email
        elif self.partner_id:
            self.partner_email = self.partner_id.email


    @api.model
    def create(self, vals_list):
        channel_partner = super(SlideChannelPartner, self).create(vals_list)
        if channel_partner.employee_id not in channel_partner.channel_id.employee_id:
            channel_partner.channel_id.employee_id += channel_partner.employee_id
        return channel_partner


