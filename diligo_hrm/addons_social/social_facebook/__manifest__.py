# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Social Facebook',
    'category': 'Marketing/Social Marketing',
    'summary': 'Manage your Facebook pages and schedule posts',
    'version': '1.0',
    'description': """Manage your Facebook pages and schedule posts""",
    'depends': ['social'],
    'data': [
        'data/social_media_data.xml',
        # 'views/assets.xml',
        'views/social_facebook_templates.xml',
        'views/social_post_views.xml',
        'views/social_stream_post_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            '/social_facebook/static/src/js/social_post_formatter_mixin.js',
            '/social_facebook/static/src/scss/social_facebook.scss',
            '/social_facebook/static/src/js/stream_post_facebook_comments.js',
            '/social_facebook/static/src/js/stream_post_kanban_controller.js',
        ],
        'web.qunit_suite_tests': [
            '/social_facebook/static/src/js/tests/social_facebook_test_comments.test.js',
        ],
    },
    'qweb': [
        "static/src/xml/social_facebook_templates.xml",
    ],
    'auto_install': True,
}
