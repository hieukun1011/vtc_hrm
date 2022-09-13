"""Part of odoo. See LICENSE file for full copyright and licensing details."""
import logging

from odoo.addons.restful.common import (
    invalid_response,
    valid_response,
    valid_response_once,
)
from odoo.addons.restful.controllers.main import (
    validate_token
)
from datetime import datetime
from odoo import SUPERUSER_ID
from odoo import http, fields
from odoo.http import request

_logger = logging.getLogger(__name__)


class QuizController(http.Controller):

    @validate_token
    @http.route("/api/v1/quiz", type="http", auth="public", methods=["GET"], csrf=False, cors='*')
    def get_source(self, **payload):
        """ API 1.13 Danh sách tin tuyển dụng"""
        values = []
        quiz = request.env['op.quiz'].sudo().search([
            ('state', '=', 'open'),
            ('start_date', '<=', fields.datetime.now()),
            ('end_date', '>=', fields.datetime.now())
        ])
        for rec in quiz:
            data = {'id': rec.id,
                    'name': rec.name or '',
                    'category': {'id': rec.categ_id.id, 'name': rec.categ_id.name} or '',
                    'quiz_config': rec.quiz_config or '',
                    'total_marks': rec.quiz_config or '',
                    'start_date': rec.start_date or '',
                    'total_result_user': request.env['op.quiz.result'].search_count([('quiz_id', '=', rec.id),
                                                                                     ('user_id', '=', request.uid)]),
                    'end_date': rec.end_date or '',
                    'quiz_title': rec.quiz_html or '',
                    'quiz_description': rec.description or '',
                    'type': rec.type or '',
                    'config': {
                        'single_que': rec.single_que,
                        'prev_allow': rec.prev_allow,
                        'prev_readonly': rec.prev_readonly,
                        'no_of_attempt': rec.no_of_attempt,
                        'que_required': rec.que_required,
                        'auth_required': rec.auth_required,
                        'show_result': rec.show_result,
                        'right_ans': rec.right_ans,
                        'wrong_ans': rec.wrong_ans,
                        'not_attempt_ans': rec.not_attempt_ans,
                        'time_config': rec.time_config,
                        'time_limit_hr': rec.time_limit_hr,
                        'time_limit_minute': rec.time_limit_minute,
                    }
                    }
            questions = []
            if rec.type == 'integration_exam':
                data['department'] = {'id': rec.department_id.id, 'name': rec.department_id.name} or '',
            elif rec.type == 'channel_slide':
                data['slide_channel'] = {'id': rec.slide_channel_id.id, 'name': rec.slide_channel_id.name} or '',
            if rec.quiz_config == 'quiz_bank_selected':
                for ques in rec.line_ids:
                    question = {
                        'name': ques.name,
                        'id': ques.id,
                        'mark': ques.mark,
                        'type': ques.que_type,
                    }
                    questions.append(question)
                    answers = []
                    for ret in ques.line_ids:
                        answer = {
                            'answer': ret.name,
                            'id': ret.id,
                            'grade': {'name': ret.grade_id.name, 'id': ret.grade_id.id,
                                      'value': ret.grade_id.value} or '',
                        }
                        answers.append(answer)
                    question['answer'] = answers

            elif rec.quiz_config == 'quiz_bank_random':
                for bank_question in rec.config_ids:
                    for ques in bank_question.bank_id.line_ids:
                        question = {
                            'id': ques.id,
                            'name': ques.name,
                            'mark': ques.mark,
                            'type': ques.que_type,
                        }
                        questions.append(question)
                        answers = []
                        for ret in ques.line_ids:
                            answer = {
                                'id': ret.id,
                                'answer': ret.name,
                                'grade': {'name': ret.grade_id.name, 'id': ret.grade_id.id,
                                          'value': ret.grade_id.value} or '',
                            }
                            answers.append(answer)
                        question['answers'] = answers
            data['questions'] = questions
            values.append(data)
        if quiz:
            return valid_response(values)
        else:
            return valid_response_once({})

    @validate_token
    @http.route("/api/v1/quiz/result", type="http", auth="public", methods=["POST"], csrf=False, cors='*')
    def record_result_quiz(self, **payload):
        field_require = [
            'quiz_id',
            'finish_date',
            'score',
            'categ_id',
            'total_correct',
            'total_incorrect',
            'line_ids',
            'total_question',
        ]
        for field in field_require:
            if field not in payload.keys():
                return invalid_response(
                    "Missing",
                    "The parameter %s is missing!!!" % field)
            quiz = request.env['op.quiz'].sudo().search([('id', '=', payload.get('quiz_id'))])
        result = request.env['op.quiz.result'].with_user(request.uid).create({
            'name': quiz.name,
            'quiz_id': quiz.id,
            'user_id': request.uid,
            'categ_id': quiz.categ_id.id,
            'total_marks': quiz.total_marks,
            'score': payload.get('score'),
            'finish_date': datetime.now(),
            # 'total_question': payload.get('total_question'),
            'total_correct': payload.get('total_correct'),
            'total_incorrect': payload.get('total_incorrect'),
        })
        supervisor = eval(payload.get('line_ids'))
        result.total_question = len(supervisor)
        for record in supervisor:
            if record.get('answer_user') == record.get('answer'):
                result.total_correct += 1
                line = request.env['op.quiz.result.line'].sudo().create({
                    'name': record.get('question'),
                    'answer': record.get('answer'),
                    'given_answer': record.get('answer_user'),
                    'question_mark': record.get('mark'),
                    'mark': record.get('mark'),
                    'result_id': result.id,
                })
            else:
                result.total_incorrect += 1
                line = request.env['op.quiz.result.line'].sudo().create({
                    'name': record.get('question'),
                    'answer': record.get('answer'),
                    'given_answer': record.get('answer_user'),
                    'question_mark': record.get('mark'),
                    'mark': 0,
                    'result_id': result.id,
                })


