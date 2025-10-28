from django.http import HttpResponse
from django.conf import settings

class CorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        origin = request.META.get('HTTP_ORIGIN')
        allowed_origin = ''


        if origin and settings.CORS_ALLOWED_ORIGINS:
            if origin in settings.CORS_ALLOWED_ORIGINS:
                allowed_origin = origin
        elif settings.CORS_ALLOWED_ORIGINS:
             allowed_origin = settings.CORS_ALLOWED_ORIGINS[0]

        if request.method == 'OPTIONS':
            
            response = HttpResponse(status=200)

            response['Access-Control-Allow-Credentials'] = 'true'
            
            if allowed_origin:
                response['Access-Control-Allow-Origin'] = allowed_origin
            response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            if hasattr(settings, 'CORS_ALLOW_HEADERS') and settings.CORS_ALLOW_HEADERS:
                response['Access-Control-Allow-Headers'] = ', '.join(settings.CORS_ALLOW_HEADERS)
            else:
                response['Access-Control-Allow-Headers'] = 'Content-Type'
            return response
        
        response = self.get_response(request)
        
        if allowed_origin:
            response['Access-Control-Allow-Origin'] = allowed_origin
        
        
        return response
