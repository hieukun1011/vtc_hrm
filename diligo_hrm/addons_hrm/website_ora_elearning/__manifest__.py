# -*- coding: utf-8 -*-
{
    'name': 'ELearning with ORA',
    'description': 'Open Response Assessment',
    'category': 'Website/eLearning',
    'summary': 'Manage and publish an eLearning platform',
    'sequence': 10,
    'version': '1.0',
    'website': 'https://www.manprax.com',
    'author': 'ManpraX Software LLP',
    'depends': ['website_slides', 'diligo_hr'],
    'data': [
        'data/ir_cron_data.xml',
        'security/ir.model.access.csv',
        'views/slide_assessment_view.xml',
        'views/templates.xml',
        'views/slide_fullscreen_view.xml',
        'views/slide_channel_partner_views.xml',
        'views/website_slider_templates.xml',
        'views/web_slider_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_ora_elearning/static/src/scss/website_slides.scss',
            'website_ora_elearning/static/src/js/ora_fullscreen.js',
            'website_ora_elearning/static/src/js/website_ora.js',
        ],
    },
    'qweb': [],
    'images': ["static/description/images/banner.png"],
    'application': True,
    'license': 'AGPL-3',
}
