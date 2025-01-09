from django.urls import path

#from inventory.views import MyView
from slb_registry.views import SlbIndexView, SlbDetailsView, create_slb

# urlpatterns = [
#     path("", MyView.as_view(), name="slb"),
# ]

urlpatterns = [
    path("create", create_slb, name="create_slb"),
    path("", SlbIndexView.as_view(), name="slb"),
    path("<str:handle>", SlbDetailsView.as_view(), name='slb_vip_detail')
]