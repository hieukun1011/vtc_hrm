
{
    'name': 'DILIGO HRMS',
    'version': '1.0',
    'category': 'Human Resources',
    'sequence': 1,
    'summary': 'Centralize employee information',
    'author': 'Chí Nguyễn',
    'company': '',
    'website': "",
    'depends': ['hr',
                'hr_recruitment',
                'hr_contract',
                # 'website_hr_recruitment',
                'ohrms_core',
                'hr_disciplinary_tracking',
                'sh_message',
                'mail',
                'web_monetary_format',
                'base_unit_vn'],
    'data': [
        'data/hr_data.xml',
        'data/hr_job_data.xml',
        'data/mail_data.xml',
        'security/ir.model.access.csv',
        'security/group.xml',
        # 'views/assets_custom_css.xml',
        'views/hr_applicant_views.xml',
        'views/hr_job_views.xml',
        # 'views/website_hr_recruitment_templates_new.xml',
        'views/hr_employee_views.xml',
        'views/hr_department_views.xml',
        'views/applicant_refuse_reason_views.xml',
        'views/template_attachment.xml',
        'wizard/report_job_view.xml',
        'wizard/report_recruitment.xml',


    ],
    'assets': {
            'web.assets_frontend': [
                'diligo_hr/static/src/css/website_hr_recruitment.css',
                'diligo_hr/static/src/css/app.css',
                # 'diligo_hr/static/src/js/app.js',
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
