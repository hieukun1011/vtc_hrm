# # -*- coding: utf-8 -*-
# import json
# import logging
#
# from odoo.addons.website.controllers.form import WebsiteForm  # Import the class
# from odoo.addons.website_hr_recruitment.controllers.main import WebsiteHrRecruitment  # Import the class
# from psycopg2 import IntegrityError
# from werkzeug.exceptions import NotFound
#
# from odoo import http
# from odoo.exceptions import ValidationError
# from odoo.http import request
#
# _logger = logging.getLogger(__name__)
#
#
# class WebsiteHomePageJob(http.Controller):
#
#     @http.route('/', type='http', auth="public", website=True, sitemap=True)
#     def index(self, **kw):
#         print('12312313242532')
#         # prefetch all menus (it will prefetch website.page too)
#         top_menu = request.website.menu_id
#
#         homepage = request.website.homepage_id
#         print(homepage)
#         if homepage and (
#                 homepage.sudo().is_visible or request.env.user.has_group('base.group_user')) and homepage.url != '/':
#             print('ejnfwnfw')
#             return request.env['ir.http'].reroute(homepage.url)
#
#         website_page = request.env['ir.http']._serve_page()
#         print(website_page)
#         jobs_office = request.env['hr.job'].search([('website_published', '=', True),
#                                                     ('state', '=', 'recruit'),
#                                                     ('work_address', '=', 'office')], limit=4)
#
#         jobs_factory = request.env['hr.job'].search([('website_published', '=', True),
#                                                      ('state', '=', 'recruit'),
#                                                      ('work_address', '=', 'factory')], limit=4)
#
#         jobs_inventory = request.env['hr.job'].search([('website_published', '=', True),
#                                                        ('state', '=', 'recruit'),
#                                                        ('work_address', '=', 'inventory')], limit=4)
#
#         jobs_south = request.env['hr.job'].search([('website_published', '=', True),
#                                                    ('state', '=', 'recruit'),
#                                                    ('work_address', '=', 'south')], limit=4)
#
#         if website_page:
#             values = {
#                 'jobs_office': jobs_office,
#                 'jobs_factory': jobs_factory,
#                 'jobs_south': jobs_south,
#                 'jobs_inventory': jobs_inventory,
#             }
#             return request.render("diligo_fontend.diligo_homepage", values)
#             # print('$$$$$$$$$$$$$$$$$')
#             # return website_page
#         else:
#             first_menu = top_menu and top_menu.child_id and top_menu.child_id.filtered(lambda menu: menu.is_visible)
#             if first_menu and first_menu[0].url not in ('/', '', '#') and (
#             not (first_menu[0].url.startswith(('/?', '/#', ' ')))):
#                 return request.redirect(first_menu[0].url)
#         print('!!!!!!!!!!!!!!!!!!')
#         raise request.not_found()
#
# class ApplyDistributors(http.Controller):
#
#     @http.route('/apply-distributors', type='http', auth='public',
#                 website=True)
#     def apply_distributors(self):
#         countries = request.env['res.country.state'].search([('country_id.id', '=', request.env.ref('base.vn').id)])
#         data = {
#             'countries': countries
#         }
#         return request.render('diligo_fontend.apply_distributors', data)
#
#     @http.route('/apply-distributors/state/<model("res.country.state"):state_id>', type='json', auth='public',
#                 website=True)
#     def get_district(self, state_id):
#         districts = dict(((district['id'], district['name']) for district in state_id.district_ids))
#         return districts
#
#     @http.route('/apply-distributors/district/<model("res.country.district"):district_id>', type='json',
#                 auth='public',
#                 website=True)
#     def get_wards(self, district_id):
#         wards = dict(((ward['id'], ward['name']) for ward in district_id.ward_ids))
#         return wards
#
