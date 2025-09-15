from django.urls import path

from kyc_api_gateway.views.role_menagement_view import (

     RoleManagementListCreate, RoleManagementDetail,
)

from kyc_api_gateway.views.user_menagement_view import (

     UserManagementListCreate, UserManagementDetail,
)

from kyc_api_gateway.views.client_management_view import (

     ClientManagementListCreate, ClientManagementDetail,
)

from kyc_api_gateway.views.vendor_management_view import (

     VendorManagementListCreate, VendorManagementDetail,
)


urlpatterns = [
  
    path("role_management/", RoleManagementListCreate.as_view(), name="role_management_list_create"),
    path("role_management/<int:pk>/", RoleManagementDetail.as_view(), name="prole_management_detail"),

    path("user_management/", UserManagementListCreate.as_view(), name="user_management_list_create"),
    path("user_management/<int:pk>/", UserManagementDetail.as_view(), name="user_management_detail"),

    path("client_management/", ClientManagementListCreate.as_view(), name="client_management_list_create"),
    path("client_management/<int:pk>/", ClientManagementDetail.as_view(), name="client_management_detail"),

    path("vendors_management/", VendorManagementListCreate.as_view(), name="client_management_list_create"),
    path("vendors_management/<int:pk>/", VendorManagementDetail.as_view(), name="client_management_detail"),

]
