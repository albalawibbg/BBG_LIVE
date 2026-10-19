# Hakbani IT Actual Manufacturing Cost (Odoo 17)

Author: Bahaa Adel

## What it does
- Enhances Odoo 17's existing `mrp_account._cal_price` allocation before inventory posting.
- Calculates actual input material costs from available stock valuation layers, falling back to Odoo move values.
- Includes operations/work order costs and Odoo's `extra_cost` per produced unit.
- Applies BOM by-product cost shares and supports multiple finished moves.
- Retains Odoo 17's stock valuation layer creation and journal posting mechanisms; does not create second entries.
- Adds a **Actual Cost Audit** tab to Manufacturing Orders with material, operation, extra, finished and by-product valuations, cost difference and navigation to valuations/account moves.

## Important accounting safeguards
- FIFO and AVCO (`average`) finished products may use actual calculated costs.
- Standard-cost finished products retain Odoo's standard-price valuation (differences are shown for review).
- Only new / unposted manufacturing completion is affected. Historic entries are **not** silently edited.
- A posted production's audit difference is a diagnostic, **not** authority to automatically adjust the general ledger.
- The module does not automatically adjust lot valuation inconsistencies in Odoo core if Odoo did not create distinct accurate layer values.
- Where processing byproduct cost shares, material costs, work orders or valuation differ from company accounting setup, manually investigate before relying on the financials.

## Installation
1. Back up the database and filestore; use staging first.
2. Extract the root directory into an Odoo 17 addons path.
3. Restart Odoo, update Apps List, install "Hakbani IT - Actual Manufacturing Cost".
4. Enable automated inventory valuation in accounting configurations for products intended to generate stock journal entries.
5. Set costing to AVCO or FIFO on the finished product category if actual capitalization is required.
6. Configure work centers and log actual operations where relevant.
7. Validate a small test MO; check Actual Cost Audit, valuation layers and journal entries.

## Test case
- Consume 2 component units valued at 30 and 40; record operation cost 20; extra unit cost 5 and produce 2 units.
- Total = 30 + 40 + 20 + (5 × 2) = 100; finished unit cost = 50 if no by-products.
- With a 10% by-product cost share, finish main output at 90 total and by-product at 10 total.

Note: This package is statically validated; live Odoo integration testing is still required on the exact target build and accounting configuration.
