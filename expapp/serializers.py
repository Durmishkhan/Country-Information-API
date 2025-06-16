from rest_framework import serializers
from .models import Country

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = [
            'id', 'name_common', 'name_official', 'capital', 'population',
            'area', 'languages', 'region', 'subregion', 'currencies',
            'created_at', 'updated_at'
        ]