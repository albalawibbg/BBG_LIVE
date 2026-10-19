{
    'name': 'Hakbani IT - Partner Excel and Sales Team Reporting',
    'version': '17.0.1.0.0',
    'summary': 'Partner ledger XLSX, sales manager analysis and invoice team leader grouping',
    'author': 'Bahaa Adel',
    'license': 'LGPL-3',
    'category': 'Accounting/Reporting',
    'depends': ['account', 'sale_management', 'sales_team'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/partner_ledger_export_views.xml',
        'views/partner_ledger_action.xml',
        'views/sales_analysis_views.xml',
        'views/invoice_group_views.xml',
    ],
    'installable': True,
    'application': False,
}
