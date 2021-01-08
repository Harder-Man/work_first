from django.views import View
from apps.areas.models import Area
from django.http.response import JsonResponse


class ProvinceView(View):
    def get(self, request):
        province = Area.objects.filter(parent=None)

        province_list = []
        for item in province:
            province_list.append({
                'id': item.id,
                'name': item.name
            })

        return JsonResponse({'code': 0, 'errmsg': 'ok', 'province_list': province_list})

