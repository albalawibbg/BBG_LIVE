# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Access Cost price & Update Qty',
    'version': '15.0',
    'category': 'Sale',
    'description': """Access Cost price & Update Qty""",
    'depends': ['stock_account','stock','product'],
    'data': ['views/cost_price_views.xml'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
