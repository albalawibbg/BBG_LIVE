# -*- coding: utf-8 -*-
{
    'name': 'Sales Custom',
    'version': '1.0.0',
    'category': 'Sales',
    'author': 'Hakbani IT',
    'website': 'https://www.nutechits.com',
    'depends': [
        'sale_management','base','sale','sales_team'
    ],
    'data': [
        'security/security.xml',
        'views/partner.xml',
        'views/users.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
