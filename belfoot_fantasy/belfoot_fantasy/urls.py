"""
URL configuration for belfoot_fantasy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import logout
from django.urls import path, include, re_path
from apps.users.views import (RegisterUser, SecuredView, LoginUser,  ForgotPassword,
                              ResetPassword, OAuth2, OAuth2Complete,
                              TelegramAuth,)
from apps.users_profile.views import (ProfilePicture, ChangeUsername, ChangeEmail, ChangeEmailConfirmation,
                                      DeleteAccount, DeleteAccountConfirmation, GetUserInfo)

from apps.databases.views import (CRUDTurns, CRUDPlayers, CRUDMatches)

from apps.game.views import PlayersCommandsCRUD, BuyPlayers

#from apps.users.views import TestingLocalModel
#OAuth2, OAuth2Complete, TelegramAuth)
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from drf_yasg.views import get_schema_view  # new
from drf_yasg import openapi  # new
from rest_framework import permissions
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView
)



schema_view = get_schema_view(
    openapi.Info(
        title="API",
        default_version='v1',
        description="API documentation",
        terms_of_service="<https://www.google.com/policies/terms/>",
        contact=openapi.Contact(email="contact@api.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

#//TODO РОУТЕРЫ
urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    path('users/admin/', admin.site.urls),

    path('users/auth/register', RegisterUser.as_view(), name='register_user'),
    path('users/auth/login', LoginUser.as_view(), name='login_user'),
    path('users/auth/secured_view', SecuredView.as_view(), name='test_secured_view'),
    path('users/auth/logout', TokenBlacklistView.as_view(), name='logout_user'),
    path('users/auth/forgot_password', ForgotPassword.as_view(), name='forgot_password'),
    path('users/auth/forgot_password/reset_password', ResetPassword.as_view(), name='reset_password'),
    #path('users/auth/token', TokenObtainPairView.as_view(), name='token_obtain'),
    path('users/auth/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/auth/google-oauth2/login', OAuth2.as_view(), name='google_oauth_login'),
    re_path(r'users/auth/google-oauth2/complete/?.+', OAuth2Complete.as_view(), name='google_oauth_complete'),
    path('users/auth/telegram-auth/login', csrf_exempt(TelegramAuth.as_view()), name='telegram_auth'),

    path('users/profile/picture', ProfilePicture.as_view(), name='change_picture'),
    path('users/profile/change_username', ChangeUsername.as_view(), name='change_username'),
    path('users/profile/change_email', ChangeEmail.as_view(), name='change_email'),
    path('users/profile/change_email/confirm', ChangeEmailConfirmation.as_view(), name='change_email_confirmation'),
    path('users/profile/delete_account', DeleteAccount.as_view(), name='delete_account'),
    path('users/profile/delete_account/confirm', DeleteAccountConfirmation.as_view(), name='delete_account_confirmation'),
    path('users/profile/info', GetUserInfo.as_view(), name='get_user_info'),

    path('fantasy/db/turns', CRUDTurns.as_view(), name='crud_turns'),
    path('fantasy/db/players', CRUDPlayers.as_view(), name='crud_players'),
    path('fantasy/db/matches', CRUDMatches.as_view(), name='crud_matches'),

    path('fantasy/game/command', PlayersCommandsCRUD.as_view(), name='crud_players_commands'),
    path('fantasy/game/shop', BuyPlayers.as_view(), name='buy_player')

    #path('users/auth/common_auth', AuthRequestHandler.as_view(), name='common_auth')
    #path('testing/', TestingLocalModel.as_view()),
    #path('users/auth/token_check', TokenAuthUser.as_view(), name='token_check'),
]
