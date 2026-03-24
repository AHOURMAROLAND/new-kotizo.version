import random
import string
import hashlib
import requests
import logging
from django.conf import settings

logger = logging.getLogger('kotizo')

def generer_code(prefix='', longueur=12):
    chars = string.ascii_uppercase + string.digits
    code = ''.join(random.choices(chars, k=longueur))
    return f"{prefix}{code}" if prefix else code

def calculer_frais_kotizo(montant):
    return round(float(montant) * settings.KOTIZO_FRAIS_PERCENT, 0)

def calculer_total_participant(montant):
    return round(float(montant) * (1 + settings.PAYDUNYA_PAYIN_PERCENT + settings.KOTIZO_FRAIS_PERCENT), 0)

def hash_numero_cni(numero):
    return hashlib.sha256(numero.strip().encode()).hexdigest()

def detecter_operateur(numero):
    if not numero:
        return None
    clean = numero.replace('+228', '').replace(' ', '')
    if len(clean) < 2:
        return None
    prefix = int(clean[:2])
    if prefix in range(90, 98):
        return 'MOOV_TOGO'
    elif prefix in [70, 71, 72, 79]:
        return 'MIXX_TOGO'
    elif prefix in [98, 99]:
        return 'TMONEY_TOGO'
    return None

def get_geo_from_ip(ip):
    try:
        if ip in ('127.0.0.1', 'localhost', '::1'):
            return None
        r = requests.get(
            f'http://ip-api.com/json/{ip}?lang=fr&fields=status,country,countryCode,city,lat,lon,timezone,isp',
            timeout=3
        )
        data = r.json()
        if data.get('status') == 'success':
            return {
                'pays': data.get('country', ''),
                'pays_code': data.get('countryCode', ''),
                'ville': data.get('city', ''),
                'latitude': data.get('lat'),
                'longitude': data.get('lon'),
                'timezone': data.get('timezone', ''),
                'isp': data.get('isp', ''),
            }
    except Exception as e:
        logger.warning({'action': 'geo_lookup_failed', 'error': str(e)})
    return None

def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')