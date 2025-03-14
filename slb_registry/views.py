"""

"""
# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views import View
from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic import ListView
from device_inventory.models import DeviceInfo
from slb_registry.models import HealthCheckInfo, BackendInfo, FrontendInfo
from rich import print

from .forms import SlbCreateForm, SlbDisplayForm, BackendInfoFormSet

# class MyView(View):
#     def get(self, request, *args, **kwargs):
#         return HttpResponse("Hello, World!")

# class SlbIndexView(TemplateView):
#     template_name = "slb_vips_page.html"

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['vip_list'] = SlbVIP.objects.all()
#         return context


class SlbIndexView(ListView):
    template_name = "slb_vips_listpage.html"

    paginate_by = 15
    model = FrontendInfo
    context_object_name = "vip_list"
    ordering = ["frontend_handle"]

    # @meta
    # def get_queryset(self, **kwargs):


    def get_queryset(self, **kwargs):
        return FrontendInfo.objects.values(
            "frontend_handle",
            "listener_address",
            "address_type",
            "port",
            "protocol",
            "app_inventory_slug",
            "device_fqdn",
            "datacenter",
            "security_zone"
        ).order_by("frontend_handle")


class SlbDetailsView(TemplateView):
    template_name = "slb_vip_detail.html"

    def get_context_data(self, **kwargs):

        handle = kwargs["handle"]
        vip_info = FrontendInfo.objects.filter(frontend_handle=handle).values().first()

        device_info = DeviceInfo.objects.filter(device_fqdn=vip_info["device_fqdn_id"]).values().first()

        if vip_info["backend_handle_id"] is not None:
            pool_info = (
                BackendInfo.objects.filter(backend_handle=vip_info["backend_handle_id"]).values().first()
            )
            pool_info.update({"backend_handle": vip_info["backend_handle_id"]})
            print(pool_info)

            if pool_info["healthcheck_handle_id"] is not None:
                healthcheck_info = HealthCheckInfo.objects.filter(healthcheck_handle=pool_info["healthcheck_handle_id"]).values().first()
                pool_info.update({"healthcheck_handle": healthcheck_info})
        
        
        return {"vip_info": vip_info, "pool_info": pool_info, 'device_info': device_info, "healthcheck_info": healthcheck_info}



def create_slb(request):

    if request.method == "POST":
        form = SlbCreateForm(request.POST)
        backend_formset = BackendInfoFormSet(request.POST)
        #print(form)
        print(backend_formset)
        if form.is_valid() and backend_formset.is_valid():
            form_data = form.cleaned_data

            backend_data = []
            for backend_form in backend_formset:
                if backend_form.cleaned_data and not backend_form.cleaned_data.get('DELETE', False):
                    backend_data.append(backend_form.cleaned_data)


            print(form_data)
            print(backend_data)
            return HttpResponseRedirect("/slb")
        else:
            # Return form errors
            errors = {
                'form_errors': form.errors,
                'backend_errors': backend_formset.errors
            }
            return JsonResponse({
                'success': False,
                'errors': errors
            })

    else:
        form = SlbCreateForm()
        backend_formset = BackendInfoFormSet()

    return render(request, "slb_create.html", { "form": form, 'backend_formset': backend_formset } )












