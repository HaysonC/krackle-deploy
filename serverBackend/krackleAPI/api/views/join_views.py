from django.http import JsonResponse
import json
from .share_data import lobbies_data
import uuid
import secrets 
from django.views.decorators.csrf import csrf_exempt # Import csrf_exempt
from django.conf import settings # Import settings

@csrf_exempt
def create_lobby(request):
    allowed_origin = settings.CORS_ALLOWED_ORIGINS[0] if settings.CORS_ALLOWED_ORIGINS else ''
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            max_players = data.get('max_players')
            lobby_name = data.get('lobby_name')
            rounds = data.get('rounds')
        except json.JSONDecodeError:
            response = JsonResponse({"error": "Invalid JSON payload."}, status=400)
            response['Access-Control-Allow-Origin'] = allowed_origin
            return response

        if not all([username, isinstance(max_players, int), lobby_name, isinstance(rounds, int)]):
            response = JsonResponse({
                "error": "Missing or invalid parameters. Required: username (string), max_players (int), lobby_name (string), rounds (int)."
            }, status=400)
            response['Access-Control-Allow-Origin'] = allowed_origin
            return response

        if not (2 <= max_players <= 50): 
            response = JsonResponse({"error": "max_players must be between 2 and 50."}, status=400)
            response['Access-Control-Allow-Origin'] = allowed_origin
            return response
        if not (1 <= rounds <= 10):
            response = JsonResponse({"error": "rounds must be between 1 and 10."}, status=400)
            response['Access-Control-Allow-Origin'] = allowed_origin
            return response

        while True:
            lobby_code = secrets.token_hex(3).upper()
            if lobby_code not in lobbies_data:
                break
        
        admin_token = uuid.uuid4().hex

        lobbies_data[lobby_code] = {
            "name": lobby_name,
            "max_players": max_players,
            "rounds": rounds,
            "admin_token": admin_token, # Host uses this as their user_token
            "host_username": username,
            "players": [username], # Creator is the first player
            "verified_players": [], # Players who have submitted their photos
            "player_images": {}, # Mapping of username to image filename
            "game_state": {},
            "connected_users": {}, # For WebSocket connected users
            "issued_player_tokens": {admin_token: username},
            "laugh_meters": {}, # {Player1Name: Player1LaughMeterValue, Player2Name: Player2LaughMeterValue, ...}
        }

        # in setting, we add a laught increment which is the increment value for the laugh meter

        response = JsonResponse({
            "message": f"Lobby '{lobby_name}' created successfully.",
            "lobby_code": lobby_code,
            "admin_token": admin_token, # For the host
            "username": username
        }, status=201)
        response['Access-Control-Allow-Origin'] = allowed_origin
        return response

    response = JsonResponse({"error": "Only POST method is allowed."}, status=405)
    response['Access-Control-Allow-Origin'] = allowed_origin
    return response

@csrf_exempt
def join_lobby(request):
    allowed_origin = settings.CORS_ALLOWED_ORIGINS[0] if settings.CORS_ALLOWED_ORIGINS else ''
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            lobby_code = data.get('lobby_code')
        except json.JSONDecodeError:
            response = JsonResponse({"error": "Invalid JSON payload."}, status=400)
            response['Access-Control-Allow-Origin'] = allowed_origin
            return response

        if not username or not lobby_code:
            response = JsonResponse({"error": "Username and lobby parameters are required."}, status=400)
            response['Access-Control-Allow-Origin'] = allowed_origin
            return response

        if lobby_code not in lobbies_data:
            response = JsonResponse({"error": f"Lobby '{lobby_code}' not found."}, status=404)
            response['Access-Control-Allow-Origin'] = allowed_origin
            return response

        lobby_info = lobbies_data[lobby_code]

        if username in lobby_info["players"]:
             pass

        if username not in lobby_info["players"]:
            if len(lobby_info["players"]) >= lobby_info["max_players"]:
                response = JsonResponse({"error": f"Lobby '{lobby_code}' is full (HTTP join limit)."}, status=400)
                response['Access-Control-Allow-Origin'] = allowed_origin
                return response
            lobby_info["players"].append(username)

        # Generate a player token for WebSocket connection
        player_token = uuid.uuid4().hex
        lobby_info["issued_player_tokens"][player_token] = username

        response = JsonResponse({
            "message": f"Successfully joined lobby '{lobby_code}'.",
            "username": username,
            "lobby_code": lobby_code,
            "lobby_name": lobby_info["name"],
            "players": lobby_info["players"],
            "player_token": player_token # Client uses this for WebSocket connection
        }, status=200)
        response['Access-Control-Allow-Origin'] = allowed_origin
        return response
    
    response = JsonResponse({"error": "Only POST method is allowed."}, status=405)
    response['Access-Control-Allow-Origin'] = allowed_origin
    return response

