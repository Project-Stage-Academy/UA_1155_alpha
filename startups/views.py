from django.http import JsonResponse


def simple_json_view(request):
    data = {
        'message': 'Hello, STARTUP PAGE',
        'status': 'success'
    }
    return JsonResponse(data)
