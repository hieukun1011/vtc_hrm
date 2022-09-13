# -*- coding: utf-8 -*-

{
    'name': 'Diligo Maintenance',
    'version': '1.0',
    'sequence': 125,
    'author': 'Chí Nguyễn',
    'company': 'Diligo Holdings',
    'website': "diligo.vn",
    'depends': ['mail', 'hr', 'diligo_device', 'odoo_email_cc_bcc'],
    'data': [
        'security/maintenance.xml',
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'data/mail_template_data.xml',
        'wizard/applicant_refuse_reason_views.xml',
        'wizard/change_person_in_charge.xml',
        'views/maintenance_views.xml',
        'views/maintenance_preventive_views.xml',
        'views/device_main_views.xml',
        'views/equipment_export_view.xml',
        'views/hr_employee_view.xml',
        'views/website_support_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'diligo_maintenance/static/src/js/countdown_time.js',
        ]},
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
