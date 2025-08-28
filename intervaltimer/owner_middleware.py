
import uuid
from django.utils.deprecation import MiddlewareMixin

class OwnerCookieMiddleware(MiddlewareMixin):
    COOKIE_NAME = 'owner_token'
    def process_response(self, request, response):
        if self.COOKIE_NAME not in request.COOKIES:
            token = uuid.uuid4().hex
            # Set for ~2 years
            response.set_cookie(self.COOKIE_NAME, token, max_age=60*60*24*730, samesite='Lax')
        return response
