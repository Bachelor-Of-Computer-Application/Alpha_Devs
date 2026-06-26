from django.shortcuts import redirect


def redirect_restaurant_detail(request, pk):
    return redirect('restaurant_detail', pk=pk)


def redirect_restaurants(request):
    return redirect('restaurants')
