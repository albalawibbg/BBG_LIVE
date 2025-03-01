# -*-coding: utf-8 -*-
{
    "name": "Hakbani-IT Loan Enhancement",
    "summary": "Hakbani-IT Loan Enhancement",
    "version": "17.0",
    "category": "Hr",
    "author": "Hakbani IT",
    'website': 'https://www.nutechits.com',
    "license": "AGPL-3",
    "depends": ["ohrms_loan_accounting", "ohrms_loan"],
    "data": [
        'security/ir.model.access.csv',
        'security/security.xml',
        'wizard/pay_loan_wizard.xml',
        'views/loan.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
