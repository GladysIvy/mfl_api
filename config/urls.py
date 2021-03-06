from django.conf.urls import url, patterns, include
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from common.views import APIRoot, root_redirect_view


apipatterns = patterns(
    '',
    url(r'^$', login_required(
        cache_page(60*60)(APIRoot.as_view())), name='root_listing'),
    url(r'^explore/', include('rest_framework_swagger.urls',
        namespace='swagger')),
    url(r'^common/', include('common.urls', namespace='common')),
    url(r'^users/', include('users.urls', namespace='users')),
    url(r'^facilities/', include('facilities.urls', namespace='facilities')),
    url(r'^chul/', include('chul.urls', namespace='chul')),
    url(r'^gis/', include('mfl_gis.urls', namespace='mfl_gis')),
    url(r'^rest-auth/', include('rest_auth.urls', namespace='rest_auth')),
    url(r'^rest-auth/registration/', include('rest_auth.registration.urls',
        namespace='rest_auth_registration'))
)

urlpatterns = patterns(
    '',
    url(r'^$', root_redirect_view, name='root_redirect'),
    url(r'^api/', include(apipatterns, namespace='api')),
    url(r'^accounts/',
        include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/token/', 'rest_framework.authtoken.views.obtain_auth_token'),
    url(r'^o/', include('oauth2_provider.urls')),
)
