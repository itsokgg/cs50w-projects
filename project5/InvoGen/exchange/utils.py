from .models import Inventory, SerializedItem, Item

from django.utils import timezone
from django.core.exceptions import FieldError   

def count_inventory(user, inventories="all"):
    if inventories == "all":
        inventories = Inventory.objects.filter(user=user, active_until=None).order_by("item")

    nsi = {}
    for inventory in inventories:
        
        if nsi.get(str(inventory.item.SKU)):
            nsi[str(inventory.item.SKU)] += inventory.count
        else:
            nsi[str(inventory.item.SKU)] = inventory.count
    return nsi


def get_restock_warning(user):
    nsi = count_inventory(user)
    si = SerializedItem.objects.filter(user=user, status="INV").order_by("item")
    items = Item.objects.filter(user=user)
    for item in items:
        if not nsi.get(str(item.SKU)):
            nsi[str(item.SKU)] = 0
        
    for item in si:
        if nsi.get(str(item.item.SKU)):
            nsi[str(item.item.SKU)] += 1
        else:
            nsi[str(item.item.SKU)] = 1
    
    total_inventory = nsi
    warnings = []
    for sku, count in total_inventory.items():
        item = Item.objects.get(user=user, SKU=sku)
        if count <= item.inventory_restock_warning:
            warnings.append({"sku": sku, "count": count, "restock_warning": item.inventory_restock_warning})
    
    return warnings


def remove_from_inventory(user, item, count, sale_price):
    
    # sort by oldest first
    current_inventories = Inventory.objects.filter(item=item, active_until=None).order_by("date_time")
    
    count_left = count
    # inventories to set active_until_date
    inventories_deactivating = []

    for inventory in current_inventories:
        inventory_count = inventory.count
        # always deactivate inventory if loop reaches it
        inventories_deactivating.append(inventory)

        if count_left > inventory_count:
            count_left = count_left - inventory_count
            inventory.count_sold = inventory_count
        
        #elif count_left <= inventory_count:
        else:
            inventory.count_sold = count_left
            remainder = inventory_count - count_left
            # make new inventory even if there are no items left from last one
            new_inventory = Inventory(
                user=user,
                item=item,
                count=remainder,
                purchase_cost = inventory.purchase_cost,
                nsi_purchase_l = inventory.nsi_purchase_l
            )
            new_inventory.clean()
            new_inventory.save()
            count_left = 0
            # break out of the for loop
            break 

    if count_left != 0:
        raise ValueError(f"You only have {count - count_left} of {item} in non-serialized inventory, not {count}")

    # deactivate inventories
    for inv in inventories_deactivating:
        inv.active_until = timezone.now()
        inv.sale_price = sale_price
        inv.save()

    # return inventories to add nsi_sale_l
    return inventories_deactivating

                                        