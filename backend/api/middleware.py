# api/middleware.py

import json
import re
from django.http import JsonResponse
from django.contrib.auth.models import User


# ---------------- USERNAME MIDDLEWARE ----------------
class UsernameMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/api/signup/" and request.method == "POST":
            try:
                data = json.loads(request.body)
            except:
                return JsonResponse({"error": "Invalid JSON"}, status=400)

            username = data.get("username", "").strip()

            if not username:
                return JsonResponse({"error": "Username is required"}, status=400)

            if len(username) < 3 or len(username) > 20:
                return JsonResponse({"error": "Username must be 3 to 20 characters"}, status=400)

            if username[0] in "._" or username[-1] in "._":
                return JsonResponse({"error": "Username should not start/end with . or _"}, status=400)

            if not re.match(r"^[a-zA-Z0-9._]+$", username):
                return JsonResponse({"error": "Only letters, numbers, dot and underscore allowed"}, status=400)

            if ".." in username or "__" in username:
                return JsonResponse({"error": "Username cannot contain .. or __"}, status=400)

            if User.objects.filter(username=username).exists():
                return JsonResponse({"error": "Username already exists"}, status=400)

        return self.get_response(request)


# ---------------- EMAIL MIDDLEWARE ----------------
class EmailMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/api/signup/" and request.method == "POST":
            data = json.loads(request.body)
            email = data.get("email", "").strip()

            if not email:
                return JsonResponse({"error": "Email is required"}, status=400)

            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                return JsonResponse({"error": "Invalid email format"}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({"error": "Email already exists"}, status=400)

        return self.get_response(request)


# ---------------- PASSWORD MIDDLEWARE ----------------
class PasswordMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/api/signup/" and request.method == "POST":
            data = json.loads(request.body)
            password = data.get("password", "")

            if not password:
                return JsonResponse({"error": "Password is required"}, status=400)

            if len(password) < 8 or len(password) > 12:
                return JsonResponse({"error": "Password must be 8 to 12 characters"}, status=400)

            if not re.match(
                r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])',
                password
            ):
                return JsonResponse({
                    "error": "Password must contain uppercase, lowercase, digit, special char"
                }, status=400)

        return self.get_response(request)
