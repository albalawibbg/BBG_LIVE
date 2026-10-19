# Hakbani IT Sales Read Only & Collections — Odoo 17

Author: Bahaa Adel

## Configuration

1. Install module on **Staging**.
2. Open Settings → Users & Companies → Users → target sales manager.
3. Set Sales access to **User: All Documents** (or Administrator, which implies it).
4. In **Hakbani Sales Access**, check **Sales Orders Read Only**.
5. Re-login as that sales manager, open Quotations and Sales Orders.

Only users with BOTH the Sales All Documents group and the custom checkbox are blocked from creating, editing, deleting, confirming sales orders and modifying their lines. Others retain existing rights. Server-side checks enforce this even when writing through RPC. Views also hide normal create/edit actions. This is not a replacement for all model permissions: unrelated apps, server actions under sudo, accounting actions, and custom workflows must be separately audited.

## Collections

Read-only columns in quotation / sale order list and totals near the total in the order form:

- **Invoiced**: posted customer invoices and refunds linked through sale order lines.
- **Collected**: corresponding posted invoice totals less remaining residual (includes reconciled credits; not proof of cash received).
- **Outstanding**: invoice residual still outstanding (refunds reduce the figures).

Invoices associated with multiple sales orders are allocated by the proportion of untaxed invoice lines linked to each order. Amounts convert to the order currency using the invoice date. Uninvoiced quotations show zero collected. Advance payments not yet reconciled to a related invoice are **not** included. Payment allocations can differ from accounting's exact settlement attribution if invoices are shared among sales orders or other non-sales-originated lines; validate examples with accounting before relying on these as official cash collection reporting.

## Notes

- Requires `sale_management`, `account`.
- The checkbox is opt-in to prevent unintentionally locking all sales administrators.
- Odoo.sh deployment must be via Git and normal module install/upgrade; do not edit files in the ephemeral staging shell.
