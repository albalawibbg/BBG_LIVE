# -*- coding: utf-8 -*-
{
    'name': "Hakbani It Holding Item Report",
    'summary': """
    Hakbani It Holding Item Report
    """,
    "author": "Hakbani IT",
    'website': 'https://www.nutechits.com',
    'category': 'stock',
    'version': '17.0.0.0',
    'depends': ['base', 'report_xlsx', 'stock', 'sale_management', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'report/report.xml',
        'wizard/sale_purchase_register.xml',
    ],
}