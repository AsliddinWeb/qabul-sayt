# apps/regions/views.py
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Region, District


def get_regions(request):
    """Barcha regionlarni qaytarish"""
    regions = Region.objects.all().values('id', 'name')
    return JsonResponse({
        'success': True,
        'regions': list(regions)
    })


def get_districts(request):
    """Region bo'yicha districtlarni qaytarish"""
    region_id = request.GET.get('region_id')

    if region_id:
        try:
            districts = District.objects.filter(region_id=region_id).values('id', 'name')
            return JsonResponse({
                'success': True,
                'districts': list(districts)
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    else:
        return JsonResponse({
            'success': False,
            'error': 'Region ID kiritilmagan'
        })


def get_region_with_districts(request, region_id):
    """Region va unga tegishli districtlarni qaytarish"""
    try:
        region = get_object_or_404(Region, id=region_id)
        districts = District.objects.filter(region=region).values('id', 'name')

        return JsonResponse({
            'success': True,
            'region': {
                'id': region.id,
                'name': region.name
            },
            'districts': list(districts)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })