"""
Middleware de headers de segurança (Sprint 14 - Preparação para Produção).

Adiciona headers HTTP defensivos padrão em toda resposta. Não altera
nenhum comportamento de negócio - é seguro em qualquer ambiente
(desenvolvimento ou produção).
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        # HSTS - o backend em produção (Fly.io) já roda atrás de HTTPS
        # (force_https = true no fly.toml). O header é inofensivo em
        # dev/HTTP, pois só é respeitado pelo navegador em conexões HTTPS.
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        # CSP - o backend só serve JSON de API, então a política pode ser
        # restritiva ao extremo. Existe apenas como defesa em profundidade
        # caso alguma resposta seja renderizada num contexto de navegador
        # (ex.: erro cru). O Swagger UI em /docs usa CDN externo e pode
        # quebrar sob essa política - tudo bem, /docs não roda em produção.
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; frame-ancestors 'none'"
        )
        return response
