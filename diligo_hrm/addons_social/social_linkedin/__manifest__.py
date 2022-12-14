# -*- coding: utf-8 -*-
{
    'name': 'Social LinkedIn',
    'summary': 'Manage your LinkedIn accounts and schedule posts',
    'description': 'Manage your LinkedIn accounts and schedule posts',
    'category': 'Marketing/Social Marketing',
    'version': '0.1',
    'depends': ['social', 'iap'],
    'data': [
        'data/social_media_data.xml',
        # 'views/assets.xml',
        'views/social_post_views.xml',
        'views/social_linkedin_preview.xml',
        'views/social_stream_posts_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            '/social_linkedin/static/src/js/social_post_formatter_mixin.js',
            '/social_linkedin/static/src/js/stream_post_kanban_controller.js',
            '/social_linkedin/static/src/js/stream_post_linkedin_comments.js',
            '/social_linkedin/static/src/scss/social_linkedin.scss',
        ],
    },
    'qweb': [
        "static/src/xml/social_linkedin_templates.xml",
    ],
    'auto_install': True,
}
