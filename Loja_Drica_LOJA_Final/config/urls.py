"""URLConf exclusiva da loja pública. Nenhuma rota do painel é publicada."""
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from shop import public_api

urlpatterns = [
    path('api/v1/store/', public_api.public_config, name='api-public-store'),
    path('api/v1/products/', public_api.public_catalog, name='api-public-products'),
    path('api/v1/categories/', public_api.public_collections, name='api-public-categories'),
    path('api/v1/campaigns/', public_api.public_campaigns, name='api-public-campaigns'),
    path('', include('shop.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
