from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .models import Training
from .serializers import TrainingSerializer

# ==========================
# REGISTRA TREINO (PROTEGIDO)
# ==========================
#     
class RegistrarTreinoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TrainingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# ==========================
# LOGIN COM EMAIL + SENHA
# ==========================
class LoginEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email e senha são obrigatórios"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Usuário não encontrado"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Autentica pelo username real do Django
        user = authenticate(username=user_obj.username, password=password)

        if user is None:
            return Response(
                {"error": "Credenciais inválidas"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response(
            {"message": "Login realizado com sucesso"},
            status=status.HTTP_200_OK
        )

        # Cookies HttpOnly (SEGURANÇA)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,   # True só quando estiver em HTTPS
            samesite="Lax"
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="Lax"
        )

        return response


# ==========================
# LOGOUT (REMOVE COOKIES)
# ==========================
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response(
            {"message": "Logout realizado com sucesso"},
            status=status.HTTP_200_OK
        )

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response


# ==========================
# ME (RETORNA DADOS DO USER)
# ==========================
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email
        })

# ==========================
# CADASTRA NOVO USUÁRIO
# ==========================

class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        email = request.data.get("email")
        password = request.data.get("password")

        if not first_name or not last_name or not email or not password:
            return Response(
                {"error": "Todos os campos são obrigatórios"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verifica se email já existe
        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "Esse email já está cadastrado"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Cria username automaticamente baseado no email
        username = email.split("@")[0]

        # Se username já existir, cria um username diferente
        counter = 1
        original_username = username
        while User.objects.filter(username=username).exists():
            username = f"{original_username}{counter}"
            counter += 1

        # Cria usuário (senha vai ser salva corretamente HASH)
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        user.save()

        return Response(
            {"message": "Usuário cadastrado com sucesso"},
            status=status.HTTP_201_CREATED
        )

