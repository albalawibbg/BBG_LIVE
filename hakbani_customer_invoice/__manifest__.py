# -*- coding: utf-8 -*-

{
    'name': 'Hakbani-IT Customer Invoice',
    'version': '17.0.0.0',
    'category': 'Invoice',
    'description': """Hakbani-IT Customer Invoice""",
    'depends': [
        'account'
    ],
    'data': [
        'security/security.xml',
        'views/account_move.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
