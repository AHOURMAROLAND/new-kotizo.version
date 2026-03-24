import time
import logging

logger = logging.getLogger('kotizo')

class RequestTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        duration = round((time.time() - start) * 1000, 2)
        if not request.path.startswith('/django-admin'):
            logger.info({
                'action': 'http_request',
                'method': request.method,
                'path': request.path,
                'status': response.status_code,
                'duration_ms': duration,
            })
        return response