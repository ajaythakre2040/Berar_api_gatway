from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

from auth_system.models.user import TblUser
from auth_system.models.login_session import LoginSession
from auth_system.serializers.user import TblUserSerializer
from auth_system.utils.token_utils import blacklist_token, generate_tokens_for_user
from auth_system.utils.common import get_client_ip_and_agent, refresh_token_expiry_time
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

User = get_user_model()


# class RegisterView(generics.CreateAPIView):
#     queryset = TblUser.objects.all()
#     serializer_class = TblUserSerializer
#     permission_classes = [AllowAny]

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#             user.created_by = request.user.id
#             user.save()
#             return Response(
#                 {
#                     "success": True,
#                     "status_code": status.HTTP_201_CREATED,
#                     "message": "User registered successfully.",
#                     "user": TblUserSerializer(user).data,
#                 },
#                 status=status.HTTP_201_CREATED,
#             )
#         return Response(
#             {
#                 "success": False,
#                 "status_code": status.HTTP_400_BAD_REQUEST,
#                 "message": "Registration failed.",
#                 "errors": serializer.errors,
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("username")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Email (username) and password are required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "message": "username not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not user.check_password(password):
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_401_UNAUTHORIZED,
                    "message": "Incorrect password.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_403_FORBIDDEN,
                    "message": "User account is disabled.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        tokens = generate_tokens_for_user(user)

        ip, agent = get_client_ip_and_agent(request)

        access_token = tokens["access"]
        refresh_token = tokens["refresh"]

        LoginSession.objects.create(
            user=user,
            token=access_token,
            is_active=True,
            login_at=timezone.now(),
            expiry_at=refresh_token_expiry_time(),
            ip_address=ip,
            agent_browser=agent,
            request_headers=dict(request.headers),
        )

        return Response(
            {
                "success": True,
                "message": "Login successful.",
                "status_code": status.HTTP_200_OK,
                "accessToken": tokens.get("access"),
                "refreshToken": tokens.get("refresh"),
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        auth_header = request.headers.get("Authorization")

        if (
            not refresh_token
            or not auth_header
            or not auth_header.startswith("Bearer ")
        ):
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Both refresh and access tokens are required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        access_token = auth_header.split(" ")[1]

        try:

            session = LoginSession.objects.filter(token=access_token).first()

            if session:
                if not session.is_active:
                    return Response(
                        {
                            "success": False,
                            "status_code": status.HTTP_400_BAD_REQUEST,
                            "message": "User is already logged out.",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                session.is_active = False
                session.logout_at = timezone.now()
                session.save()

            blacklist_token(refresh_token, token_type="refresh", user=request.user)
            blacklist_token(access_token, token_type="access", user=request.user)

            return Response(
                {
                    "success": True,
                    "status_code": status.HTTP_200_OK,
                    "message": "Logout successful.",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "message": "An unexpected error occurred during logout.",
                    "details": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
