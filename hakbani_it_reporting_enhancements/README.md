# Hakbani IT Reporting Enhancements — Odoo 17
Author: Bahaa Adel
Version: 17.0.1.0.2

## Sales Analysis Pivot
- Adds **Sales Team** (`team_id`, native Odoo 17 sale.report) and **Sales Leader** (`team_leader_id`) as grouping dimensions in the Pivot view.
- Adds both fields to search and explicit Group By options.
- Sales Leader reads the `user_id` of the sales team assigned to the sales order. Orders without assigned team/manager will appear under Undefined.
- In a Pivot, Measures are numeric aggregations such as Untaxed Total. Many2one fields like Sales Team and Sales Leader must be used as rows/columns (Group By), not Measures. This is an Odoo framework limitation.
- Existing partner-ledger Excel export and invoice Team Leader grouping remain included.

## Upgrade
Replace previous `hakbani_it_reporting_enhancements` directory and **Upgrade** the module in Apps on a staging Odoo 17 database; refreshing browser is not sufficient. No removal of existing module is necessary.

## Testing
Syntax/XML/packaging only; actual Odoo.sh install/upgrade and custom view compatibility must be validated on staging.
