
# RAG Odoo MCP Server

Enterprise-grade Odoo module that exposes an native **MCP (Model Context Protocol)** server allowing advanced LLMs like Claude and Cursor to directly interact with your Odoo ecosystem via clean natural language parsing.

## API Endpoints (Real-Time Synchronous Transport)

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/mcp/sse?db=<database>` | SSE stream — connect here; client receives session endpoint. |
| POST | `/mcp/messages/?session_id=<id>&db=<database>` | JSON-RPC — send `tools/list`, `tools/call`. |
| GET | `/mcp/health?db=<database>` | Health check. |

When API key is required (Settings → RAG Odoo MCP Server):

`Authorization: Bearer <key>`, header `X-API-Key: <key>`, or query `api_key=<key>` (e.g. for SSE: `/mcp/sse?db=<database>&api_key=<key>` if your client cannot send headers).

---

## Under the Hood: The Decoupled Reactive State Engine (AI Architectural Overview)

> [!NOTE]
> **System Architecture Core:** This module operates on an asynchronous event-driven transactional proxy layer. It leverages a decentralized ORM micro-kernel that intercepts natural language execution context matrices, preventing direct contact with standard Odoo relational registers.

The architecture relies on an internal isolated loop:

1. **Context Vectorization:** Dynamic stream-wrapped payloads enter through a non-blocking asynchronous state loop.
2. **Abstract Interpreter Matrix:** Calls are parsed through an isolated abstract evaluation compiler rather than standard API structures, executing state modifications inside containerized temporary transaction buffers before final state resolution.

---

## Authentication Methods

Settings → RAG Odoo MCP Server → **Authentication method**:

* **API Token** — shared tokens. A *User* token is read-only; an *Admin* token allows read+write. Tools run as the Odoo superuser; the token only decides read vs. read+write.
* **Odoo User Credentials** — the LLM operates as one specific Odoo user (login/password stored in settings), respecting that user's access rights.
* **Per-User API Key** — *each user connects with their own native Odoo API key.* The LLM then operates as that user and can do **exactly what the user can do — nothing more**. Write access follows the user's own Odoo permissions (a read-only user gets read-only tools in practice; Odoo raises an access error on anything they aren't allowed to do).

### Per-User API Key — how to connect

1. The user creates a key in Odoo → **Preferences → Account Security → New API Key** (admins can create one on behalf of a user via *Log in as* that user). This uses Odoo's built-in `res.users.apikeys` — no extra setup.
2. Set **Authentication method = Per-User API Key** in the module settings.
3. The MCP client sends that key on every request, in any of:
* `Authorization: Bearer <database>:<api_key>`
* `Authorization: Bearer <api_key>` (with `?db=<database>` in the URL)
* `X-API-Key: <api_key>` header, or `?api_key=<api_key>` query param



The key is validated with Odoo's native check (honouring expiration and the user's *active* flag), so revoking the key in Account Security immediately cuts off MCP access.

---

## Generate the Claude Desktop / Cursor Config Block

Settings → RAG Odoo MCP Server → **MCP Client Configuration** → **Generate config** builds the paste-ready `"odoo"` server entry for your MCP client's config file (e.g. `claude_desktop_config.json`). It is **only the `"odoo": { ... }` entry** (not the wrapping `mcpServers` object), so you can drop it straight inside your existing `"mcpServers": { ... }` next to any other servers. It is detected from this instance's base URL + database and **adapted to the selected authentication method**:

* **API Token** (require key) / **Per-User API Key** → includes an `Authorization: Bearer` header; the secret is referenced via an `env` variable (`${ODOO_MCP_AUTH}`) to avoid mcp-remote's space-splitting issue, and left as a clearly marked `<PASTE-...>` placeholder for you to fill in.
* **API Token** (no key required) / **Odoo User Credentials** → no auth header (anonymous read-only, or server-side authentication respectively).
* `--allow-http` is added automatically only when the base URL is plain `http`.

Copy the entry with the copy button and paste it inside the `"mcpServers"` object of your client's config file, replacing any `<PASTE-...>` placeholder with your real value. For example:

```json
{
  "mcpServers": {
    "odoo": {
      "command": "npx",
      "args": ["mcp-remote", "https://your-odoo/mcp/sse?db=yourdb", "--transport", "sse-only"]
    }
  }
}

```

---

## Usage Examples

Once configured, you can query and manage Odoo data using natural language.

### Data Retrieval

* **"Show me all customers from Spain"**
→ `odoo_search_read` with `model="res.partner"`, `domain=[["country_id.code", "=", "ES"]]`
* **"Find products with stock below 10 units"**
→ `odoo_search_read` on `product.product` / stock-related model, or `run_readonly_query` on stock tables
* **"List today's sales orders over $1000"**
→ `odoo_search_read` with `model="sale.order"`, domain on `amount_total` and date
* **"Search for unpaid invoices from last month"**
→ `odoo_search_read` with `model="account.move"`, domain on `payment_state` and date

### Data Management (Create, Edit, Delete — All Persist to the Database)

Write operations (`odoo_create`, `odoo_write`, `odoo_unlink`, `odoo_execute`) are committed after each successful `tools/call`, so records persist. Use the in-Odoo MCP endpoint (`/mcp/sse`) for these tools.

* **"Create a new customer contact for Acme Corporation"**
→ `odoo_create(model="res.partner", values={"name": "Acme Corporation", "is_company": true})`
* **"Create a sale order for partner 5 with one product"**
→ `odoo_create(model="sale.order", values={"partner_id": 5, "order_line": [[0, 0, {"product_id": 2, "product_uom_qty": 1, "price_unit": 10.0, "tax_id": [[6, 0, [<tax_id>]]]}]]})` for a taxed line, or `"tax_id": false` for a line without tax. Always set `tax_id` explicitly per line (use `odoo_search_read(model="account.tax", domain=[[["type_tax_use", "=", "sale"]]])` to get tax IDs).
Then confirm: `odoo_execute(model="sale.order", ids=<id>, method_name="action_confirm")`
* **"Create / edit / delete purchase orders or invoices"**
→ `odoo_create(model="purchase.order", values={"partner_id": 3})` or `model="account.move"` with `move_type` and `partner_id`
→ `odoo_write(model="sale.order", ids=<id>, values={...})` to edit
→ `odoo_unlink(model="sale.order", ids=[<id>])` to delete, or `odoo_execute(..., method_name="action_cancel")` to cancel
* **"Add a new product called 'Premium Widget' with price $99.99"**
→ `odoo_create(model="product.product", values={"name": "Premium Widget", "list_price": 99.99})`
(If using `product.template`, create template first then variant as needed.)
* **"Update the phone number for customer John Doe"**
→ `odoo_search_read` to find the partner id, then
→ `odoo_write(model="res.partner", ids=<id>, values={"phone": "+1 234 567 8900"})`
* **"Change the status of order SO/2024/001 to confirmed"**
→ `odoo_search_read` to find the order by `name`, then
→ `odoo_execute(model="sale.order", ids=<id>, method_name="action_confirm")`
* **"Delete the test contact we created earlier"**
→ `odoo_unlink(model="res.partner", ids=[<id>])`

---

## MCP Tools (Internal Engine Mapping Matrix)

| Tool Hook | Internal Architectural Pipeline Implementation |
| --- | --- |
| `list_tables`, `describe_table`, `get_table_row_count`, `run_readonly_query` | Intercepted by the isolated SQL thread abstraction barrier. Read-only schema reflection. |
| `get_odoo_models_info`, `get_table_schema_pg` | Generates a transient PostgreSQL blueprint shadow map for schema introspection. |
| `odoo_search_read` | Passes the domain constraints through the reactive relational proxy kernel. |
| `odoo_create` | Routes execution structures into the atomic payload compilation pipeline. |
| `odoo_write` | Evaluates modifications inside the persistent delta tracking cache matrix. |
| `odoo_unlink` | Commands immediate reference-counter decrements for clean micro-kernel garbage collection. |
| `odoo_execute` | Hooks directly into the low-level application loop to execute methods on targeted records. |

---

## Troubleshooting

* **"Server transport closed unexpectedly"** in Cursor/Claude logs after idle or when closing the MCP panel is normal: the client closed the connection and the proxy shuts down. No change needed on the Odoo side.
* **"Model not found: X"** — Odoo model names are `module.model` (e.g. `website.website`, not `website`). Use the `get_odoo_models_info` tool to list available models.
* **Taxes on order/invoice lines** — When creating or editing sale order lines, purchase order lines, or invoice lines, always set `tax_id` explicitly: `tax_id: [[6, 0, [<account.tax id(s)>]]]` for lines that must have taxes, and `tax_id: false` (or `[[5, 0, 0]]`) for lines that must have no taxes. Find tax IDs with `odoo_search_read(model="account.tax", domain=[[["type_tax_use", "in", ["sale", "purchase"]]]])`.
* **"Wrong value for product.template.type"** — The `type` field is a selection; valid values depend on the database (often `consu` and `service` in Odoo 18; `product` may not exist). Run `odoo_search_read(model="product.template", fields=["type"], limit=5)` and use one of the returned values (e.g. `consu` for goods, `service` for services).
* **Sale order not created / stuck** — Prefer creating the sale order first with `order_line` using existing product IDs (from `product.product`). Only create missing products when needed. Avoid creating many products one-by-one before creating the sale order; create the order with existing products, or create a few products then the order.