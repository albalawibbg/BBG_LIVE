{
    'name': 'Hakbani-IT Stock Aging Report for Warehouse',
    'summary': 'Inventory and Stock Aging Report for Warehouse',
    'version': '17.0.0.0',
    'category': 'Warehouse',
    "author": "Hakbani IT",
    'website': 'https://www.nutechits.com',
    "license": "AGPL-3",
    'depends': ['base', 'sale_management', 'purchase', 'stock'],
    'data': [
            'security/ir.model.access.csv',
            'wizard/stock_aging_report_view.xml',
            'report/stock_aging_report.xml',
            'report/stock_aging_report_template.xml',
            ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
