
{
    'name': 'DILIGO Fontend',
    'version': '1.0',
    'category': 'Human Resources',
    'sequence': 1,
    'summary': 'Centralize employee information',
    'author': 'Chí Nguyễn',
    'company': '',
    'website': "",
    'depends': [
        # 'website',
        #         'diligo_hr',
                ],
    'data': [
        # 'views/homepage_template.xml',
        # 'views/apply_distributors_template_view.xml',
        # 'views/hr_job_inherit_view.xml',
        # 'views/sources_view.xml',

    ],
    'assets': {
        'web.assets_frontend': [
            'diligo_fontend/static/src/css/app.css',
            'diligo_fontend/static/src/css/app.css.map',
            'diligo_fontend/static/src/js/app.js',
            # 'diligo_fontend/static/src/js/confetti.js',
            # 'diligo_fontend/static/src/js/main.js',
            # 'diligo_fontend/static/src/js/quiz.js',
            # 'diligo_fontend/static/src/js/responsive.js',
            # 'diligo_fontend/static/src/js/results.js',
            # 'diligo_fontend/static/src/css/courses.css',
            # 'diligo_fontend/static/src/css/courses-res.css',
            'web/static/lib/bootstrap/css/bootstrap.css',
        ],
    },
    'qweb': [
        'static/src/xml/view.xml'
    ],
    'demo': [],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
###################################################################################
