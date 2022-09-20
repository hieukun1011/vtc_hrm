from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ProjectTaskSendMail(models.TransientModel):

    _name = 'project.task.send.mail'
    _description = 'Send mail from project task'

    send_mail = fields.Boolean("Send Email", default=False, readonly=False)
    template_id = fields.Many2one('mail.template', string='Email Template',
                                readonly=False,
                                  domain="[('model', '=', 'res.users')]")
    user_ids = fields.Many2many('project.task')
    user_without_email = fields.Text(compute='_compute_user_without_email',
                                          string='Applicant(s) not having email')

    @api.depends('user_ids', 'send_mail')
    def _compute_user_without_email(self):
        for wizard in self:
            users = wizard.user_ids.filtered(lambda x: not x.partner_id.email) # not x.user_ids.email and   and not x.manager_ids.email
            if users and wizard.send_mail:
                wizard.user_without_email = "%s\n%s" % (
                    _("The email will not be sent to the following user(s) as they don't have email address."),
                    "\n".join([i.name for i in users])
                )
            else:
                wizard.user_without_email = False

    def action_project_task_send_mail(self):
        # print('res users', self.user_ids.user_ids)

        # if self.send_mail:
        #     if not self.template_id:
        #         raise UserError(_("Email template must be selected to send a mail"))
        #     # if not self.user_ids.user_ids.filtered(lambda x: x.email):
        #     #     raise UserError(_("Email of the user is not set, email won't be sent."))
        #     if not self.user_ids.user_ids:
        #         raise UserError(_("User has not account, email won't be sent."))

        if self.send_mail:
            users = self.user_ids.user_ids.filtered(lambda x: x.email)
            # print('mail', users)
            users.with_context(active_test=True).message_post_with_template(self.template_id.id, **{
                'auto_delete_message': True,
                'subtype_id': self.env['ir.model.data']._xmlid_to_res_id('mail.mt_note'),
                'email_layout_xmlid': 'mail.mail_notification_light'
            })