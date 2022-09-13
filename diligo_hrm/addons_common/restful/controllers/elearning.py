"""Part of odoo. See LICENSE file for full copyright and licensing details."""

import logging

from odoo.addons.restful.common import (
    invalid_response,
    valid_response,
)
from odoo.addons.restful.controllers.main import (
    validate_token
)
from werkzeug import urls

from odoo import SUPERUSER_ID
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class ElearningController(http.Controller):

    def get_url_base(self):
        config = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if config:
            return config
        return 'https://test.diligo.vn:15000'

    @http.route("/api/v1/slide_channel", type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def get_source(self, **payload):
        """ API 1.13 Danh sách khóa học"""
        values = []
        headers = request.httprequest.headers
        base_url = ElearningController.get_url_base(self)
        data = request.env['slide.channel'].sudo().search([('website_published', '=', True),
                                                           ('enroll', '=', 'public'),
                                                           ('visibility', '=', 'public')
                                                           ])
        if headers.get("access_token"):
            user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
            if user:
                employee = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)])
                channels_my = request.env['slide.channel'].sudo().search([('website_published', '=', True),
                                                                          ('employee_id', 'in', employee.id),
                                                                          ])
                for channel in channels_my:
                    if channel not in data:
                        data += channel
        for rec in data:
            dates = {'name': rec.name,
                     'id': rec.id,
                     'description': rec.description,
                     'total_time': rec.total_time,
                     "avatar": urls.url_join(base_url,
                                             '/web/image?model=slide.channel&id={0}&field=image_1024'.format(
                                                 rec.id)),
                     'members_count': rec.members_count,
                     'avatar_lecturers': urls.url_join(base_url,
                                                       '/web/image?model=slide.channel&id={0}&field=lecturers.avatar'.format(
                                                           rec.id)),
                     'rating_lecturers': rec.lecturers.rating,
                     'department': rec.department_id if rec.department_id else rec.general_course_type}
            tag_ids = []
            for tag in rec.tag_ids:
                tag_ids.append({
                    'id': tag.id or '',
                    'name': tag.name or '',
                })
            dates['tag_ids'] = tag_ids
            # ____________________________________________________
            ratings = []
            for rat in rec.rating_ids:
                ratings.append({
                    'name': rat.rated_partner_name,
                    'partner': rat.partner_id.name,
                    'name_rating': rat.rated_partner_id.name,
                    'rating_text': rat.rating_text,
                    'rating': rat.rating,
                    'res_model': rat.res_model,
                    'res_model_id': rat.res_model_id,
                    'res_name': rat.res_name,
                    'res_id': rat.res_id,
                })
            dates['rating'] = ratings
            # ____________________________________________________
            comment = []
            for mes in rec.website_message_ids:
                comment.append({
                    'model': mes.model,
                    'body': mes.body,
                    'create_date': mes.create_date,
                    'description': mes.description,
                    'res_id': mes.res_id,
                    'author_id': mes.author_id.name,
                    'partner_ids': mes.partner_ids,
                    'reply_to': mes.reply_to,
                })
            dates['comment'] = comment
            # ____________________________________________________
            quiz_ids = []
            for quiz in rec.quiz_ids:
                quiz_ids.append({
                    'id': quiz.id or '',
                    'name': quiz.name or '',
                })
            dates['quiz_ids'] = quiz_ids
            # ____________________________________________________
            lecturers = []
            for lec in rec.lecturers:
                lecturers.append({
                    'id': lec.id or '',
                    'name': lec.name or '',
                    'seniority': lec.experience or '',
                    'position': lec.position or '',
                })
            dates['lecturers'] = lecturers
            lesson = []
            for cate in rec.slide_category_ids:
                category = {
                    'id': cate.id,
                    'title': cate.name,
                }
                lesson.append(category)
                slides = []
                for sl in cate.slide_ids:
                    slide = {
                        'id': sl.id,
                        'name': sl.name,
                        'type': sl.slide_type,
                        'url': sl.url,
                        'completion_time': sl.completion_time,
                        'description': sl.description,
                        'preview': sl.is_preview,
                    }
                    slides.append(slide)
                    questions = []
                    for ques in sl.question_ids:
                        question = {
                            'question': ques.question,
                        }
                        questions.append(question)
                        answers = []
                        for aw in ques.answer_ids:
                            answer = {
                                'value': aw.text_value,
                                'is_correct': aw.is_correct,
                                'comment': aw.comment,
                            }
                            answers.append(answer)
                        question['answers'] = answers
                    slide['questions'] = questions
                category['slides'] = slides
            dates['lesson'] = lesson
            values.append(dates)
        return valid_response(values)

    @validate_token
    @http.route("/api/v1/slide_channel/join_course", type="http", auth="public", methods=["POST"], csrf=False, cors='*')
    def join_course(self, **payload):
        field_require = [
            'course_id',
        ]
        for field in field_require:
            if field not in payload.keys():
                return invalid_response(
                    "Missing",
                    "The parameter %s is missing!!!" % field)
        headers = request.httprequest.headers
        slide_channel = request.env['slide.channel'].sudo().search([('id', '=', payload['course_id'])])
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        if user.self not in slide_channel.channel_partner_ids.partner_id:
            channel_partner = request.env['slide.channel.partner'].with_user(SUPERUSER_ID).create({
                'channel_id': slide_channel.id,
                'partner_id': user.self.id,
            })
        return invalid_response("Bạn đã tham gia thành công khóa học %s." % slide_channel.name)

    @validate_token
    @http.route("/api/v1/slide_channel/rating", type="http", auth="public", methods=["POST"], csrf=False, cors='*')
    def update_comment_slide_channel(self, **payload):
        field_require = [
            'res_id',
            'rating',
        ]
        for field in field_require:
            if field not in payload.keys():
                return invalid_response(
                    "Missing",
                    "The parameter %s is missing!!!" % field)
        headers = request.httprequest.headers
        slide_channel = request.env['slide.channel'].sudo().search([('id', '=', payload['res_id'])])
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        rating = request.env['rating.rating'].sudo().create({
            'res_id': slide_channel.id,
            'rating': payload['rating'],
            'partner_id': user.self.id,
            'res_model_id': request.env['ir.model']._get_id('slide.channel'),
        })
        return invalid_response("Bạn đã đánh giá vào khóa học %s." % slide_channel.name)

    @validate_token
    @http.route("/api/v1/slide_channel/comment", type="http", auth="public", methods=["POST"], csrf=False, cors='*')
    def update_comment_slide_channel(self, **payload):
        field_require = [
            'res_id',
            'body',
            'description',
        ]
        for field in field_require:
            if field not in payload.keys():
                return invalid_response(
                    "Missing",
                    "The parameter %s is missing!!!" % field)
        headers = request.httprequest.headers
        slide_channel = request.env['slide.channel'].sudo().search([('id', '=', payload['res_id'])])
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        comment = request.env['mail.message'].sudo().create({
            'subject': payload['body'],
            'email_from': user.self.email,
            'model': 'slide.channel',
            # _________________________
            'res_id': slide_channel.id,
            'body': payload['body'],
            'author_id': user.self.id,
        })
        return invalid_response("Bạn đã bình luận vào khóa học %s." % slide_channel.name)

    @validate_token
    @http.route("/api/v1/slide_channel/apply_member", type="http", auth="public", methods=["POST"], csrf=False, cors='*')
    def apply_member_slide_channel(self, **payload):
        field_require = [
            'channel_id',
        ]
        for field in field_require:
            if field not in payload.keys():
                return invalid_response(
                    "Missing",
                    "The parameter %s is missing!!!" % field)
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        channel_partner_ids = request.env['slide.channel.partner'].sudo().create({
            'channel_id': int(payload['channel_id']),
            'partner_id': user.self.id,
        })
