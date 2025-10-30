# -*- coding: utf-8 -*-
{
    'name': "Purchase Order Approve",
    'summary': """""",
    'author': "AWD Soltan",
    'category': 'Purchase',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['purchase','account'],
    # always loaded
    'data': [
        'security/security_group.xml',
        'views/purchase_order_inh_view.xml',
        'views/invoice.xml',
    ],
}
