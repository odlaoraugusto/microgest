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
        return response
