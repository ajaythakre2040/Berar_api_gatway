from django.urls import path

from kyc_api_gateway.views.Kyc_vendor_priority_view import KycVendorPriorityDetail, KycVendorPriorityListCreate
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

from kyc_api_gateway.views.kyc_my_services_view import (
    KycMyServicesListCreate,
    KycMyServicesDetail,
)

from kyc_api_gateway.views.kyc_client_services_management_view import (
    KycClientServicesListCreate,
    KycClientServicesDetail,
)



# from kyc_api_gateway.views.uat.pan_details_view import PanUatDetailsAPIView

# from kyc_api_gateway.views.pro.pan_details_view import PanProductionDetailsAPIView

# from kyc_api_gateway.views.uat.bill_details_view import BillUatDetailsAPIView

from kyc_api_gateway.views.uat.pan_details_view import UatPanDetailsAPIView
from kyc_api_gateway.views.uat.bill_details_view import UatBillDetailsAPIView
from kyc_api_gateway.views.uat.name_details_view import NameMatchUatAPIView
from kyc_api_gateway.views.uat.voter_details_view import UatVoterDetailsAPIView
from kyc_api_gateway.views.uat.rc_detailsi_view import RcUatAPIView
from kyc_api_gateway.views.uat.driving_license_details_view import UatDrivingLicenseAPIView

#production
from kyc_api_gateway.views.pro.bill_details_view import ProBillDetailsAPIView   
from kyc_api_gateway.views.pro.pan_details_view import ProPanDetailsAPIView   
from kyc_api_gateway.views.pro.name_details_view import ProNameMatchAPIView
from kyc_api_gateway.views.pro.rc_detailsi_view import ProRcAPIView
from kyc_api_gateway.views.pro.voter_details_view import ProVoterDetailsAPIView
from kyc_api_gateway.views.pro.driving_license_details_view import ProDrivingLicenseAPIView


urlpatterns = [
    path("client_management/",ClientManagementListCreate.as_view(), name="client_management_list_create",),
    path("client_management/<int:pk>/", ClientManagementDetail.as_view(), name="client_management_detail",),
    # path("client_count/", ClientAllCount.as_view(), name="client_count"),

    path("vendors_management/",VendorManagementListCreate.as_view(), name="client_management_list_create",),
    path("vendors_management/<int:pk>/",VendorManagementDetail.as_view(),name="client_management_detail",),

    path("kyc_my_services/",KycMyServicesListCreate.as_view(), name="kyc_my_services_list"),
    path("kyc_my_services/<int:pk>/", KycMyServicesDetail.as_view(), name="kyc_my_services_detail"),
    
    path("kyc_client_services/", KycClientServicesListCreate.as_view(), name="kyc_client_services_list"),
    path("kyc_client_services/<int:pk>/", KycClientServicesDetail.as_view(), name="kyc_client_services_detail"),

    path("vendor_priority/", KycVendorPriorityListCreate.as_view(), name="vendor_priority_list_create"),
    path("vendor_priority/<int:pk>/", KycVendorPriorityDetail.as_view(), name="vendor_priority_detail"),

    #uat
    # path("vendor_active_count/", VendorAllCount.as_view(), name="Vendor_all_count"),
    path("vendors_api_list/", VendorApiList.as_view(), name="vendor_api_list"),
    path("api_management/", ApiManagementListCreate.as_view(), name="api_list_create"),
    path("api_management/<int:pk>/", ApiManagementDetail.as_view(), name="api_detail"),
    path("end_point_list/", ApiManagementList.as_view(), name="api_list"),
    # path("uat_pan-details/", PanUatDetailsAPIView.as_view(), name="pan-details"),


    path("uat_pan_details/", UatPanDetailsAPIView.as_view(), name="uat_pan_details"),
    path("uat_bill_details/", UatBillDetailsAPIView.as_view(), name="uat_bill_details"),
    path("uat_name_details/", NameMatchUatAPIView.as_view(), name="uat_name_details"),
    path("uat_voter_details/", UatVoterDetailsAPIView.as_view(), name="uat_voter_details"),
    path("uat_rc_details/", RcUatAPIView.as_view(), name="uat_rc_details"),
    path("uat_driving_license_details/", UatDrivingLicenseAPIView.as_view(), name="uat_driving_license_details"),

    #production
    path("prod_bill_details/", ProBillDetailsAPIView.as_view(), name="prod_bill_details"),
    path("prod_pan_details/", ProPanDetailsAPIView.as_view(), name="prod_pan_details"),
    path("prod_name_details/", ProNameMatchAPIView.as_view(), name="prod_name_details"),
    path("prod_voter_details/", ProVoterDetailsAPIView.as_view(), name="prod_voter_details"),
    path("prod_rc_details/", ProRcAPIView.as_view(), name="prod_rc_details"),
    path("prod_driving_license_details/", ProDrivingLicenseAPIView.as_view(), name="prod_driving_license_details"),

]