# Hakbani IT - Reporting Enhancements (Odoo 17)

Author: Bahaa Adel
Technical module: `hakbani_it_reporting_enhancements`
Version: 17.0.1.0.1

## Features
- Action menu on customer/vendor record and Journal Items: Export Partner Ledger (Excel).
- XLSX wizard: partner, date range, posted only, receivable/payable only, include child contacts. Exports all matching ledger entries, not just current pagination.
- Sales > Reporting > Sales Analysis: filter and group by Sales Manager / Team Leader using the sales team's leader.
- Accounting > Customers > Invoices: Group By Team Leader (sales team leader associated with invoice's originating order, or invoice's own team/salesperson).

## Install
Unzip into custom addons, restart Odoo, Update Apps List, install the module. Depends on account, sale_management, sales_team. Test in staging first.

## Notes
- Invoice team leaders are computed/stored. If team leadership changes, pre-existing invoices may need recomputation.
- Running balance in Excel begins at zero for the exported range; it is **not** an opening-balance-adjusted ledger.
- The customer export is a custom journal-item worksheet, not a direct export of the Enterprise dynamic account report PDF.
- Untested on your particular Odoo 17 database; custom CRM team fields and views may need adapting.

## Fix 17.0.1.0.1
- Fixed invalid Odoo domain (`in` passed an integer instead of a list).
- Batch resolve CRM team memberships using `crm.team.member` rather than per-invoice lookups.
- Use the invoice sales team and sales order team as primary sources.
