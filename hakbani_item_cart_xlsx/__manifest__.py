{
    'name': "Hakbani-IT Item Cart Report",
    'category': 'stock',
    'summary': "Manage properties, tenant and tenancies",
    'version': '1.0',
    'author': 'Hakbani-IT',
    'depends': [
        'report_xlsx',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'report/report.xml',
        'wizard/inventory_valuation.xml',
    ],

    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
