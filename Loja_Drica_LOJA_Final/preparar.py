# -*- coding: utf-8 -*-
"""Prepara a aplicação local sem colocar segredos em pacotes públicos."""
import os
import secrets
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHARED = Path.home() / 'HyperFemmeCompartilhado'
ENVFILE = SHARED / '.env'
MEDIA = SHARED / 'media'
OLD = Path.home() / 'Downloads' / 'hyper_store_codigo_fonte' / 'hyper_store'


def ensure_env():
    SHARED.mkdir(parents=True, exist_ok=True)
    MEDIA.mkdir(parents=True, exist_ok=True)
    if not ENVFILE.exists():
        original = OLD / '.env'
        if original.is_file():
            shutil.copy2(original, ENVFILE)
            print('Configuracao privada importada da Hyper Store antiga.')
        else:
            example = [
                'DEBUG=true',
                'SECRET_KEY=' + secrets.token_urlsafe(48),
                'DATABASE_URL=postgresql://postgres:COLOQUE_SUA_SENHA_CODIFICADA@127.0.0.1:5432/hyper',
                'ALLOWED_HOSTS=127.0.0.1,localhost',
                'CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000,http://127.0.0.1:8001,http://localhost:8001',
                'PUBLIC_BASE_URL=http://127.0.0.1:8000',
                'STOREFRONT_URL=http://127.0.0.1:8000/',
                'SECURE_SSL_REDIRECT=false',
                'ENABLE_HSTS=false',
                'MP_ACCESS_TOKEN=',
                'MP_WEBHOOK_SECRET=',
                'PIX_PAYMENT_MODE=manual_key',
                'PIX_KEY=+5511971992138',
                'PIX_RECEIVER_NAME=LOJA DRICA',
                'PIX_RECEIVER_CITY=SAO PAULO',
            ]
            ENVFILE.write_text('\n'.join(example)+'\n', encoding='utf-8')
            print('Configuracao privada criada para preenchimento manual.')
    # Acrescenta / corrige APENAS os ajustes de localhost e a chave ausente.
    content = ENVFILE.read_text(encoding='utf-8-sig')
    if 'SECRET_KEY=' in content and not any(x.strip().startswith('SECRET_KEY=') for x in content.splitlines()):
        content = content.replace('falseSECRET_KEY=', 'false\nSECRET_KEY=')
    values = {
        'DEBUG': 'true',
        'ALLOWED_HOSTS': '127.0.0.1,localhost',
        'CSRF_TRUSTED_ORIGINS': 'http://127.0.0.1:8000,http://localhost:8000,http://127.0.0.1:8001,http://localhost:8001',
        'PUBLIC_BASE_URL': 'http://127.0.0.1:8000',
        'STOREFRONT_URL': 'http://127.0.0.1:8000/',
        'SECURE_SSL_REDIRECT': 'false',
        'ENABLE_HSTS': 'false',
    }
    for key,value in values.items():
        pattern = r'(?m)^' + re_escape(key) + r'=.*$'
        import re
        if re.search(pattern, content):
            content = re.sub(pattern, lambda _: key+'='+value, content)
        else:
            content = content.rstrip()+'\n'+key+'='+value+'\n'
    if not any(x.startswith('SECRET_KEY=') and x[11:].strip() for x in content.splitlines()):
        content = content.rstrip()+'\nSECRET_KEY='+secrets.token_urlsafe(48)+'\n'
    ENVFILE.write_text(content.rstrip()+'\n', encoding='utf-8')
    # Mantem fotos previamente cadastradas (nunca sobrescreve arquivos compartilhados).
    oldmedia = OLD / 'media'
    if oldmedia.is_dir():
        count = 0
        for source in oldmedia.rglob('*'):
            if not source.is_file():
                continue
            dest = MEDIA / source.relative_to(oldmedia)
            if not dest.exists():
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, dest)
                count += 1
        if count:
            print('Fotos antigas preservadas na pasta compartilhada:', count)
    if any(x in content for x in ['COLOQUE_SUA_SENHA_CODIFICADA','SUA_SENHA','@HOST:']):
        print('\nFALTA configurar DATABASE_URL no arquivo privado:')
        print('  '+str(ENVFILE))
        print('Use a senha real do PostgreSQL, mas nao envie fotos desse arquivo.')
        return False
    return True


def re_escape(text):
    import re
    return re.escape(text)


def run(command, env=None):
    return subprocess.call([str(c) for c in command], cwd=HERE, env=env)


def main():
    print('LOJA DRICA | Configuracao local (PostgreSQL compartilhado)')
    print('Dados privados: '+str(SHARED))
    if not ensure_env():
        return 2
    exe = HERE / '.venv' / 'Scripts' / 'python.exe'
    if not exe.exists():
        if run([sys.executable, '-m', 'venv', HERE/'.venv']):
            print('Falha ao criar o ambiente .venv')
            return 1
    if run([exe, '-m', 'pip', 'install', '-r', 'requirements.txt']):
        print('Falha ao instalar os pacotes. Verifique sua internet.')
        return 1
    env = os.environ.copy()
    env['HYPER_SITE_MODE'] = 'store' if APP_TIPO == 'LOJA' else 'panel'
    if run([exe, 'manage.py', 'check'], env):
        print('Falha na verificacao do Django.')
        return 1
    if run([exe, 'manage.py', 'migrate', '--noinput'], env):
        print('Falha nas migracoes. Nao apague o PostgreSQL.')
        return 1
    print('\nINSTALACAO CONFIGURADA. Abra 02_INICIAR_'+APP_TIPO+'.bat')
    if APP_TIPO == 'PAINEL':
        print('Se nao existir administrador, use:')
        print(r'  .\.venv\Scripts\python.exe manage.py createsuperuser')
    return 0


if __name__ == '__main__':
    APP_TIPO = 'LOJA'
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('Operacao interrompida.')
        sys.exit(1)
