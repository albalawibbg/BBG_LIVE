# -*- coding: utf-8 -*-

import json
import logging
import secrets
from urllib.parse import urlparse

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# YouTube tutorial explaining how to find & edit the MCP client config file
MCP_CONFIG_TUTORIAL_URL = 'https://www.youtube.com/watch?v=AzKtHMH1FsM'


MCP_API_KEY_PARAM = 'rag_odoo_mcp_server.api_key'  # legacy, unused
MCP_API_KEY_USER_PARAM = 'rag_odoo_mcp_server.api_key_user'
MCP_API_KEY_ADMIN_PARAM = 'rag_odoo_mcp_server.api_key_admin'
MCP_REQUIRE_API_KEY_PARAM = 'rag_odoo_mcp_server.require_api_key'
MCP_AUTH_METHOD_PARAM = 'rag_odoo_mcp_server.auth_method'
MCP_ODOO_USER_LOGIN_PARAM = 'rag_odoo_mcp_server.odoo_user_login'
MCP_ODOO_USER_PASSWORD_PARAM = 'rag_odoo_mcp_server.odoo_user_password'
MCP_ODOO_USER_ALLOW_WRITE_PARAM = 'rag_odoo_mcp_server.odoo_user_allow_write'
MCP_CRM_MANAGER_ENABLED_PARAM = 'rag_odoo_mcp_server.crm_manager_enabled'


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    mcp_endpoint_hint = fields.Char(
        string='MCP endpoint',
        readonly=True,
        default='http://<your-odoo>/mcp/sse?db=<database>',
        help='MCP runs inside Odoo. Use this URL in Cursor/Claude with mcp-remote (--transport sse-only, --allow-http). '
             'Replace <your-odoo> and <database> with your base URL and database name.',
    )

    require_api_key = fields.Boolean(
        string='Require API key for MCP',
        help='If checked, clients must send a valid User or Admin token. If not checked, no token is required (read-only).',
    )

    user_token_set = fields.Boolean(
        string='User token (read-only)',
        readonly=True,
        help='User token: Claude can only search and read data. Give this token to standard users.',
    )

    admin_token_set = fields.Boolean(
        string='Admin token (read+write)',
        readonly=True,
        help='Admin token: Claude can create, edit and delete records. Give only to managers or admins.',
    )

    mcp_auth_method = fields.Selection(
        [
            ('token', 'API Token'),
            ('odoo_user', 'Odoo User Credentials'),
            ('user_api_key', 'Per-User API Key'),
        ],
        string='Authentication Method',
        default='token',
        help='Choose how the LLM authenticates with Odoo.\n'
             '- API Token: use generated shared tokens (read-only User token / read+write Admin token).\n'
             '- Odoo User Credentials: the LLM operates as one specific Odoo user, '
             'respecting that user\'s access rights and permissions.\n'
             '- Per-User API Key: each user connects with their own native Odoo API key '
             '(Preferences → Account Security → New API Key). The LLM then operates as that '
             'user and can do exactly what the user can do — nothing more.',
    )

    mcp_odoo_user_login = fields.Char(
        string='Odoo Username',
        help='The login (email) of the Odoo user the LLM will impersonate.',
    )

    mcp_odoo_user_password = fields.Char(
        string='Odoo Password',
        help='The password of the Odoo user. Stored in system parameters.',
    )

    mcp_odoo_user_allow_write = fields.Boolean(
        string='Allow write operations',
        default=False,
        help='If checked, the LLM can create, edit and delete records when using Odoo User authentication.',
    )

    # Feature flag stored in ir.config_parameter. Saving toggles membership of
    # the rag_odoo_mcp_server.group_crm_manager group on every internal user,
    # which in turn shows/hides the brief menus and CRM/Email-Marketing buttons.
    # The mailing/CRM MCP tools also check this flag and refuse when it's off.
    crm_manager_enabled = fields.Boolean(
        string='CRM Manager',
        help='Enable lead-generation and mailing-campaign "from a brief" features. '
             'When ON: shows the "Claude Lead Brief" button on CRM > Leads, the "Claude brief" '
             'button on Email Marketing > Mailings, the Claude Briefs menus under each app, '
             'and exposes the lead-gen / CRM / mailing MCP tools to Claude. '
             'When OFF: those menus, buttons, and tools are hidden and refused. '
             'Note: CRM and Mass Mailing modules are dependencies of this module and stay '
             'installed in either case.',
    )

    # -------- Generated MCP client configuration block -------------------
    mcp_client_config = fields.Text(
        string='MCP client configuration',
        help='The "odoo" server entry to paste inside the "mcpServers" object of your '
             'Claude Desktop / Cursor MCP client configuration file (e.g. claude_desktop_config.json). '
             'It is built from this Odoo instance\'s URL and database, and adapted to the selected '
             'Authentication method. Any value the server cannot know (such as your API key) is left '
             'as a clearly-marked placeholder for you to fill in. Click "Generate config" to rebuild it.',
    )

    def get_values(self):
        res = super().get_values()
        ICP = self.env['ir.config_parameter'].sudo()
        val = ICP.get_param(MCP_REQUIRE_API_KEY_PARAM)
        res['require_api_key'] = (str(val or '').strip().lower() in ('true', '1', 'yes'))
        user_key = (ICP.get_param(MCP_API_KEY_USER_PARAM) or '').strip()
        admin_key = (ICP.get_param(MCP_API_KEY_ADMIN_PARAM) or '').strip()
        res['user_token_set'] = bool(user_key)
        res['admin_token_set'] = bool(admin_key)
        res['mcp_auth_method'] = ICP.get_param(MCP_AUTH_METHOD_PARAM) or 'token'
        res['mcp_odoo_user_login'] = ICP.get_param(MCP_ODOO_USER_LOGIN_PARAM) or ''
        # Show masked password if set (never expose the real password in the UI)
        stored_pwd = ICP.get_param(MCP_ODOO_USER_PASSWORD_PARAM) or ''
        res['mcp_odoo_user_password'] = '********' if stored_pwd else ''
        allow_write = ICP.get_param(MCP_ODOO_USER_ALLOW_WRITE_PARAM)
        res['mcp_odoo_user_allow_write'] = (str(allow_write or '').strip().lower() in ('true', '1', 'yes'))
        crm_mgr = ICP.get_param(MCP_CRM_MANAGER_ENABLED_PARAM)
        res['crm_manager_enabled'] = (str(crm_mgr or '').strip().lower() in ('true', '1', 'yes'))
        # Auto-populate the paste-ready MCP client config block (adapted to the auth method).
        res['mcp_client_config'] = self._build_mcp_client_config()
        return res

    def set_values(self):
        super().set_values()
        icp = self.env['ir.config_parameter'].sudo()
        icp.set_param(
            MCP_REQUIRE_API_KEY_PARAM, 'True' if self.require_api_key else 'False'
        )
        # Odoo User authentication settings
        icp.set_param(MCP_AUTH_METHOD_PARAM, self.mcp_auth_method or 'token')
        icp.set_param(MCP_ODOO_USER_LOGIN_PARAM, self.mcp_odoo_user_login or '')
        # Only update password if the user actually changed it (not the masked placeholder)
        if self.mcp_odoo_user_password and self.mcp_odoo_user_password != '********':
            icp.set_param(MCP_ODOO_USER_PASSWORD_PARAM, self.mcp_odoo_user_password)
        icp.set_param(
            MCP_ODOO_USER_ALLOW_WRITE_PARAM,
            'True' if self.mcp_odoo_user_allow_write else 'False',
        )
        # CRM Manager: persist the flag and add/remove the security group so brief
        # menus + CRM/Email-Marketing buttons appear/disappear immediately.
        icp.set_param(
            MCP_CRM_MANAGER_ENABLED_PARAM,
            'True' if self.crm_manager_enabled else 'False',
        )
        self._sync_crm_manager_group(self.crm_manager_enabled)

    def _sync_crm_manager_group(self, enabled):
        """Add or remove group_crm_manager on every internal user (skip portal/public)."""
        group = self.env.ref('rag_odoo_mcp_server.group_crm_manager', raise_if_not_found=False)
        if not group:
            _logger.warning('CRM Manager group not found; cannot toggle membership.')
            return
        internal_users = self.env['res.users'].sudo().search([
            ('share', '=', False),
            ('active', 'in', [True, False]),
        ])
        if enabled:
            to_add = internal_users - group.users
            if to_add:
                group.sudo().write({'users': [(4, u.id) for u in to_add]})
        else:
            if group.users:
                group.sudo().write({'users': [(3, u.id) for u in group.users]})

    def action_generate_mcp_api_key_user(self):
        """Generate a read-only (user) API key; show it once in a popup."""
        self.ensure_one()
        new_key = secrets.token_urlsafe(32)
        self.env['ir.config_parameter'].sudo().set_param(MCP_API_KEY_USER_PARAM, new_key)
        return {
            'type': 'ir.actions.act_window',
            'name': 'User token (read-only) — copy and store securely',
            'res_model': 'rag_odoo_mcp_server.generate_api_key_wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_api_key_display': new_key,
                'default_token_type': 'User (read-only)',
            },
        }

    def action_generate_mcp_api_key_admin(self):
        """Generate a read+write (admin) API key; show it once in a popup."""
        self.ensure_one()
        new_key = secrets.token_urlsafe(32)
        self.env['ir.config_parameter'].sudo().set_param(MCP_API_KEY_ADMIN_PARAM, new_key)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Admin token (read+write) — copy and store securely',
            'res_model': 'rag_odoo_mcp_server.generate_api_key_wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_api_key_display': new_key,
                'default_token_type': 'Admin (read+write)',
            },
        }

    def action_test_odoo_user_connection(self):
        """Test that the configured Odoo user credentials are valid."""
        self.ensure_one()
        ICP = self.env['ir.config_parameter'].sudo()
        login = self.mcp_odoo_user_login or ICP.get_param(MCP_ODOO_USER_LOGIN_PARAM) or ''
        # Use the field value if changed, otherwise the stored value
        password = self.mcp_odoo_user_password
        if not password or password == '********':
            password = ICP.get_param(MCP_ODOO_USER_PASSWORD_PARAM) or ''
        if not login or not password:
            raise UserError(_('Please set both username and password before testing the connection.'))
        db_name = self.env.cr.dbname
        try:
            # Odoo 17: _login is a classmethod taking positional (db, login, password, user_agent_env)
            # and returns user.id directly (not a dict).
            uid = self.env['res.users'].sudo()._login(db_name, login, password, {'interactive': False})
        except Exception as e:
            _logger.warning("MCP Odoo user auth test failed: %s", e)
            raise UserError(_('Authentication failed: %s') % e) from e
        if isinstance(uid, dict):
            # Defensive: some Odoo 17 forks mirror the v18 dict signature
            uid = uid.get('uid')
        if not uid:
            raise UserError(_('Authentication failed: invalid username or password.'))
        user = self.env['res.users'].sudo().browse(uid)
        raise UserError(_(
            'Connection successful!\n\n'
            'Authenticated as: %s (ID: %d)\n'
            'Groups: %s'
        ) % (user.name, uid, ', '.join(user.groups_id.mapped('full_name')[:10])))

    # -------------------------------------------------------------------
    # MCP client configuration generator (Claude Desktop / Cursor)
    # -------------------------------------------------------------------
    def _build_mcp_client_config(self):
        """Build the paste-ready JSON entry for the Claude Desktop / Cursor MCP
        client configuration file.

        Returns only the ``"odoo": { ... }`` entry (not the wrapping
        ``mcpServers`` object), so it can be dropped straight inside the user's
        existing ``"mcpServers": { ... }`` alongside any other servers.

        The entry is detected from this Odoo instance's base URL + database and
        adapted to the configured Authentication method:

        - token (require API key) → an Authorization: Bearer header carrying the
          User or Admin token (placeholder, the admin chooses which token).
        - token (no API key required) → no auth header (anonymous read-only).
        - odoo_user → no auth header: the server authenticates internally with
          the stored Odoo user credentials, the client sends nothing.
        - user_api_key → an Authorization: Bearer header carrying the connecting
          user's own native Odoo API key (placeholder, it is personal/secret).

        Anything the server cannot know (the secret key) is emitted as a clearly
        marked placeholder. The secret is passed through an ``env`` variable and
        referenced as ``${ODOO_MCP_AUTH}`` in the header, which is the documented
        mcp-remote pattern that avoids the header-splitting-on-spaces issue.
        """
        ICP = self.env['ir.config_parameter'].sudo()

        # --- base URL --------------------------------------------------
        base_url = (ICP.get_param('web.base.url') or '').strip()
        if not base_url:
            try:
                from odoo.http import request
                if request and request.httprequest:
                    base_url = request.httprequest.url_root.rstrip('/')
            except Exception:
                base_url = ''
        if not base_url:
            base_url = '<your-odoo-base-url>'
        base_url = base_url.rstrip('/')

        # --- http vs https (decides whether --allow-http is needed) ----
        probe = base_url if '://' in base_url else 'http://' + base_url
        scheme = (urlparse(probe).scheme or 'http').lower()
        is_http = scheme == 'http'

        db_name = self.env.cr.dbname or '<database>'
        sse_url = '%s/mcp/sse?db=%s' % (base_url, db_name)

        args = ['mcp-remote', sse_url, '--transport', 'sse-only']
        if is_http:
            args.append('--allow-http')

        # --- adapt to the authentication method ------------------------
        auth_method = (ICP.get_param(MCP_AUTH_METHOD_PARAM) or 'token').strip()
        env_block = None
        key_placeholder = None

        if auth_method == 'user_api_key':
            key_placeholder = '<PASTE-YOUR-PERSONAL-ODOO-API-KEY-HERE>'
        elif auth_method == 'odoo_user':
            # Server-side authentication; the client sends no secret.
            key_placeholder = None
        else:  # 'token'
            require_key = str(ICP.get_param(MCP_REQUIRE_API_KEY_PARAM) or '').strip().lower() in ('true', '1', 'yes')
            if require_key:
                key_placeholder = '<PASTE-YOUR-MCP-USER-OR-ADMIN-TOKEN-HERE>'

        if key_placeholder:
            # env-var indirection: the space in "Bearer <key>" lives inside the
            # env value, so the --header arg has no space to be split on.
            args += ['--header', 'Authorization:${ODOO_MCP_AUTH}']
            env_block = {'ODOO_MCP_AUTH': 'Bearer ' + key_placeholder}

        server_entry = {'command': 'npx', 'args': args}
        if env_block:
            server_entry['env'] = env_block

        # Return only the "odoo" entry (not the wrapping mcpServers object) so it
        # can be pasted straight into the user's existing "mcpServers": { ... }.
        return '"odoo": %s' % json.dumps(server_entry, indent=2)

    def action_generate_mcp_client_config(self):
        """Rebuild the MCP client configuration block from this instance's current
        base URL, database and authentication method, then reload the settings
        page so the fresh value is shown in the (copy-ready) textarea.
        """
        self.ensure_one()
        self.mcp_client_config = self._build_mcp_client_config()
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_open_mcp_config_tutorial(self):
        """Open a short tutorial that shows where Claude Desktop / Cursor store
        their MCP configuration file and how to edit it.
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': MCP_CONFIG_TUTORIAL_URL,
            'target': 'new',
        }
