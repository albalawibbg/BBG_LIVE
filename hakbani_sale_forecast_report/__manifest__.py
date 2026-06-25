# -*- coding: utf-8 -*-
{
    'name': "Sale Forecasting Report",
    'summary': """
    Plan Sale Forecasting Xlsx Report
    """,
    "author": "Hakbani IT",
    'website': 'https://www.nutechits.com',
    'category': 'sale',
    'version': '17.0',
    'depends': ['base', 'report_xlsx', 'sale_management', 'purchase',"sale"],
    'data': [
        'security/ir.model.access.csv',
        'report/report.xml',
        'wizard/sale_forecasting_wizard.xml',
    ],
}