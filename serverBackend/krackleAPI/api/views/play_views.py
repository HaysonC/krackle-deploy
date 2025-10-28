from django.http import JsonResponse
from .share_data import lobbies_data
from django.conf import settings # Import settings



def get_lobby_players(request):
    allowed_origin = settings.CORS_ALLOWED_ORIGINS[0] if settings.CORS_ALLOWED_ORIGINS else ''
    if request.method == 'GET':
        lobby_code = request.headers.get('X-Lobby-Code')

        if not lobby_code:
            # Fallback to query parameter if header is not present
            lobby_code = request.GET.get('lobby_code') 
            if not lobby_code:
                 response = JsonResponse({"error": "X-Lobby-Code header or lobby_code query parameter is required."}, status=400)
                 response['Access-Control-Allow-Origin'] = allowed_origin
                 return response

        if lobby_code not in lobbies_data:
            response = JsonResponse({"error": f"Lobby '{lobby_code}' not found."}, status=404)
            response['Access-Control-Allow-Origin'] = allowed_origin
            return response

        lobby_info = lobbies_data[lobby_code] # Get the specific lobby's data dictionary
        
        # Extract the actual list of players and other desired information
        actual_player_list = lobby_info.get("players", [])
        lobby_name = lobby_info.get("name", "N/A")
        host_username = lobby_info.get("host_username", "N/A")
        max_players = lobby_info.get("max_players", 0)
        rounds = lobby_info.get("rounds", 0)
        # You can also include connected_users if relevant for the frontend
        # connected_users_details = list(lobby_info.get('connected_users', {}).values())
        # connected_player_usernames = [user['username'] for user in connected_users_details]


        response = JsonResponse({
            "lobby_code": lobby_code,
            "lobby_name": lobby_name,
            "host_username": host_username,
            "max_players": max_players,
            "rounds": rounds,
            "players": actual_player_list # This now correctly refers to the list of player usernames
        }, status=200)
        response['Access-Control-Allow-Origin'] = allowed_origin
        return response

    response = JsonResponse({"error": "Only GET method is allowed."}, status=405)
    response['Access-Control-Allow-Origin'] = allowed_origin
    return response


