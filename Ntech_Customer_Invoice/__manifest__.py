# -*- coding: utf-8 -*-

{
    'name': 'Ntech_Customer_Invoice',
    'version': '17.0',
    'category': 'Invoice',
    'description': """Ntech_Customer_Invoice""",
    'depends': [
        'account'
    ],
    'data': [
        'security/security.xml',
        'views/account_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
