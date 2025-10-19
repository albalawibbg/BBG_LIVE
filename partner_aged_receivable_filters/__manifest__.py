{
    'name': 'Partner Aged Receivable Filters',
    'version': '17.0',
    'summary': '',
    'description': '',
    'category': '',
    'website': '',
    'depends': ['base', 'account_reports', 'account','mail','hr',"sale_custom"],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/payment.xml',
        'data/account_reports.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'partner_aged_receivable_filters/static/src/components/**/*',
        ],
    },
    'installable': True,
    'auto_install': False,
}
