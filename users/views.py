from django.shortcuts import render
from django.http import JsonResponse


def simple_json_view_users(request):
    data = {
        'message': 'Hello, USER PAGE',
        'status': 'success'
    }
    return JsonResponse(data)
