from django.urls import path

from kyc_api_gateway.views.client_management_view import (
     ClientManagementListCreate, ClientManagementDetail,
    #  ClientAllCount,
)
from kyc_api_gateway.views.vendor_management_view import (

     VendorManagementListCreate, VendorManagementDetail,
    #  VendorAllCount,
     VendorApiList
)

from kyc_api_gateway.views.api_management_view import (
     ApiManagementListCreate, ApiManagementDetail,
     ApiManagementList
)

from kyc_api_gateway.views.uat.pan_details_view import PanUatDetailsAPIView

# from kyc_api_gateway.views.pro.pan_details_view import PanProductionDetailsAPIView

from kyc_api_gateway.views.uat.bill_details_view import BillUatDetailsAPIView

from kyc_api_gateway.views.uat.name_details_view import NameMatchUatAPIView

from kyc_api_gateway.views.uat.voter_details_view import VoterUatAPIView

from kyc_api_gateway.views.uat.rc_detailsi_view import RcUatAPIView


urlpatterns = [
    path(
        "client_management/",
        ClientManagementListCreate.as_view(),
        name="client_management_list_create",
    ),
    path(
        "client_management/<int:pk>/",
        ClientManagementDetail.as_view(),
        name="client_management_detail",
    ),
    # path("client_count/", ClientAllCount.as_view(), name="client_count"),
    path(
        "vendors_management/",
        VendorManagementListCreate.as_view(),
        name="client_management_list_create",
    ),
    path(
        "vendors_management/<int:pk>/",
        VendorManagementDetail.as_view(),
        name="client_management_detail",
    ),
    
    #uat
    # path("vendor_active_count/", VendorAllCount.as_view(), name="Vendor_all_count"),
    path("vendors_api_list/", VendorApiList.as_view(), name="vendor_api_list"),
    path("api_management/", ApiManagementListCreate.as_view(), name="api_list_create"),
    path("api_management/<int:pk>/", ApiManagementDetail.as_view(), name="api_detail"),
    path("end_point_list/", ApiManagementList.as_view(), name="api_list"),
    # path("uat_pan-details/", PanUatDetailsAPIView.as_view(), name="pan-details"),
    path("uat_pan_details/", PanUatDetailsAPIView.as_view(), name="uat_pan_details"),
    path("uat_bill_details/", BillUatDetailsAPIView.as_view(), name="uat_bill_details"),
    path("uat_name_details/", NameMatchUatAPIView.as_view(), name="uat_name_details"),
    path("uat_voter_details/", VoterUatAPIView.as_view(), name="uat_voter_details"),
    path("uat_rc_details/", RcUatAPIView.as_view(), name="uat_rc_details"),

    #production
    # path("prod_pan-details/", PanProductionDetailsAPIView.as_view(), name="pan-details-prod"),
    # path("prod_pan_details/", PanProductionDetailsAPIView.as_view(), name="prod_pan_details"),


]
