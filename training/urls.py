from django.urls import path
from .views import (
    RegistrarTreinoView,
    LoginEmailView,
    LogoutView,
    MeView,
    RegisterUserView,
    RefreshTokenView,
    auth_check,
    get_list_all_exercises,
    get_list_all_muscle_groups,
)
from .authentication import CookieJWTAuthentication

urlpatterns = [
    # ROTAS API LOGIN
    path("auth/login/", LoginEmailView.as_view(), name="login-email"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/refresh/", RefreshTokenView.as_view(), name="token-refresh"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("auth/check/", auth_check, name="auth_check"),

    # CADASTRAR NOVO USUÁRIO
    path("auth/register/", RegisterUserView.as_view(), name="register-user"),

    # ROTA DE REGISTRAR EXERCICIO
    path('training/register/', RegistrarTreinoView.as_view(), name='registrar-treino'),

    # ROTA DE BUSCAR TODOS OS EXERCICIOS
    path('get_list_all_exercises/', get_list_all_exercises, name='listar-tipos-exercicios'),

    # ROTA DE BUSCAR TODOS OS GRUPOS MUSCULARES
    path('get_list_all_muscle_groups/', get_list_all_muscle_groups, name='listar-grupos-musculares'),
]
