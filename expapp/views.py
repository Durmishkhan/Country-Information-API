from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.core.cache import cache
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
import hashlib
from .models import Country
from .serializers import CountrySerializer

class StandardPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class CountryList(generics.ListAPIView):
    serializer_class = CountrySerializer
    queryset = Country.objects.all()
    pagination_class = StandardPageNumberPagination

    def get_cache_key(self, request):
        query_params = request.query_params.copy()
        page = query_params.pop('page', [''])[0]
        page_size = query_params.pop('page_size', [''])[0]
        query_string = urlsafe_base64_encode(
            force_bytes(f"{sorted(query_params.items())}")
        )
        cache_key = f"country_list_{hashlib.md5(query_string.encode()).hexdigest()}_{page}_{page_size}"
        return cache_key

    def list(self, request, *args, **kwargs):
        cache_key = self.get_cache_key(request)
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(cached_data)
            return Response(cached_data)

        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                paginated_response = self.get_paginated_response(serializer.data)
                cache.set(cache_key, serializer.data, timeout=300)
                return paginated_response

            
            serializer = self.get_serializer(queryset, many=True)
            cache.set(cache_key, serializer.data, timeout=300)
            return Response(serializer.data)

        except Exception as e:
            
            print(f"Error in CountryList: {str(e)}")
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)


class CountryDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CountrySerializer
    queryset = Country.objects.all()

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        cache_key = f'country_detail_{pk}'
        data = cache.get(cache_key)

        if data is None:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            data = serializer.data
            cache.set(cache_key, data, timeout=60*10)

        return Response(data)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        pk = kwargs.get('pk')
        cache.delete(f'country_detail_{pk}')
        cache.delete('country_list')
        return response

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        cache.delete(f'country_detail_{pk}')
        cache.delete('country_list')
        return super().destroy(request, *args, **kwargs)
