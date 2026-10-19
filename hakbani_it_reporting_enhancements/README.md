# Hakbani IT Reporting Enhancements — Odoo 17
Author: Bahaa Adel  
Version: 17.0.1.0.4

## Sales Analysis Measures
- **Sales Team Sales Amount**: untaxed sales amount for orders linked to a Sales Team.
- **Sales Leader Sales Amount**: untaxed sales amount for orders whose Sales Team has a configured leader (`crm.team.user_id`).
- Both amounts follow Odoo 17 sale.report currency conversion and are real summable numerical measures. They are not counts of teams or leaders and do not show their names inside the measures list.
- These are alternative slices of the same underlying sales; **do not add both together** or it will double-count sales. For complete overall total, use standard **Untaxed Total**. If no manager is assigned to a team, Sales Leader Sales Amount is zero for that team's orders until a manager is configured.
- Sales Team and Sales Leader names remain pivot dimensions (rows, columns, Group By). Your existing saved pivot favourites can override default layout.

## Other features
- Partner Ledger XLSX export.
- Invoice Group By Team Leader.

## Install / Upgrade
Copy directory `hakbani_it_reporting_enhancements` into custom addons, restart/rebuild Odoo.sh, and Upgrade module from Apps (do not uninstall). Then hard refresh Sales Analysis Pivot and select two new entries under Measures. Validate totals on Staging before Production.

Tested static Python/XML/ZIP. Not tested with user's runtime database.
