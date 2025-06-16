from rest_framework import generics
from django.core.cache import cache
from rest_framework.response import Response
from .models import Country
from .serializers import CountrySerializer

class CountryList(generics.ListAPIView):
    serializer_class = CountrySerializer

    def list(self, request, *args, **kwargs):
        cache_key = 'country_list'
        data = cache.get(cache_key)

        if data is None:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            cache.set(cache_key, data, timeout=60*5)

        return Response(data)
    


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
