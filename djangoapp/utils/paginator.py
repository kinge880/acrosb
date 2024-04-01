from django.conf import settings
from rest_framework import pagination
from rest_framework.response import Response
from rest_framework.utils.urls import remove_query_param, replace_query_param

class YourPagination(pagination.PageNumberPagination):
    
    def get_paginated_response(self, data):
        return Response({
            'links': {
               'next': self.get_next_link(),
               'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'actual_pages': self.page.number,
            'results': data
        })

class YourPaginationLimit(pagination.LimitOffsetPagination):
    
    def get_paginated_response(self, data):
        return Response({
            'links': {
               'next': self.get_next_link(),
               'previous': self.get_previous_link()
            },
            'count': self.count,
            'results': data
        })

class CustomPagination(pagination.PageNumberPagination):
    page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'links': {
               'next': self.get_next_link(),
               'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'actual_pages': self.page.number,
            'results': data
        })
        