import hashlib
import requests
import logging
from django.conf import settings

logger = logging.getLogger('kotizo')

PAYDUNYA_URLS = {
    'test': {
        'checkout': 'https://app.paydunya.com/sandbox-api/v1/checkout-invoice/create',
        'status': 'https://app.paydunya.com/sandbox-api/v1/checkout-invoice/confirm',
        'payout': 'https://app.paydunya.com/sandbox-api/v1/softpay/send-money',
        'tmoney': 'https://app.paydunya.com/sandbox-api/v1/softpay/t-money-togo',
    },
    'live': {
        'checkout': 'https://app.paydunya.com/api/v1/checkout-invoice/create',
        'status': 'https://app.paydunya.com/api/v1/checkout-invoice/confirm',
        'payout': 'https://app.paydunya.com/api/v1/softpay/send-money',
        'tmoney': 'https://app.paydunya.com/api/v1/softpay/t-money-togo',
    },
}

def get_headers():
    mode = settings.PAYDUNYA_MODE
    return {
        'Content-Type': 'application/json',
        'PAYDUNYA-MASTER-KEY': settings.PAYDUNYA_MASTER_KEY,
        'PAYDUNYA-PUBLIC-KEY': settings.PAYDUNYA_PUBLIC_KEY,
        'PAYDUNYA-PRIVATE-KEY': settings.PAYDUNYA_PRIVATE_KEY,
        'PAYDUNYA-TOKEN': settings.PAYDUNYA_TOKEN,
    }

def valider_hash_webhook(request):
    hash_recu = request.POST.get('data[hash]', '')
    hash_calcule = hashlib.sha512(
        settings.PAYDUNYA_MASTER_KEY.encode()
    ).hexdigest()
    return hash_recu == hash_calcule

def creer_invoice(montant, description, callback_url, cancel_url, reference):
    mode = settings.PAYDUNYA_MODE
    url = PAYDUNYA_URLS[mode]['checkout']
    payload = {
        'invoice': {
            'total_amount': int(montant),
            'description': description,
        },
        'store': {
            'name': 'Kotizo',
            'tagline': 'Cotisez Ensemble, Simplement',
            'postal_address': 'Lomé, Togo',
            'phone': '+22890000000',
            'return_url': callback_url,
            'cancel_url': cancel_url,
        },
        'custom_data': {
            'reference': reference,
        },
    }
    try:
        r = requests.post(url, json=payload, headers=get_headers(), timeout=15)
        data = r.json()
        if data.get('response_code') == '00':
            return {
                'success': True,
                'token': data.get('token'),
                'invoice_url': data.get('invoice_url'),
            }
        logger.error({'action': 'paydunya_invoice_echouee', 'response': data})
        return {'success': False, 'erreur': data.get('response_text', 'Erreur PayDunya')}
    except Exception as e:
        logger.error({'action': 'paydunya_invoice_exception', 'error': str(e)})
        return {'success': False, 'erreur': str(e)}

def effectuer_payout(montant, numero, operateur, description):
    mode = settings.PAYDUNYA_MODE
    if operateur == 'TMONEY_TOGO':
        url = PAYDUNYA_URLS[mode]['tmoney']
    else:
        url = PAYDUNYA_URLS[mode]['payout']
    payload = {
        'account_alias': numero,
        'amount': int(montant),
        'withdraw_mode': operateur,
        'description': description,
    }
    try:
        r = requests.post(url, json=payload, headers=get_headers(), timeout=15)
        data = r.json()
        if data.get('response_code') == '00':
            return {'success': True, 'reference': data.get('transaction_id')}
        logger.error({'action': 'paydunya_payout_echoue', 'response': data})
        return {'success': False, 'erreur': data.get('response_text', 'Erreur payout')}
    except Exception as e:
        logger.error({'action': 'paydunya_payout_exception', 'error': str(e)})
        return {'success': False, 'erreur': str(e)}
