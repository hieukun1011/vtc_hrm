from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
class ProjectTaskType(models.Model):

    _inherit = "project.task.type"

    @api.onchange('name')
    def onchange_name_strip_space(self):
        if self.name:
            self.name = self.name.strip()

    # @api.constrains('name')
    # def _constrains_name_not_duplicate(self):
    #     list_names = self.env['project.task.type'].search([]).mapped('name')
    #     list_names.remove(self.name)
    #     list = []
    #     for each in list_names:
    #         if each.upper() not in list:
    #             list.append(each.upper())
    #         if each.lower() not in list:
    #             list.append(each.lower())
    #         if each not in list:
    #             list.append(each)
    #
    #     if self.name:
    #         if self.name in list or self.name.upper() in list or self.name.lower() in list:
    #             raise ValidationError("You already have that name. Please give another name.")


    # def unlink(self):
    #     res = super(ProjectTaskType, self).unlink()
    #     for rec in self:
    #         models.Model.unlink(rec)
    #     return res

    def update_project_task_type(self):
        list_dict = []
        all_types = self.env["project.task.type"].search([('user_id', '=', False)])
        # print(len(all_types))

        # all_types_fal = self.env["project.task.type"].search([])
        # print(len(all_types_fal))
        #
        # self.env.cr.execute("select id, name, active from project_task_type")
        # all = self.env.cr.dictfetchall()
        # print(len(all))

        list_all_types = list(all_types.mapped('name'))
        set_all_types = set(list_all_types)
        list_types_no_duplicate = list(set_all_types)

        for rec in all_types:
            list_dict.append({
                'id': rec.id,
                'name': rec.name,
                'project_ids': rec.project_ids.ids if rec.project_ids.ids else [],
            })

        # list dict lưu tất cả các giai đoạn nhiệm vụ có dự án đc gán k trùng lặp
        list_dict_short = []
        # với mỗi tên trong giai đoạn nhiệm vụ k trùng lặp
        for rec in list_types_no_duplicate:
            # so sánh mỗi dict trong ds dict của bảng
            list_id = []
            list_project_ids = []
            for dict in list_dict:
                if dict['name'] == rec:
                    list_id.append(dict['id'])
                    if dict['project_ids']:
                        list_project_ids.extend(dict['project_ids'])

            list_dict_short.append({
                'id': list_id,
                'name': rec,
                'project_ids': list(set(list_project_ids)),
            })

        # cập nhật lại dự án không có giai đoạn nhiệm vụ
        projects = self.env['project.project'].search(['|', ('active', '=', True), ('active', '=', False)])
        for project in projects:
            project.write({'type_ids': ()})

        # list dict lưu các bản ghi giai đoạn nhiệm vụ đc cập nhật
        list_dict_update_type = []
        for each in list_dict_short:
            if each['project_ids']:
                update_record = all_types.browse(each['id'][0])

                # gán giai đoạn nhiệm vụ cho dự án
                update_record.write({
                    'project_ids': each['project_ids'],
                })
                list_dict_update_type.append({
                    'id': update_record.id,
                    'name': update_record.name,
                })

                # update_projects = projects.browse(each['project_ids'])
                # for each in update_projects:
                #     tasks = each.task_ids
                #     for task in tasks:
                #         if task.stage_id.name == update_record.name:
                #             task.stage_id = update_record.id

        tasks = self.env['project.task'].search(['|', ('active', '=', True), ('active', '=', False)])

        for task in tasks:

            for type in list_dict_update_type:
                if task.stage_id.name == type['name']:
                    task.stage_id = type['id']




