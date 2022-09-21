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
        list = []
        for each in list_names:
            if each.upper() not in list:
                list.append(each.upper())
            if each.lower() not in list:
                list.append(each.lower())
            if each not in list:
                list.append(each)

        for rec in self:
            if rec.name and rec.name in list:
                raise ValidationError("You already have that name. Please give another name.")


