"""Decision A local session envelopes backed by live central authentication."""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import APIException, AuthenticationFailed
from integration.central_auth import validate_session, AuthorityUnavailable

class Smart3AISSOAuthentication(JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        raw_request = getattr(request, '_request', request)
        if result is None and getattr(getattr(raw_request, 'user', None), 'is_authenticated', False):
            raise AuthenticationFailed('Se requiere sesión central.')
        return result

    def get_validated_token(self, raw_token):
        from .local_tokens import LocalAccessToken
        from rest_framework_simplejwt.exceptions import TokenError
        try:
            return LocalAccessToken(raw_token)
        except TokenError:
            raise AuthenticationFailed('Sesión local inválida.') from None

    def get_user(self, validated_token):
        try:
            user = super().get_user(validated_token)
            validate_session(validated_token, user)
            return user
        except APIException:
            raise
        except Exception:
            raise AuthorityUnavailable() from None
