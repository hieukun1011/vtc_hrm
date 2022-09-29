from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ProjectTaskSendMail(models.TransientModel):

    _name = 'project.task.send.mail'
    _description = 'Send mail from project task'

    project_name = fields.Char('Project name')
    send_mail = fields.Boolean("Send Email", default=True, readonly=False)
    # template_id = fields.Many2one('mail.template', string='Email Template',
    #                             readonly=False,
    #                               domain="[('model', '=', 'res.users')]")
    user_ids = fields.Many2many('project.task')
    user_without_email = fields.Text(compute='_compute_user_without_email',
                                          string='Applicant(s) not having email')

    @api.depends('user_ids', 'send_mail')
    def _compute_user_without_email(self):
        for wizard in self:
            res_users = self.env['res.users'].browse(self.user_ids.ids)
            res_users_no_mail = res_users.filtered(lambda x: not x.email)
            if wizard.send_mail and res_users_no_mail:
                # print('user not email', res_users_no_mail)
                wizard.user_without_email = "%s\n%s" % (
                    _("The email will not be sent to the following user(s) as they don't have email address."),
                    "\n".join([i.login for i in res_users_no_mail])
                )
            else:
                wizard.user_without_email = False

    def action_project_task_send_mail(self):
        res_users = self.env['res.users'].browse(self.user_ids.ids)
        res_users_has_mail = res_users.filtered(lambda x: x.email)
        if self.send_mail:
            # if not self.template_id:
            #     raise UserError(_("Email template must be selected to send a mail"))
            if not res_users_has_mail:
                raise UserError(_("Email of the user is not set, email won't be sent."))

        if self.send_mail:
            # res_users_has_mail.with_context(active_test=True).message_post_with_template(self.template_id.id, **{
            #     'auto_delete_message': True,
            #     'subtype_id': self.env['ir.model.data']._xmlid_to_res_id('mail.mt_note'),
            #     'email_layout_xmlid': 'mail.mail_notification_light'
            # })

            mail_server = self.env['ir.mail_server'].sudo().search([('active', '=', True)], limit=1,
                                                                      order='sequence DESC')
            for each in res_users_has_mail:
                main_content = {
                    'subject': _("Thư thông báo."),
                    'email_from': mail_server.smtp_user,
                    'body_html': '<p>Xin chào %s.</p><p>Bạn được giao làm dự án: <strong>%s</strong></p>' %(each.name, self.project_name),  #.format(each.name, self.user_ids.name),
                    'email_to': each.email,
                }
                self.env['mail.mail'].sudo().create(main_content).send()

