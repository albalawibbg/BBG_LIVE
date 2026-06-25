# -*- coding: utf-8 -*-

{
    'name': "Account Journal Restrictions",
    'summary': """Restrict users to certain account journals""",
    'description': """Restrict users to certain account journals.""",
    'author': "Hakbani-IT",
    'website': "",
    'category': 'account',
    'version': '1.0.1',
    'depends': [
        'account'
    ],
    'data': [
        'security/security.xml',
        'views/users.xml',
    ],
    "images": [
    ],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
