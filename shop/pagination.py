from math import ceil
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class ExpressLikePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "limit"
    page_query_param = "page"

    def get_paginated_response(self, data):
        page = self.page.number
        limit = self.get_page_size(self.request)
        total = self.page.paginator.count
        return Response({
            "page": page,
            "limit": limit,
            "totalPages": ceil(total / limit) if limit else 1,
            "totalItems": total,
            "products": data,
        })