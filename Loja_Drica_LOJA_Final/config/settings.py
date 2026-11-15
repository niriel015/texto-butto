import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv
BASE_DIR=Path(__file__).resolve().parent.parent
# Arquivo privado comum aos dois downloads (loja e painel).
load_dotenv(Path.home()/'HyperFemmeCompartilhado'/'.env')
load_dotenv(BASE_DIR/'.env', override=False)
SECRET_KEY=os.getenv('SECRET_KEY','unsafe-local-only-change-before-deployment')
DEBUG=os.getenv('DEBUG','false').lower()=='true'
ALLOWED_HOSTS=[s.strip() for s in os.getenv('ALLOWED_HOSTS','localhost,127.0.0.1,testserver').split(',') if s.strip()]
CSRF_TRUSTED_ORIGINS=[s.strip() for s in os.getenv('CSRF_TRUSTED_ORIGINS','').split(',') if s.strip()]
INSTALLED_APPS=['django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','shop.apps.ShopConfig']
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','whitenoise.middleware.WhiteNoiseMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware']
HYPER_SITE_MODE='store'
if HYPER_SITE_MODE not in ('store','panel'):
 raise RuntimeError('HYPER_SITE_MODE deve ser store ou panel')
ROOT_URLCONF='config.urls'
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.debug','django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages','shop.context_processors.store_ui']}}]
WSGI_APPLICATION='config.wsgi.application'
DATABASES={'default':dj_database_url.config(default=os.getenv('DATABASE_URL','postgresql://hyper:hyper@localhost:5432/hyper'),conn_max_age=60,conn_health_checks=True)}
AUTH_PASSWORD_VALIDATORS=[{'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},{'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator'},{'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},{'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'}]
LANGUAGE_CODE='pt-br'; TIME_ZONE='America/Sao_Paulo'; USE_I18N=True; USE_TZ=True
STATIC_URL='/static/'; STATIC_ROOT=BASE_DIR/'staticfiles'; STATICFILES_STORAGE='whitenoise.storage.CompressedManifestStaticFilesStorage'
MEDIA_URL='/media/'; MEDIA_ROOT=Path(os.getenv('HYPER_SHARED_MEDIA_DIR', str(Path.home()/'HyperFemmeCompartilhado'/'media')))
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
LOGIN_URL='panel:login' if HYPER_SITE_MODE=='panel' else 'login'
LOGIN_REDIRECT_URL='panel:dashboard' if HYPER_SITE_MODE=='panel' else 'home'
LOGOUT_REDIRECT_URL=LOGIN_URL
SESSION_COOKIE_HTTPONLY=True; SESSION_COOKIE_SAMESITE='Lax'; CSRF_COOKIE_SAMESITE='Lax'
# Cookies separados mesmo usando 127.0.0.1:8000 e :8001, evitando sessões misturadas.
SESSION_COOKIE_NAME='hf_panel_session' if HYPER_SITE_MODE=='panel' else 'hf_store_session'
CSRF_COOKIE_NAME='hf_panel_csrf' if HYPER_SITE_MODE=='panel' else 'hf_store_csrf'
STOREFRONT_URL=os.getenv('STOREFRONT_URL','http://127.0.0.1:8000/').rstrip('/')+'/'
SECURE_CONTENT_TYPE_NOSNIFF=True; SECURE_REFERRER_POLICY='same-origin'; X_FRAME_OPTIONS='DENY'
if not DEBUG:
 SESSION_COOKIE_SECURE=True; CSRF_COOKIE_SECURE=True
 SECURE_SSL_REDIRECT=os.getenv('SECURE_SSL_REDIRECT','true').lower()=='true'
 SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO','https')
 SECURE_HSTS_SECONDS=31536000 if os.getenv('ENABLE_HSTS')=='true' else 0
MP_ACCESS_TOKEN=os.getenv('MP_ACCESS_TOKEN','')
MP_WEBHOOK_SECRET=os.getenv('MP_WEBHOOK_SECRET','')
PUBLIC_BASE_URL=os.getenv('PUBLIC_BASE_URL','').rstrip('/')
# Hospedagens com disco efêmero devem configurar storage S3 compatível.
if os.getenv('AWS_STORAGE_BUCKET_NAME'):
 INSTALLED_APPS+=['storages']
 STORAGES={'default':{'BACKEND':'storages.backends.s3.S3Storage'},'staticfiles':{'BACKEND':'whitenoise.storage.CompressedManifestStaticFilesStorage'}}
 AWS_QUERYSTRING_AUTH=False
 AWS_DEFAULT_ACL=None

# Pix direto: gera cobrança de valor exato, sem confirmação automática.
PIX_PAYMENT_MODE=os.getenv('PIX_PAYMENT_MODE','manual_key').strip().lower()
PIX_KEY=os.getenv('PIX_KEY','+5511971992138').strip()
PIX_RECEIVER_NAME=os.getenv('PIX_RECEIVER_NAME','LOJA DRICA').strip()
PIX_RECEIVER_CITY=os.getenv('PIX_RECEIVER_CITY','SAO PAULO').strip()
