{
    'name': 'Hakbani - Partner access restrictions',
    'version': '1.0',
    'summary': 'Hakbani Module for access restrictions on Partner',
    'author': 'Hakbani IT',
    'depends': [
        'base',
        'account',
        'account_followup',
        'purchase',
        'account_reports',
        'sale',
    ],
    'data': [
        'security/security.xml',
        'views/partner.xml'
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
