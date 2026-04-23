# -*-coding: utf-8 -*-
{
    "name": "Hakbani-IT Kit Product",
    "summary": "Hakbani-IT Kit Product",
    "version": "17.0.0.0",
    "category": "Sale",
    "author": "Hakbani IT",
    'website': 'https://www.nutechits.com',
    "license": "AGPL-3",
    "depends": ["product", "sale"],
    "data": [
        'security/ir.model.access.csv',
        # 'views/mrp_bom.xml',
        'views/sale_order.xml',
        # 'views/product_template.xml',
        'views/warehouse_product_wizard.xml',
    ],
    'installable': True,
    'application': True,
}
