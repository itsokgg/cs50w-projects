from django.contrib import admin

from .models import User, Item, ItemCategory, ItemBrand, SerializedItem,\
NonSerializedItemPurchaseList, Supplier, Customer, Inventory, Purchase, Sale,\
NonSerializedItemSaleList, SaleOtherCost, PurchaseOtherCost



admin.site.register(User)
admin.site.register(Item)
admin.site.register(ItemCategory)
admin.site.register(ItemBrand)
admin.site.register(SerializedItem)
admin.site.register(NonSerializedItemPurchaseList)
admin.site.register(Supplier)
admin.site.register(Customer)
admin.site.register(Inventory)
admin.site.register(Purchase)
admin.site.register(Sale)
admin.site.register(NonSerializedItemSaleList)
admin.site.register(SaleOtherCost)
admin.site.register(PurchaseOtherCost)