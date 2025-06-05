from django.contrib import admin
from .models import Country, Region, District


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'country')
    search_fields = ('name', 'country__name')
    list_filter = ('country',)
    ordering = ('country__name', 'name')


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'region', 'get_country')
    search_fields = ('name', 'region__name', 'region__country__name')
    list_filter = ('region__country', 'region')
    ordering = ('region__country__name', 'region__name', 'name')

    def get_country(self, obj):
        return obj.region.country.name
    get_country.short_description = 'Davlat'
