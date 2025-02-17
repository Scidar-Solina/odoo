# -*- coding: utf-8 -*-
{
    'name': "HR Performance Appraisal",
    'version': '1.0',
    'summary': "Employee Performance Review & Appraisal System",
    'sequence': 10,
    'author': "Your Company",
    'website': "https://scidar.org",
    'category': 'Human Resources',
    'depends': ['base', 'hr', 'mail', 'calendar'],
    'data': [
        'security/hr_performance_security.xml',  # Load groups FIRST
        'views/hr_performance_views.xml',  # Load models BEFORE security rules
        'views/hr_performance_rating_views.xml',
        'views/hr_performance_note_views.xml',
        'views/hr_performance_goal_views.xml',
        'views/request_appraisal_views.xml',
        'views/performance_review_template.xml',
        'views/hr_performance_problem.xml',
        'views/hr_performance_comms_view.xml',
        'views/hr_performance_computer_view.xml', 
        'views/hr_performance_product_view.xml',
        'views/hr_performance_firm_view.xml',
        'views/hr_performance_profession_view.xml',
        'security/ir.model.access.csv',  # Load AFTER models are registered
        'data/appraisal_mail_templates.xml',
        'data/appraisal_cron_jobs.xml',
        'data/hr_performance_competency_data.xml',

        
    ],
    'demo': [ ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'OEEL-1',
}
