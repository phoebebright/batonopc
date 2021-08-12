from django.conf import settings

from django.urls import register_converter
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic.base import TemplateView
from rest_framework import routers

from web.api import ReadingViewset
from web.views import Landing
from gadgetdb.api import GadgetViewSet

admin.autodiscover()

router = routers.DefaultRouter()
router_ro = routers.DefaultRouter()  # readonly apis
router_enter = routers.DefaultRouter()   # related to entry and review of entries

router.register(r'reading', ReadingViewset)
router.register(r'gadget', GadgetViewSet)



#NOTE: urls are organised in these groups to make it easy to test them in test_urls.py
urlpatterns = [
    path('api/v1/', include(router.urls)),

    path('admin/doc/',include('django.contrib.admindocs.urls')),



    path('admin/', admin.site.urls),



    # path('signinup/', signinup, name='signinup'),
    path('account/', include('django.contrib.auth.urls')),
    path('', Landing.as_view(), name='home'),



]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
