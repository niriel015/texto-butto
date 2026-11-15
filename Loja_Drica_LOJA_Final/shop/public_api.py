"""API pública somente de leitura. Não expõe estoque reservado, dados pessoais ou pagamentos."""
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator
from .models import Advertisement, Banner, Category, Product, ShopSettings


def image_url(request, image):
    return request.build_absolute_uri(image.url) if image else None


def serialize_product(request, p):
    return {
        'id': p.pk, 'name': p.name, 'slug': p.slug, 'description': p.description,
        'category_id': p.category_id, 'category': p.category.name if p.category else None,
        'price': str(p.price), 'sale_price': str(p.sale_price) if p.sale_price is not None else None,
        'current_price': str(p.current_price), 'stock': p.stock, 'active': p.active,
        'image_url': image_url(request, p.image),
    }


def serialize_ad(request, ad):
    return {'id': ad.pk, 'title': ad.title, 'description': ad.description,
            'destination': ad.destination, 'button_text': ad.button_text,
            'placement': ad.placement, 'position': ad.position,
            'image_url': image_url(request, ad.image)}


def serialize_settings(request, conf):
    if not conf:
        return {'store_name':'Hyper Femme','primary_color':'#A25B7C','secondary_color':'#71385B',
                'background_color':'#FCFAF8','text_color':'#2D2230','announcement_enabled':True,
                'announcement_text':'SEU ESTILO, SUAS ESCOLHAS','animations_enabled':True,
                'headline':'Seu estilo. Suas regras. Sua essência.','headline_subtitle':'Descubra peças escolhidas para você.',
                'tagline':'BOUTIQUE FEMININA','footer_description':'','logo_url':None,'support_email':''}
    return {
        'store_name': conf.store_name, 'logo_url': image_url(request, conf.logo),
        'support_email': conf.support_email, 'primary_color': conf.primary_color,
        'secondary_color': conf.secondary_color, 'background_color': conf.background_color,
        'text_color': conf.text_color, 'announcement_enabled': conf.announcement_enabled,
        'announcement_text': conf.announcement_text, 'animations_enabled': conf.animations_enabled,
        'headline': conf.headline, 'headline_subtitle': conf.headline_subtitle,
        'tagline': conf.tagline, 'footer_description': conf.footer_description,
    }


@require_GET
@never_cache
def public_config(request):
    return JsonResponse({'ok': True, 'config': serialize_settings(request, ShopSettings.objects.first())})


@require_GET
@never_cache
def public_catalog(request):
    q = request.GET.get('q', '').strip()[:100]
    qs = Product.objects.filter(active=True).select_related('category').order_by('-created_at', '-id')
    if q:
        from django.db.models import Q
        qs = qs.filter(Q(name__icontains=q)|Q(description__icontains=q))
    try: page = max(1, int(request.GET.get('page', 1)))
    except (ValueError, TypeError): page = 1
    pager = Paginator(qs, 30)
    part = pager.get_page(page)
    return JsonResponse({'ok': True, 'total': pager.count, 'page': part.number,
                         'pages': pager.num_pages,
                         'results': [serialize_product(request, p) for p in part]})


@require_GET
@never_cache
def public_collections(request):
    categories = Category.objects.order_by('name')
    return JsonResponse({'ok': True, 'results': [{'id': c.pk, 'name': c.name, 'slug': c.slug}
                                                for c in categories]})


@require_GET
@never_cache
def public_campaigns(request):
    ads = list(Advertisement.published()[:30])
    banners = list(Banner.objects.filter(active=True).order_by('-id')[:30])
    return JsonResponse({'ok': True, 'advertisements': [serialize_ad(request, a) for a in ads],
                         'banners': [{'id': b.pk, 'title': b.title, 'subtitle': b.subtitle,
                                     'image_url': image_url(request, b.image)} for b in banners]})
