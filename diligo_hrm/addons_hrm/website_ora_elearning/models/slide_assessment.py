# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
from odoo.tools import is_html_empty


class Slide(models.Model):
    _inherit = 'slide.slide'

    prompt_ids = fields.One2many('open.response.prompt', 'slide_id')
    rubric_ids = fields.One2many('open.response.rubric', 'slide_id')
    peer_assessment = fields.Boolean("Peer Assessment")
    peer_limit = fields.Integer("Peer Limit")
    response_ids = fields.Many2many('ora.response', string="Responses", compute="_get_user_responses")
    response_count = fields.Integer("Responses", compute="_get_user_responses")

    def _get_user_responses(self):
        for rec in self:
            rec.response_ids = False
            rec.response_count = 0
            total_response = []
            if rec.prompt_ids:
                user_response_ids = self.env['ora.response'].search([
                    ('slide_id', '=', rec.id)
                ])
                if user_response_ids:
                    rec.response_ids = [(6, 0, user_response_ids.ids)]
                    for response in user_response_ids:
                        if not response.user_id in total_response:
                            total_response.append(response.user_id)
                    rec.response_count = len(total_response)

    def action_open_responses(self):
        action = self.env['ir.actions.act_window']._for_xml_id('website_ora_elearning.action_ora_response')
        action['domain'] = [('id', 'in', self.response_ids.ids)]
        return action

    def _create_answer(self, user=False):
        user_response = self.env['ora.response']
        vals = {
            'user_id': user,
            'slide_id': self.id,
            'state': 'active'
        }
        val_line = []
        for prompt_id in self.prompt_ids:
            val_line.append((0, 0, {
                'prompt_id': prompt_id.id,
            }))
        vals['user_response_line'] = val_line
        vals['slide_rubric_ids'] = [(6, 0, self.rubric_ids.ids)]
        user_response = user_response.create(vals)
        return user_response

    @api.model
    def _assign_peer_response(self):
        """ Cron Job for responses which has not been assigned to peers. """
        ora_response_ids = self.env['ora.response'].search([('state', '=', 'submitted')])
        for ora_response in ora_response_ids:
            slide_id = ora_response.slide_id
            if slide_id.peer_assessment:
                peer_limit = slide_id.peer_limit
                enrolled_users = slide_id.channel_id.partner_ids.ids
                if peer_limit <= len(enrolled_users):
                    peer_limit = peer_limit
                else:
                    peer_limit = len(enrolled_users)
                assigned_ids = ora_response.slide_rubric_staff_line.filtered(lambda l: l.assess_type == 'peer')
                if len(assigned_ids) < peer_limit:
                    for _ in range(peer_limit):
                        peer_user = slide_id._get_peer_user(ora_response)
                        if peer_user:
                            self.env['open.response.rubric.staff'].create({
                                'assess_type': 'peer',
                                'user_id': peer_user.id,
                                'state': 'in_progress',
                                'response_id': ora_response.id
                            })

    def _get_peer_user(self, ora_response):
        ''' Iterate over response and course users and check whether course user is assigned to the response or not.
        :param response: Current response on which we are checking the peers.
        :return: A res.users record or None.
        '''
        enrolled_users = list(set(self.channel_id.partner_ids.ids) - set(ora_response.user_id.partner_id.ids))
        peer_limit = self.peer_limit
        to_allocate_user = {}
        for partner_id in enrolled_users:
            rubric_line_ids = self.env['open.response.rubric.staff'].search([
                ('assess_type', '=', 'peer'),
                ('user_id.partner_id', '=', partner_id),
                ('response_id', '!=', False),
                ('response_id.state', 'in', ['submitted'])
            ])
            to_allocate_user.setdefault(partner_id, {})
            to_allocate_user[partner_id]['peer_count'] = len(rubric_line_ids)
            to_allocate_user[partner_id]['responses'] = rubric_line_ids.mapped('response_id').ids
        # Remove ids whose peer limit has reached.
        to_allocate_user = dict((key, val) for key, val in to_allocate_user.items() if val['peer_count'] < peer_limit)
        # Sorting dict w.r.t peer_count.
        sorted_allocate_user_dic = dict(sorted(to_allocate_user.items(), key=lambda x: x[1]['peer_count']))
        # Appending those users in list whose responses does not have current response.
        user_ids = list(key for key, val in sorted_allocate_user_dic.items() if ora_response.id not in val['responses'])
        if user_ids:
            return self.env['res.users'].search([('partner_id', '=', user_ids[0])], limit=1)


class ORA_Prompt(models.Model):
    _name = 'open.response.prompt'
    _order = "sequence"

    sequence = fields.Integer("Sequence")
    name = fields.Text("Description", translate=True)
    slide_id = fields.Many2one('slide.slide')
    question_name = fields.Html("Question", required=True, translate=True)
    response_type = fields.Selection([
        ('text', 'Text'),
        ('rich_text', 'Rich Text')
    ], default='text', string="Response Type", required=True)


class ORA_Rubric(models.Model):
    _name = 'open.response.rubric'
    _rec_name = 'criterian_name'

    name = fields.Text("Description", required=True, translate=True)
    slide_id = fields.Many2one('slide.slide')
    criterian_name = fields.Char("Criterian Name", required=True, translate=True)
    criterian_ids = fields.One2many('rubric.criterian', "rubric_id", "Options")


class RubricCriterian(models.Model):
    _name = 'rubric.criterian'

    rubric_id = fields.Many2one('open.response.rubric')
    name = fields.Char("Option", required=True, translate=True)
    option_desc = fields.Text("Option Description", required=True, translate=True)
    option_points = fields.Integer("Points", required=True)


class ORAResponse(models.Model):
    _name = 'ora.response'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'slide_id'
    _description = "Response"

    slide_id = fields.Many2one('slide.slide', "Content")
    user_id = fields.Many2one('res.users', "User")
    staff_id = fields.Many2one(related="slide_id.channel_id.user_id", string="Staff", store=True)
    feedback = fields.Html("Feedback", translate=True)
    can_resubmit = fields.Boolean("Allow Resubmit")
    xp_points = fields.Integer("XP Points", compute="calculate_total_xp", store=True)
    user_response_line = fields.One2many('open.response.user.line', 'response_id' , string="Prompts")
    slide_rubric_ids = fields.Many2many('open.response.rubric', string="Rubric")
    slide_rubric_staff_line = fields.One2many('open.response.rubric.staff', 'response_id')
    submitted_date = fields.Datetime("Submitted Date", readonly=False)
    state = fields.Selection([
        ('active', 'Active'),
        ('submitted', 'Submitted'),
        ('inactive', 'Inactive'),
        ('assessed', 'Assessed')
    ], default="active", tracking=True)

    @api.depends('slide_rubric_staff_line.total_score')
    def calculate_total_xp(self):
        for rec in self:
            total_xp = 0
            for line in rec.slide_rubric_staff_line:
                if line.assess_type == 'staff':
                    total_xp += line.total_score
            rec.xp_points = total_xp

    def action_mark_assessed(self):
        if self.state == 'submitted':
            only_peer = True
            for line in self.slide_rubric_staff_line:
                if line.assess_type == 'staff':
                    self.state = 'assessed'
                    line.state = 'completed'
                    user_karma = self.user_id.karma
                    user_karma += self.xp_points
                    self.sudo().user_id.karma = user_karma
                    only_peer = False
            if only_peer:
                raise UserError("Please fill the rubric first.")


class OpenResponseUserLine(models.Model):
    _name = 'open.response.user.line'

    response_id = fields.Many2one('ora.response', ondelete="cascade")
    value_text_box = fields.Text("Text answer", translate=True)
    value_richtext_box = fields.Html("Richtext answer", translate=True)
    slide_id = fields.Many2one(related="response_id.slide_id")
    prompt_id = fields.Many2one('open.response.prompt', ondelete='cascade', string="Prompt")
    question_name = fields.Html("Question", related='prompt_id.question_name', store=True)
    question_sequence = fields.Integer('Sequence', related='prompt_id.sequence', store=True)
    response_type = fields.Selection(string="Response Type", related="prompt_id.response_type")


class OpenResponseRubricStaff(models.Model):
    _name = 'open.response.rubric.staff'

    response_id = fields.Many2one('ora.response', ondelete="cascade")
    assess_type = fields.Selection([
        ('peer', 'Peer'),
        ('staff', 'Staff')
    ], default='staff', required=True)
    user_id = fields.Many2one('res.users', string="User", required=True)
    total_score = fields.Integer('Total Score', compute="calculate_total_score", store=True)
    state = fields.Selection([
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], default="in_progress", readonly=True, string="Status")
    submitted_date = fields.Datetime("Submitted Date")
    option_ids = fields.One2many('open.response.rubric.assess', 'response_assess_id')

    @api.depends('option_ids.criteria_option_point')
    def calculate_total_score(self):
        for rec in self:
            total_score = 0
            for line in rec.option_ids:
                total_score += line.criteria_option_point
            rec.total_score = total_score


class OpenResponseRubricAssess(models.Model):
    _name = 'open.response.rubric.assess'

    criteria_id = fields.Many2one('open.response.rubric', 'Criteria', required=True)
    criteria_desc = fields.Text(related='criteria_id.name')
    option_id = fields.Many2one('rubric.criterian', 'Options', required=True)
    criteria_option_desc = fields.Text(related='option_id.option_desc')
    criteria_option_point = fields.Integer(related='option_id.option_points')
    assess_explanation = fields.Text("Assess Explanation", required=True, translate=True)
    response_assess_id = fields.Many2one('open.response.rubric.staff', ondelete="cascade")

    @api.onchange('criteria_id')
    def onchange_criteria_id(self):
        for rec in self:
            rubric_ids = rec.response_assess_id.response_id.slide_id.rubric_ids.ids
            return {
                'domain': {
                    'criteria_id': [('id', 'in', rubric_ids)]
                }
            }

class SlideChannel(models.Model):
    _inherit = 'slide.channel'

    department_id = fields.Selection([
        ('ht', 'Ban Hiền tài'),
        ('ccu', 'Ban Chuỗi cung ứng'),
        ('cn', 'Ban Công nghệ'),
        ('ks', 'Ban Kiểm soát'),
        ('ptsp', 'Ban Phát triển thương hiệu và sản phẩm'),
        ('ptkh', 'Ban Phát triển khách hàng'),
        ('kt', 'Ban Tài chính kế toán'),
    ], string="Department")
    internal_training = fields.Boolean('Internal training')
    employee_id = fields.Many2many('hr.employee', string='Participation employee')
    general_course = fields.Boolean('General course')
    general_course_type = fields.Selection([
        ('orientation_integration', 'Orientation and integration'),
        ('training_industry', 'Training industry')
    ], string="General course type")
    name_lecturers = fields.Char('Name lecturers')
    rating = fields.Selection([('1', 'Rất tệ'),
                               ('2', 'Tệ'),
                               ('3', 'Bình thường'),
                               ('4', 'Tốt'),
                               ('5', 'Rất tốt')], string='Đánh giá')
    phone_lecturers = fields.Char('Phone lecturers')
    email_lecturers = fields.Char('Email lecturers')
    experience_lecturers = fields.Char('Experience lecturers')
    position_lecturers = fields.Char('Position lecturers')
    introduce_lecturers = fields.Text('Introduce lecturers')
    count_source = fields.Integer(related='lecturers.count_source', string='Count source')
    count_student = fields.Integer(related='lecturers.count_student', string='Count student')
    lecturers = fields.Many2one('channel.lecturers', string='Lecturers')

    @api.onchange('general_course')
    def clear_type_source(self):
        if self.general_course == True:
            self.department_id = False
        else:
            self.general_course_type = False

    @api.onchange('lecturers')
    def render_infor_lecturers(self):
        if self.lecturers:
            self.name_lecturers = self.lecturers.name
            self.phone_lecturers = self.lecturers.phone
            self.email_lecturers = self.lecturers.email
            self.rating = self.lecturers.rating
            self.experience_lecturers = self.lecturers.experience
            self.position_lecturers = self.lecturers.position


    @api.constrains('employee_id')
    def create_slide_channel_partner(self):
        for record in self:
            channel_employee = self.env['slide.channel.partner'].search([('channel_id', '=', record.id),
                                                                         ('internal_training', '=', True)])
            for employee in record.employee_id:
                if employee not in channel_employee.employee_id:
                    record.channel_partner_ids += self.env['slide.channel.partner'].create({
                        'channel_id': record.id,
                        'employee_id': employee.id,
                        # 'partner_id': employee.user_id.partner_id or '',
                    })
            for rec in channel_employee:
                if rec.employee_id not in record.employee_id:
                    rec.unlink()

    @api.constrains('internal_training')
    def clear_employee_id(self):
        for record in self:
            if record.internal_training == False:
                record.employee_id = None
                record.channel_partner_ids = None
            else:
                record.visibility = 'members'


    def write(self, vals):
        # If description_short wasn't manually modified, there is an implicit link between this field and description.
        if not is_html_empty(vals.get('description')) and is_html_empty(
                vals.get('description_short')):
            vals['description_short'] = vals.get('description')

        res = super(SlideChannel, self).write(vals)

        if vals.get('user_id'):
            self._action_add_members(self.env['res.users'].sudo().browse(vals['user_id']).partner_id)
            self.activity_reschedule(['website_slides.mail_activity_data_access_request'],
                                     new_user_id=vals.get('user_id'))
        if 'enroll_group_ids' in vals:
            self._add_groups_members()

        return res

class ChannelLecturers(models.Model):
    _name = 'channel.lecturers'
    _description = 'Channel Lecturers'

    user_id = fields.Many2one('res.users', string='User')
    avatar = fields.Image('Avatar', related='user_id.image_1920')
    name = fields.Char('Name')
    email = fields.Char('Email')
    phone = fields.Char('Phone')
    experience = fields.Char('Experience')
    position = fields.Char('Position')
    introduce = fields.Text('Introduce')
    count_source = fields.Integer('Count source', default=0, compute='calculate_count_student_and_source')
    count_student = fields.Integer('Count student', default=0, compute='calculate_count_student_and_source')
    rating = fields.Selection([('1', 'Rất tệ'),
                               ('2', 'Tệ'),
                               ('3', 'Bình thường'),
                               ('4', 'Tốt'),
                               ('5', 'Rất tốt')], string='Đánh giá')
    slide_channel_ids = fields.One2many('slide.channel', 'lecturers')

    @api.onchange('user_id')
    def render_infor(self):
        if self.user_id:
            self.name = self.user_id.name
            self.email = self.user_id.login

    @api.depends('slide_channel_ids')
    def calculate_count_student_and_source(self):
        for record in self:
            if record.slide_channel_ids:
                record.count_source = len(record.slide_channel_ids)
                record.count_student = len(record.slide_channel_ids.channel_partner_ids)
            else:
                record.count_source = 0
                record.count_student = 0