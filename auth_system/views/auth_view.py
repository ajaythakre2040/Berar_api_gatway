from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

from auth_system.models.login_fail_attempts import LoginFailAttempts
from auth_system.models.password_reset_log import PasswordResetLog
from auth_system.models.user import TblUser
from auth_system.models.login_session import LoginSession
from auth_system.serializers.user import TblUserSerializer
from auth_system.throttles import ChangePasswordThrottle, ForgotPasswordThrottle
from auth_system.utils.token_utils import blacklist_token, generate_tokens_for_user
from auth_system.utils.common import get_client_ip_and_agent, refresh_token_expiry_time
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.db.models import Q
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.utils.http import urlsafe_base64_decode
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from auth_system.utils.email_utils import send_reset_password_email
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from auth_system.utils.common import validate_password
from constant import MAX_LOGIN_ATTEMPTS
import re
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.db import transaction

User = get_user_model()
token_generator = PasswordResetTokenGenerator()


# class LoginView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         username = request.data.get("username")
#         password = request.data.get("password")

#         if not username or not password:
#             return Response(
#                 {
#                     "success": False,
#                     "status_code": status.HTTP_400_BAD_REQUEST,
#                     "message": "Email (username) and password are required.",
#                 },
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         try:

#             user = User.objects.get(Q(email=username) | Q(username=username))

#         except User.DoesNotExist:
#             return Response(
#                 {
#                     "success": False,
#                     "status_code": status.HTTP_404_NOT_FOUND,
#                     "message": "username not found.",
#                 },
#                 status=status.HTTP_404_NOT_FOUND,
#             )
#         if user.login_attempt >= MAX_LOGIN_ATTEMPTS:
#             return Response(
#                         {
#                             "status": "error",
#                             "status_code": status.HTTP_403_FORBIDDEN,
#                             "message": "Account locked. Try later.",
#                         },
#                         status=status.HTTP_403_FORBIDDEN,
#                     )
#         if not user.check_password(password):
#             return Response(
#                 {
#                     "success": False,
#                     "status_code": status.HTTP_401_UNAUTHORIZED,
#                     "message": "Incorrect password.",
#                 },
#                 status=status.HTTP_401_UNAUTHORIZED,
#             )

#         if not user.is_active:
#             return Response(
#                 {
#                     "success": False,
#                     "status_code": status.HTTP_403_FORBIDDEN,
#                     "message": "User account is disabled.",
#                 },
#                 status=status.HTTP_403_FORBIDDEN,
#             )

#         tokens = generate_tokens_for_user(user)

#         ip, agent = get_client_ip_and_agent(request)
#         user.login_attempt = 0
#         user.is_login = True
#         user.save()
#         access_token = tokens["access"]
#         refresh_token = tokens["refresh"]

#         LoginSession.objects.create(
#             user=user,
#             token=access_token,
#             is_active=True,
#             login_at=timezone.now(),
#             expiry_at=refresh_token_expiry_time(),
#             ip_address=ip,
#             agent_browser=agent,
#             request_headers=dict(request.headers),
#         )


#         return Response(
#             {
#                 "success": True,
#                 "message": "Login successful.",
#                 "status_code": status.HTTP_200_OK,
#                 "accessToken": tokens.get("access"),
#                 "refreshToken": tokens.get("refresh"),
#             },
#             status=status.HTTP_200_OK,
#         )
def is_valid_mobile(identifier: str) -> bool:
    pattern = r"^\+?1?\d{9,15}$"
    return bool(re.match(pattern, identifier))


# Helper: retrieve user by identifier (mobile/email/username)
def get_user_by_identifier(identifier: str):
    if is_valid_mobile(identifier):
        return TblUser.objects.filter(mobile_number=identifier).first()
    return TblUser.objects.filter(Q(email=identifier) | Q(username=identifier)).first()


# Helper: log failed login attempts
def log_failed_attempt(username, ip, agent, reason):
    LoginFailAttempts.objects.create(
        username=username,
        ip=ip,
        agent_browser=agent,
        user_details=reason,
        created_at=timezone.now(),
    )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        identifier = request.data.get("username")
        password = request.data.get("password")
        ip, agent = get_client_ip_and_agent(request)

        if not identifier or not password:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Username (email/username/mobile) and password are required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = get_user_by_identifier(identifier)
        if not user:
            log_failed_attempt(identifier, ip, agent, {"reason": "User not found"})
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "message": "User not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if user.login_attempts >= MAX_LOGIN_ATTEMPTS:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_403_FORBIDDEN,
                    "message": "Account locked due to too many failed login attempts.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if not user.check_password(password):
            user.login_attempts += 1
            user.save()
            log_failed_attempt(
                user.email,
                ip,
                agent,
                {
                    "reason": "Incorrect password",
                    "current_attempts": user.login_attempts,
                },
            )
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
                    "message": "User account is inactive or disabled.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Success: reset attempts & update status
        user.login_attempts = 0
        user.is_login = True
        user.save()

        tokens = generate_tokens_for_user(user)

        LoginSession.objects.create(
            user=user,
            token=tokens["access"],
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
                "status_code": status.HTTP_200_OK,
                "message": "Login successful.",
                "accessToken": tokens["access"],
                "refreshToken": tokens["refresh"],
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
        ip, agent = get_client_ip_and_agent(request)

        try:
            session = LoginSession.objects.filter(
                token=access_token, is_active=True
            ).first()
            if not session:
                return Response(
                    {
                        "success": False,
                        "status_code": status.HTTP_400_BAD_REQUEST,
                        "message": "Active session not found or user already logged out.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Verify that logout request's IP and agent match login session's details
            if session.ip_address != ip or session.agent_browser != agent:
                return Response(
                    {
                        "success": False,
                        "status_code": status.HTTP_403_FORBIDDEN,
                        "message": "Logout request's IP or device does not match the login session.",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Mark session as inactive and record logout time
            session.is_active = False
            session.logout_at = timezone.now()
            session.save()

            # Blacklist tokens to invalidate them
            blacklist_token(refresh_token, token_type="refresh", user=request.user)
            blacklist_token(access_token, token_type="access", user=request.user)

            # Update user's login status
            user = request.user
            user.is_login = False
            user.save(update_fields=["is_login"])

            return Response(
                {
                    "success": True,
                    "status_code": status.HTTP_200_OK,
                    "message": "Logout successful.",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as exc:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "message": "An unexpected error occurred during logout.",
                    "details": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ForgotPasswordThrottle]

    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response(
                {"success": False, "message": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_email(email)
            email = email.lower().strip()
        except ValidationError:
            return Response(
                {"success": False, "message": "Invalid email address."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ip = request.META.get("REMOTE_ADDR", "")
        user_agent = request.headers.get("User-Agent", "")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            PasswordResetLog.objects.create(
                email=email,
                ip_address=ip,
                user_agent=user_agent,
                action="forgot_password_requested",
                successful=False,
                details="Email not found",
            )

            return Response(
                {
                    "success": True,
                    "message": "If the email exists, a reset link has been sent.",
                },
                status=status.HTTP_200_OK,
            )

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)
        reset_link = f"{settings.FRONTEND_RESET_PASSWORD_URL}?uid={uid}&token={token}"

        try:

            send_reset_password_email(email, reset_link)
            successful = True
            details = "Reset link sent"
        except Exception as e:
            successful = False
            details = f"Email send failed: {str(e)}"

        PasswordResetLog.objects.create(
            user=user,
            email=email,
            ip_address=ip,
            user_agent=user_agent,
            action="forgot_password_requested",
            successful=successful,
            details=details,
        )

        return Response(
            {
                "success": True,
                "message": "If the email exists, a reset link has been sent.",
            },
            status=status.HTTP_200_OK,
        )


class ResetPasswordConfirmView(APIView):
    permission_classes = []
    throttle_classes = [ForgotPasswordThrottle]

    def post(self, request):
        uidb64 = request.data.get("uid")
        token = request.data.get("token")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")
        ip, user_agent = get_client_ip_and_agent(request)

        missing_fields = []

        if not uidb64:
            missing_fields.append("uid")
        if not token:
            missing_fields.append("token")
        if not new_password:
            missing_fields.append("new_password")
        if not confirm_password:
            missing_fields.append("confirm_password")

        if missing_fields:
            return Response(
                {
                    "success": False,
                    "message": f"Missing required parameter(s): {', '.join(missing_fields)}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_password != confirm_password:
            return Response(
                {
                    "success": False,
                    "message": "New password and confirm password do not match.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(new_password)
        except ValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": "Password validation failed.",
                    "errors": e.messages,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"success": False, "message": "Invalid or expired reset link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not token_generator.check_token(user, token):
            return Response(
                {"success": False, "message": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        PasswordResetLog.objects.create(
            user=user,
            email=user.email,
            ip_address=ip,
            user_agent=user_agent,
            action="forgot_password_reset",
            successful=True,
            details="Password reset successfully via email link",
        )

        return Response(
            {"success": True, "message": "Password reset successfully."},
            status=status.HTTP_200_OK,
        )


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ChangePasswordThrottle]

    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        ip, user_agent = get_client_ip_and_agent(request)

        if not old_password:
            return Response(
                {"success": False, "message": "Old password is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not new_password:
            return Response(
                {"success": False, "message": "New password is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.check_password(old_password):
            PasswordResetLog.objects.create(
                user=user,
                email=user.email,
                ip_address=ip,
                user_agent=user_agent,
                action="change_password",
                successful=False,
                details="Old password incorrect",
            )
            return Response(
                {"success": False, "message": "Old password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(new_password)
        except ValidationError as e:
            return Response(
                {
                    "success": False,
                    "message": "New password validation failed.",
                    "errors": e.messages,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if old_password == new_password:
            return Response(
                {
                    "success": False,
                    "message": "New password must be different from the old password.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        PasswordResetLog.objects.create(
            user=user,
            email=user.email,
            ip_address=ip,
            user_agent=user_agent,
            action="change_password",
            successful=True,
            details="Password changed successfully",
        )

        return Response(
            {"success": True, "message": "Password changed successfully."},
            status=status.HTTP_200_OK,
        )
