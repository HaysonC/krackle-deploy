from django.http import JsonResponse
from django.conf import settings # Import settings

def test_view(request):
    allowed_origin = settings.CORS_ALLOWED_ORIGINS[0] if settings.CORS_ALLOWED_ORIGINS else ''
    try:
        arg1 = int(request.GET.get("arg1", 0))
        arg2 = int(request.GET.get("arg2", 0))
        result = arg1 + arg2
        response = JsonResponse({"message": f"The result of {arg1} + {arg2} is {result}"})
        response['Access-Control-Allow-Origin'] = allowed_origin
        return response
    except ValueError:
        response = JsonResponse({"error": "Invalid input, please provide integers for arg1 and arg2"}, status=400)
        response['Access-Control-Allow-Origin'] = allowed_origin
        return response
