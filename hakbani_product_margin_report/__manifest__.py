# -*- coding: utf-8 -*-
{
    'name': 'Hakbani-IT Product margin report',
    'version': '1.0.0',
    'category': 'Hidden',
    'author': 'hakbani-it',
    'website': '',
    'depends': [
        'sale',
        'report_xlsx',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/product_margin_report.xml',
        'report/product_margin_report.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
