# -*- coding: utf-8 -*-
{
    'name': 'Hakbani Batch Payslip Report',
    'version': '17.0.0.0',
    'category': 'hr',
    "author": "Hakbani IT",
    'website': 'https://www.nutechits.com',
    'depends': [
        'hr',
        'hr_payroll',
        'report_xlsx',
    ],
    'data': [
        # 'report/hr_payslip_run_template.xml',
        'report/record.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
