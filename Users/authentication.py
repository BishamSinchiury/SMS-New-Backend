from rest_framework.authentication import SessionAuthentication

class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    Custom SessionAuthentication that skips CSRF check.
    Ideal for decoupled SPAs where CORS and SameSite cookies already provide security.
    """
    def enforce_csrf(self, request):
        return  # Skip CSRF check
