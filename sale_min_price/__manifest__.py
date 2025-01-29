# -*- coding: utf-8 -*-
{
    'name': 'Sales Auto Internal Transfer',
    'version': '1.0.0',
    'category': 'Hidden',
    'author': 'Mohamed Lamine Lalmi',
    'website': 'www.fiverr.com/mohamedlaminela',
    'depends': [
        'hr',
        'sale_management',
    ],
    'data': [
        'security/security.xml',
        'views/product_views.xml',
        'views/sale_order_views.xml',
        'views/account_payment_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
