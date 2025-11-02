import datetime

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
   pass

class Entity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=127, blank=False, null=False)
    address = models.CharField(max_length=127, blank=True)
    phone = models.CharField(max_length=127, blank=True)
    email = models.EmailField(blank=True)
    notes = models.TextField(blank=True, null=False)

    class Meta:
        abstract = True

class Supplier(Entity):
    def __str__(self):
        return f"{self.name}"

class Customer(Entity):
    def __str__(self):
        return f"{self.name}"

class ItemCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, blank=False, null=False)
    abbreviation = models.CharField(max_length=3, blank=False, null=False)

    def __str__(self):
        return f"{self.category} ({self.abbreviation})"

class ItemBrand(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    brand = models.CharField(max_length=20, blank=False, null=False)
    # generate abrv with js, used for sku generation
    abbreviation = models.CharField(max_length=3, blank=False, null=False)

    def __str__(self):
        return f"{self.brand} ({self.abbreviation})"

class Item(models.Model): #eg. iphone 16 pro white
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_category = models.ForeignKey(ItemCategory, on_delete=models.CASCADE, null=True, related_name="category_items")
    item_brand = models.ForeignKey(ItemBrand, on_delete=models.CASCADE, null=True, related_name="brand_items")
    name = models.CharField(max_length=127, blank=False, null=False)
    SKU = models.CharField(max_length=30, blank=False, null=False) #generate sku in views if user wants
    inventory_restock_warning = models.IntegerField(default=0)
    description = models.TextField(blank=True, null=False)

    def __str__(self):
        return f"{self.SKU}"
    class Meta:
        unique_together = [["user", "SKU"]]

class Purchase(models.Model): # user's purchase
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    date = models.DateField(default=datetime.date.today)
    notes = models.TextField(blank=True, null=False)

    def __str__(self):
        return f"Purchase from {self.supplier} on {self.date}"

class Sale(models.Model): # user's sale
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    date = models.DateField(default=datetime.date.today)
    notes = models.TextField(blank=True, null=False)

    def __str__(self):
        return f"Sale to {self.customer} on {self.date}"

class SerializedItem(models.Model): 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    STATUS_TYPES = [
        ("INV", "In Inventory"),
        ("SLD", "Sold"),
        ("MSN", "Missing")
    ] 
    status = models.CharField(max_length=3, blank=False, null=False, choices=STATUS_TYPES, default="INV")
    purchase = models.ForeignKey(Purchase, on_delete=models.SET_NULL, null=True) #link to purchase
    sale = models.ForeignKey(Sale, on_delete=models.SET_NULL, null=True, blank=True, default=None) # link to sale
    unit_purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    unit_sold_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=None)
    unique_id_type = models.CharField(max_length=50, blank=False, null=False) #eg. serial no
    unique_id = models.CharField(max_length=50, blank=False)    #eg. 123456789

    def __str__(self):
        return f"{self.item}-{self.unique_id}"
    
    

class ItemList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    item = models.ForeignKey(Item, on_delete=models.PROTECT, null=False)
    count = models.IntegerField(null=False)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=False)

    class Meta():
        abstract = True

class NonSerializedItemPurchaseList(ItemList):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, null=False, related_name="ns_item_list")
    
    def __str__(self):
        return f"{self.item} count: {self.count}; unit cost:{self.unit_price}"

class NonSerializedItemSaleList(ItemList):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, null=False, related_name="ns_item_list")


class OrderOtherCost(models.Model): #use for both Purchase and Sale
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    COST_TYPES = {
        ("TAX", "Tax"),
        ("SHP", "Shipping"),
        ("OTR", "Other Cost")
    }
    cost_type = models.CharField(max_length=3, blank=False, null=False, choices=COST_TYPES)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=False)

    class Meta():
        abstract = True

class PurchaseOtherCost(OrderOtherCost):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name="other_cost")    

class SaleOtherCost(OrderOtherCost):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="other_cost")

class Inventory(models.Model): #for non serialized
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_time = models.DateTimeField(default=timezone.now)
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name="inventory")
    count = models.PositiveIntegerField(default=0, null=False)
    purchase_cost = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    count_sold = models.PositiveIntegerField(null=True, blank=True)
    # to track profits
    nsi_purchase_l = models.ForeignKey(NonSerializedItemPurchaseList, on_delete=models.CASCADE, null=True, related_name="inventory")
    nsi_sale_l = models.ForeignKey(NonSerializedItemSaleList, on_delete=models.CASCADE, null=True, blank=True, related_name="inventory")
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    active_until = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.item} count: {self.count} remaining: {self.count - (self.count_sold or 0)}"
    