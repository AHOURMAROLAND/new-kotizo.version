from rest_framework.pagination import CursorPagination

class KotizoCursorPagination(CursorPagination):
    page_size = 20
    ordering = '-date_creation'
    cursor_query_param = 'cursor'