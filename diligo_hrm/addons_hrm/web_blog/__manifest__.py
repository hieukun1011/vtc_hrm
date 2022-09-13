{
    'name': 'Blog Website',
    'version': '1.0',
    'category': 'Uncategorized',
    'summary': '',
    'author': 'Longlh',
    'company': '',
    'website': "",
    'depends': ['base_setup'],
    'data': [
        'security/blog_website_security.xml',
        'security/ir.model.access.csv',
        # 'views/template_blog_theme.xml',
        'views/web_blog_tag.xml',
        'views/web_blog.xml',
        'views/web_blog_meta.xml',
        'views/res_config_settings_views.xml',

    ],
    'assets': {
        'web.assets_frontend': [
        ],
    },
    'qweb': [

    ],
    'installable': True,
    'application': True,
}
###################################################################################
