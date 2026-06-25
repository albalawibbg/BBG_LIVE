# -*- coding: utf-8 -*-

{
    "name": "Stock Disallow Negative",
    "summary": "Disallow negative stock levels by default",
    "version": "17.0.0.0",
    "category": "Inventory, Logistic, Storage",
    'author': 'Hakbani IT',
    'website': 'https://www.nutechits.com',
    "license": "AGPL-3",
    "depends": ["stock",'product'],
    "data": [
        "views/product_product_views.xml",
        "views/stock_location_views.xml"
    ],
    "installable": True,
}
