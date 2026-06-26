"""Menu CRUD business logic for restaurant owners."""

from restaurant.models import FoodItem


def create_menu_item(restaurant, data, image=None):
    item = FoodItem(restaurant=restaurant, **data)
    if image:
        item.image = image
    item.save()
    return item


def update_menu_item(item, data, image=None):
    for key, value in data.items():
        setattr(item, key, value)
    if image:
        item.image = image
    item.save()
    return item


def delete_menu_item(item):
    item.delete()
