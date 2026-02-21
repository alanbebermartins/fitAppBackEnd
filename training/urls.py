from django.urls import path
from .views import RegistrarTreinoView, LoginEmailView, LogoutView, MeView, RegisterUserView

urlpatterns = [
    # ROTAS API LOGIN
    path("auth/login/", LoginEmailView.as_view(), name="login-email"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/me/", MeView.as_view(), name="me"),

    # CADASTRAR NOVO USUÁRIO
    path("auth/register/", RegisterUserView.as_view(), name="register-user"),

    # ROTA DE REGISTRAR EXERCICIO
    path('register/', RegistrarTreinoView.as_view(), name='registrar-treino'),
]
