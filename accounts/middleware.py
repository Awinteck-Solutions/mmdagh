from django.shortcuts import redirect
from .models import UserAssignment
import logging
from django.shortcuts import redirect
from django.urls import reverse


logger = logging.getLogger(__name__)

# middleware.py

class RegionMMDAMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                # Ensure the user has an associated region
                user_assignment = UserAssignment.objects.get(user=request.user)
                request.region = user_assignment.region
            except UserAssignment.DoesNotExist:
                request.region = None
        else:
            request.region = None

        return self.get_response(request)
