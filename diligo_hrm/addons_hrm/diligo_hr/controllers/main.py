# -*- coding: utf-8 -*-
import json
import logging

from odoo.addons.website.controllers.form import WebsiteForm  # Import the class
from odoo.addons.website_hr_recruitment.controllers.main import WebsiteHrRecruitment  # Import the class
from psycopg2 import IntegrityError
from werkzeug.exceptions import NotFound

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)

class WebsiteSearchJob(http.Controller):
    @http.route(['''/jobs''',
                '''/jobs/page/<int:page>'''], type='http', auth='public', website=True)
    def search_job(self, page=0, search='', industry='', location='', countries='', **post):
        domain = [('website_published', '=', True), ('state', '=', 'recruit')]
        # get industries
        industries = request.env['hr.industry.job'].search([])

        countries = request.env['res.country.state'].search([('country_id.id', '=', request.env.ref('base.vn').id)])
        location_dict = {}
        results = None
        if search:
            post["search_key"] = search
            domain += [('name', 'ilike', search)]
        if industry:
            post["industry"] = industry
            if industry == 0:
                industry = None
            else:
                domain += [('job_industry.id', '=', industry)]
        if location:
            post['location'] = location
            if location != 'all':
                domain += [('city_id.id', '=', location)]
                # domain += [('city_id.id', '=', location)]
        results = request.env['hr.job'].sudo().search(domain)
        count = len(results)
        model_ids = request.env['hr.job'].search(domain)
        total = model_ids.search_count(domain)
        pager = request.website.pager(
            url='/jobs',
            total=total,
            page=page,
            step=9,
        )
        offset = pager['offset']
        jobs_obj = model_ids[offset: offset + 9]
        if not results:
            values = {
                'jobs': None,
                'pager': pager,
                'model_ids': model_ids,
                'jobs_obj': jobs_obj,
                'industries': industries,
                'countries': countries,
            }
            return request.render("website_hr_recruitment.index", values)
        else:
            values = {
                'jobs': jobs_obj,
                'model_ids': model_ids,
                'pager': pager,
                'total': total,
                'jobs_obj': jobs_obj,
                'industries': industries,
                'count_result': count,
                'countries': countries,
            }
            return request.render("website_hr_recruitment.index", values)

class CustomWebsiteHrRecruitmentController(WebsiteHrRecruitment):

    @http.route('''/jobs/detail/<model("hr.job", "[('website_id', 'in', (False, current_website_id))]"):job>''',
                type='http', auth="public", website=True)
    def jobs_detail(self, job, **kwargs):
        job = job.sudo()
        job_department = request.env['hr.job'].sudo().search([('department_id.id', '=', job.department_id.id),
                                                              ('id', '!=', job.id),
                                                              ('state', '=', 'recruit')], limit=4)
        res = super(CustomWebsiteHrRecruitmentController, self).jobs_detail(job, **kwargs)
        if kwargs.get('source'):
            base_url = http.request.env["ir.config_parameter"].sudo().get_param("web.base.url")
            res.set_cookie('job_source', kwargs.get('source'), '/', 'localhost')
            cook_lang = request.httprequest.cookies.get('job_source')
            _logger.info(cook_lang)
        else:
            res.set_cookie('job_source', '')

        # render hightlight recruiment
        domain = [('website_published', '=', True), ('highlight', '=', True), ('id', '!=', job.id)]
        base_url = request.httprequest.url
        url_split = base_url.split('.')
        hot_recruitment = request.env['hr.job'].sudo().search(domain, limit=3, order='write_date desc')
        result = []
        for rec in hot_recruitment:
            result.append(rec)
        department_job = []
        for record in job_department:
            department_job.append(record)

        if department_job:
            value = {
                'highlight_job': result,
                'job_department': department_job,
                'job': job,
                'main_object': job,
            }
            return request.render("diligo_hr.view_detail_jobs_inherit", value)
        else:
            value = {
                'job': job,
                'main_object': job,
            }
            return request.render("diligo_hr.view_detail_jobs_inherit", value)
        return res

    @http.route('''/jobs/apply/<model("hr.job", "[('website_id', 'in', (False, current_website_id))]"):job>''',
                type='http', auth="public", website=True)
    def jobs_apply(self, job, **kwargs):
        if not job.can_access_from_current_website():
            raise NotFound()

        error = {}
        default = {}
        if 'website_hr_recruitment_error' in request.session:
            error = request.session.pop('website_hr_recruitment_error')
            default = request.session.pop('website_hr_recruitment_default')
        return request.render("diligo_hr.view_apply_jobs_inherit", {
            'job': job,
            'error': error,
            'default': default,
        })

    @http.route('/information-lookup', type='http', auth='public',
                website=True)
    def information_lookup(self):
        return request.render('diligo_hr.information_lookup')

    @http.route('/results-information-lookup', type='http', auth='public',
                website=True)
    def results_information_lookup(self, **post):
        # applicant_email = request.env['hr.applicant'].sudo().search([('email_from', '=', post['email'])])
        # applicant_phone = request.env['hr.applicant'].sudo().search([('partner_phone', '=', post['phone'])])
        # data = {
        #     'applicant_email': applicant_email,
        #     'applicant_phone': applicant_phone,
        # }
        return request.render('diligo_hr.results_information_lookup')
