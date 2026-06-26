from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from restaurant.selectors.dashboard import get_restaurant_for_user


def restaurant_owner_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        restaurant = get_restaurant_for_user(request.user)
        if not restaurant:
            messages.error(
                request,
                "No restaurant linked to your account. Complete partner registration first.",
            )
            return redirect("partners:partner_registration")
        request.restaurant = restaurant
        return view_func(request, *args, **kwargs)

    return wrapper
