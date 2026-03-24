from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger('kotizo')

def kotizo_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data = {
            'success': False,
            'erreur': response.data,
            'status_code': response.status_code,
        }
    else:
        logger.error({'action': 'unhandled_exception', 'error': str(exc)})
        response = Response(
            {'success': False, 'erreur': 'Erreur serveur inattendue'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    return response