# -*-coding: utf-8 -*-
{
    "name": "Hakbani-IT Invoice Report",
    "summary": "Hakbani-IT Invoice Report",
    "version": "17.0.0.0",
    "category": "account",
    "author": "Hakbani IT",
    'website': 'https://www.nutechits.com',
    "license": "AGPL-3",
    "depends": ["account", "l10n_sa", "hakbani_customer_invoice"],
    "data": [
        "reports/invoice_report.xml",
        "reports/records.xml",
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
