# Hakbani IT Reporting Enhancements — Odoo 17
Author: Bahaa Adel
Version: 17.0.1.0.3

## Sales Analysis
Sales Team (`team_id`) and Sales Leader (`team_leader_id`) appear as pivot grouping dimensions. Default pivot layout adds Sales Leader as a row and Sales Team as a column. The search panel also has a dedicated **Team & Leader Group By** section.

### Why not in Measures?
Measures in Odoo pivots are numeric fields. Sales Team / Sales Leader are Many2one categories. To calculate total sales by leader or team, use Group By and select Untaxed Total measure.

If the screenshot already shows different sales-team names in the column headers, Sales Team grouping is working. For Sales Leader, ensure each Sales Team has a Team Leader set in CRM > Configuration > Sales Teams (the team `user_id` manager); orders without a leader group under Undefined.

**Note:** Existing saved favourite filters and custom pivot preferences can override the default pivot layout. Remove active groupings from the search bar and group by Sales Leader, then Sales Team. Upgrade Apps module after deploying, and hard-refresh the tab.

### Export / Invoices
Partner Ledger XLSX export and invoice Team Leader grouping remain in the module.

### Deployment
Replace directory `hakbani_it_reporting_enhancements`; upgrade from Apps; do not uninstall. Tested statically only (XML, Python, ZIP), not on user's Odoo.sh instance.
