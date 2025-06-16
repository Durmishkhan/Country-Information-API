import requests
import time
from django.core.management.base import BaseCommand
from expapp.models import Country

class Command(BaseCommand):
    help = 'Synchronizes country data from REST Countries API'

    def handle(self, *args, **kwargs):
        # Specify required fields to avoid 'fields' query error
        fields = 'name,capital,population,area,languages,region,subregion,currencies'
        url = f'https://restcountries.com/v3.1/all?fields={fields}'
        try:
            self.stdout.write(self.style.NOTICE(f'Fetching data from {url}...'))
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            countries = response.json()

            for country in countries:
                try:
                    # Extract required fields with defaults
                    name_common = country.get('name', {}).get('common', '')
                    name_official = country.get('name', {}).get('official', '')
                    capital = country.get('capital', [])
                    population = country.get('population', 0)
                    area = country.get('area', 0.0)
                    languages = country.get('languages', {})
                    region = country.get('region', '')
                    subregion = country.get('subregion', '')
                    currencies = country.get('currencies', {})

                    # Update or create country
                    Country.objects.update_or_create(
                        name_common=name_common,
                        defaults={
                            'name_official': name_official,
                            'capital': capital,
                            'population': population,
                            'area': area,
                            'languages': languages,
                            'region': region,
                            'subregion': subregion,
                            'currencies': currencies,
                        }
                    )
                    self.stdout.write(self.style.SUCCESS(f'Successfully synced {name_common}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error syncing : {str(e)}'))
                time.sleep(0.5)  # Avoid overwhelming the API
            self.stdout.write(self.style.SUCCESS('Sync completed successfully'))
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Failed to fetch data: {str(e)}'))