from odoo import api, fields, models
from odoo.exceptions import ValidationError
class ProjectTaskType(models.Model):

    _inherit = "project.task.type"

    @api.onchange('name')
    def onchange_name_strip_space(self):
        if self.name:
            self.name = self.name.strip()

    @api.constrains('name')
    def _constrains_name_not_duplicate(self):
        list_names = self.env['project.task.type'].search([]).mapped('name')
        for rec in self:
            if rec.name:
                if rec.name in list_names or rec.name.upper() in list_names or rec.name.lower() in list_names:
                    raise ValidationError("You already have that name. Please give another name.")

