import uuid
from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .models import Training, Exercise
from .serializers import TrainingSerializer, ExerciseListSerializer
from rest_framework_simplejwt.exceptions import TokenError
from .authentication import CookieJWTAuthentication

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
    authentication_classes = []
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
            samesite="Lax",
            path="/"
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
# REFRESH
# ==========================

class RefreshTokenView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):

        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"error": "Refresh token não encontrado"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            response = Response(
                {"message": "Token renovado"},
                status=status.HTTP_200_OK
            )

            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=False,
                samesite="Lax",
                path="/"
            )

            return response

        except TokenError:
            return Response(
                {"error": "Refresh token inválido"},
                status=status.HTTP_401_UNAUTHORIZED
            )

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

@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def get_list_all_exercises(request):
    exercises = Exercise.objects.all()
    serializer = ExerciseListSerializer(exercises, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def get_list_all_muscle_groups(request):
    # Busca todas as categorias distintas da coluna muscle_group,
    # entrega uma lista plana e única, sem duplicidade.
    groups = sorted({
        group for group in Exercise.objects.values_list("muscle_group", flat=True) if group
    })

    payload = [{"muscle_group": group} for group in groups]
    return Response(payload, status=status.HTTP_200_OK)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def get_list_all_realized_exercises(request, exercise_id=None):
    """
    Retorna os 12 registros mais recentes de treino para um exercise_id informado
    pelo caminho da própria URL, sem depender de query string.

    Aceita UUID com hífens e sem hífens.
    """
    if not exercise_id:
        return Response(
            {"error": "O parâmetro exercise_id é obrigatório no path da URL."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    raw_id = str(exercise_id).strip().replace("/", "")

    # Normaliza UUID sem hífens para o formato canônico com hífens.
    # Exemplo: 6257567d5aab42c9bd034f1697dd1aa1 -> 6257567d-5aab-42c9-bd03-4f1697dd1aa1
    if len(raw_id) == 32 and all(ch in "0123456789abcdefABCDEF" for ch in raw_id):
        raw_id = f"{raw_id[0:8]}-{raw_id[8:12]}-{raw_id[12:16]}-{raw_id[16:20]}-{raw_id[20:32]}"

    try:
        parsed_uuid = uuid.UUID(raw_id)
    except (TypeError, ValueError):
        return Response(
            {"error": "O parâmetro exercise_id deve ser um UUID válido."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    records = Training.objects.filter(exercise_id=parsed_uuid).order_by("-training_date", "-id")[:12]

    payload = [
        {
            "exercise_id": str(record.exercise_id),
            "weight_kg": record.weight_kg,
            "training_date": record.training_date.isoformat(),
        }
        for record in records
    ]

    return Response(payload, status=status.HTTP_200_OK)


@api_view(["GET"])
@authentication_classes([CookieJWTAuthentication])
@permission_classes([IsAuthenticated])
def auth_check(request):

    return Response({
        "authenticated": True,
        "user_id": request.user.id,
        "email": request.user.email
    })