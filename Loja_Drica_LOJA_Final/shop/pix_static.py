"""BR Code Pix estático: dados da chave e valor correto do pedido.
Não consulta o banco do recebedor e NUNCA confirma pagamento automaticamente.
"""
import base64
from decimal import Decimal
from io import BytesIO
import re
import unicodedata

import qrcode


def _tlv(identifier, value):
    value = str(value)
    length = len(value.encode('utf-8'))
    if length > 99:
        raise ValueError('Campo Pix excedeu o tamanho máximo')
    return f'{identifier}{length:02d}{value}'


def _clean(text, limit):
    ascii_text = unicodedata.normalize('NFKD', text).encode('ascii','ignore').decode().upper()
    return re.sub(r'[^A-Z0-9 .-]', '', ascii_text).strip()[:limit]


def _crc16(payload):
    crc = 0xFFFF
    for b in payload.encode('utf-8'):
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return f'{crc:04X}'


def create_static_pix(key, amount, order_id, merchant_name, city):
    """Chave Pix já cadastrada pelo recebedor. Retorna (copia-cola, qr_png_base64)."""
    key = key.strip()
    if not key or len(key) > 77:
        raise ValueError('Configure uma chave Pix válida no arquivo privado')
    amount = Decimal(str(amount)).quantize(Decimal('.01'))
    if amount <= 0 or amount > Decimal('9999999999.99'):
        raise ValueError('Valor de pagamento inválido')
    name = _clean(merchant_name,25)
    city = _clean(city,15)
    if not name or not city:
        raise ValueError('Configure nome e cidade do recebedor')
    txid = re.sub(r'[^A-Za-z0-9]', '', str(order_id))[:25].upper()
    if not txid:raise ValueError('Identificador do pedido inválido')
    merchant_account = _tlv('00','br.gov.bcb.pix') + _tlv('01',key)
    payload = ( _tlv('00','01') + _tlv('26',merchant_account)
        + _tlv('52','0000') + _tlv('53','986') + _tlv('54',f'{amount:.2f}')
        + _tlv('58','BR') + _tlv('59',name) + _tlv('60',city)
        + _tlv('62',_tlv('05',txid)) + '6304' )
    payload += _crc16(payload)
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,box_size=6,border=4)
    qr.add_data(payload)
    qr.make(fit=True)
    out=BytesIO()
    qr.make_image(fill_color='black',back_color='white').save(out,format='PNG')
    return payload, base64.b64encode(out.getvalue()).decode('ascii')
