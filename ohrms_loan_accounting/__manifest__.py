# -*- coding: utf-8 -*-
{
    'name': ' Loan Management',
    'version': '17.0',
    'summary': 'Manage Loan Requests',
    'description': """
        Helps you to manage Loan Requests of your company's staff.
        """,
    'category': 'Generic Modules/Human Resources',
    'author': "Hakbani IT",
    'website': "https://www.nutechits.com",
    'depends': [
        'base', 'hr_payroll', 'hr', 'account', 'ohrms_loan',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/hr_loan_config.xml',
        'views/hr_loan_acc.xml',
    ],
    'demo': [],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
