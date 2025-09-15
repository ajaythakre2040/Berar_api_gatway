from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from auth_system.views.auth_view import (
    LoginView,
    LogoutView,
)
from auth_system.views.menu_view import (
    MenuDetailView,
    MenuListCreateView,
)
from auth_system.views.role_permission_view import (
    RolePermissionDetailView,
    RolePermissionListCreateView,
)
from auth_system.views.role_view import RoleDetailView, RoleListCreateView
from auth_system.views.user_view import UserDetailUpdateDeleteView, UserListCreateView

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("login/", LoginView.as_view(), name="user-login"),
    path("logout/", LogoutView.as_view(), name="user-logout"),
    path("users/", UserListCreateView.as_view(), name="user-list"),
    path(
        "users/<int:id>/",
        UserDetailUpdateDeleteView.as_view(),
        name="user-detail-update-delete",
    ),
    path("menus/", MenuListCreateView.as_view(), name="menu-list-create"),
    path("menus/<int:pk>/", MenuDetailView.as_view(), name="menu-detail"),
    path("roles/", RoleListCreateView.as_view(), name="role-list-create"),
    path("roles/<int:pk>/", RoleDetailView.as_view(), name="role-detail"),
    path(
        "role-permissions/",
        RolePermissionListCreateView.as_view(),
        name="role-permission-list-create",
    ),
    path(
        "role-permissions/<int:role_id>/",
        RolePermissionDetailView.as_view(),
        name="role-permission-detail",
    ),
]
