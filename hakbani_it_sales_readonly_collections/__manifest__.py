{
    'name': 'Hakbani IT Sales Read Only & Collections',
    'summary': 'Controlled read-only sales documents and invoice-based collections',
    'version': '17.0.1.0.0',
    'category': 'Sales/Sales',
    'author': 'Bahaa Adel',
    'license': 'LGPL-3',
    'depends': ['sale_management', 'account'],
    'data': [
        'views/res_users_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
}
