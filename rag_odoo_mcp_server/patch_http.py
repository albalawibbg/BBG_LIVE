# -*- coding: utf-8 -*-
"""
Patch Odoo's request handling so session.db is set from ?db=, X-Odoo-Database header,
or Bearer db:key token BEFORE the Application chooses between _serve_db and _serve_nodb.
In Odoo 17, that choice is made in Application.__call__ using request.db, which is set
in Request._post_init() by _get_session_and_dbname(). So we must patch _get_session_and_dbname
to inject the db from query/header/token; otherwise requests to /mcp/sse?db=xxx get 404
because request.db is None and Odoo uses _serve_nodb() whose routing map has no MCP routes.
"""
import logging

_logger = logging.getLogger(__name__)

_APPLIED = False


def _mcp_db_from_request(request):
    """Extract database name from query, X-Odoo-Database header, or Bearer db:key."""
    if not getattr(request, "httprequest", None):
        return None
    db = request.httprequest.args.get("db")
    if db:
        return db
    db = (request.httprequest.headers.get("X-Odoo-Database") or "").strip()
    if db:
        return db
    auth = (request.httprequest.headers.get("Authorization") or "").strip()
    if auth.startswith("Bearer "):
        token = auth[7:].strip()
        if ":" in token:
            return token.split(":", 1)[0].strip() or None
    return None


def apply_patch():
    """Set session.db from URL/header/token inside _get_session_and_dbname so request.db
    is set before Application.__call__ branches to _serve_db vs _serve_nodb."""
    global _APPLIED
    if _APPLIED:
        return
    try:
        import odoo.http as http
        # Request is the class that has _get_session_and_dbname (Odoo 17)
        Request = getattr(http, "Request", None)
        if not Request or not hasattr(Request, "_get_session_and_dbname"):
            _logger.warning(
                "rag_odoo_mcp_server: Request._get_session_and_dbname not found, "
                "multi-db MCP may return 404. Use --db-filter=^yourdb$ or set db in session."
            )
            _APPLIED = True
            return

        _get_session_and_dbname_orig = Request._get_session_and_dbname
        if getattr(_get_session_and_dbname_orig, "_mcp_patched", False):
            _APPLIED = True
            return

        def _get_session_and_dbname_patched(self):
            session, dbname = _get_session_and_dbname_orig(self)
            # Inject db from query/header/token so that when Odoo has not set session.db
            # (e.g. first request with ?db=), we use it and the branch in __call__ uses _serve_db.
            db_from_request = _mcp_db_from_request(self)
            if db_from_request and session is not None:
                session.db = db_from_request
                dbname = db_from_request
            return session, dbname

        _get_session_and_dbname_patched._mcp_patched = True
        Request._get_session_and_dbname = _get_session_and_dbname_patched
        _APPLIED = True
        _logger.info("rag_odoo_mcp_server: patched _get_session_and_dbname for db from query/header/token")
    except Exception as e:
        _logger.warning("rag_odoo_mcp_server: could not patch _get_session_and_dbname: %s", e)
        _APPLIED = True
