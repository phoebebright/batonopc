

#from registration.backends.simple.views import RegistrationView
#from web.forms import CustomUserForm


from django.urls import register_converter
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic.base import TemplateView

admin.autodiscover()


#NOTE: urls are organised in these groups to make it easy to test them in test_urls.py
urlpatterns = [
    # these won't be tested

    # libraries etc.
    #path("stripe/", include("djstripe.urls", namespace="djstripe")),
    path('admin/doc/',include('django.contrib.admindocs.urls')),
    # path('apidocs/', include_docs_urls(title='Skorie API', public=False)),
    # path('helpdesk/', include('helpdesk.urls', namespace='helpdesk')),


    path('admin/', admin.site.urls),



    # path('signinup/', signinup, name='signinup'),
    path('account/', include('django.contrib.auth.urls')),


]
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#     urlpatterns += static(settings.ASSETS_URL, document_root=settings.ASSETS_ROOT)
#     urlpatterns += static(settings.EVENT_URL, document_root=settings.EVENT_ROOT)
#     # urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]
#     # import debug_toolbar
#     #
#     # urlpatterns = [
#     #                   path('__debug__/', include(debug_toolbar.urls)),
#     #               ] + urlpatterns
#     #
