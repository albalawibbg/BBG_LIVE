# -*-coding: utf-8 -*-
{
    "name": "Sale Margin Access",
    "summary": "Sale Margin Access",
    "version": "17.0.0.0",
    "category": "Sale",

    "license": "AGPL-3",
    "depends": ["sale_management", "sale_stock_margin","sale_margin"],
    "data": [
        'security/security.xml',
        'views/sale_management.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
