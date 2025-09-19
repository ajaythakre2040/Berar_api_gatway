from django.urls import path

from kyc_api_gateway.views.client_management_view import (

     ClientManagementListCreate, ClientManagementDetail,
     ClientAllCount,
)

from kyc_api_gateway.views.vendor_management_view import (

     VendorManagementListCreate, VendorManagementDetail,
     VendorAllCount,
)

from kyc_api_gateway.views.api_management_view import (

     ApiManagementListCreate, ApiManagementDetail,
)


urlpatterns = [

    path("client_management/", ClientManagementListCreate.as_view(), name="client_management_list_create"),
    path("client_management/<int:pk>/", ClientManagementDetail.as_view(), name="client_management_detail"),
    path("client_count/", ClientAllCount.as_view(), name="client_count"),

    path("vendors_management/", VendorManagementListCreate.as_view(), name="client_management_list_create"),
    path("vendors_management/<int:pk>/", VendorManagementDetail.as_view(), name="client_management_detail"),
    path('vendor_active_count/', VendorAllCount.as_view(), name='Vendor_all_count'),


    path('api_management/', ApiManagementListCreate.as_view(), name='api_list_create'),
    path('api_management/<int:pk>/', ApiManagementDetail.as_view(), name='api_detail'),


]
