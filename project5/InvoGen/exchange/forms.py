from .models import Item, ItemCategory, ItemBrand, SerializedItem,\
NonSerializedItemPurchaseList, Supplier, Customer, Inventory, Purchase, Sale,\
NonSerializedItemSaleList, PurchaseOtherCost, SaleOtherCost

from django.forms import ModelForm, modelformset_factory, BaseModelFormSet
from django import forms
from django.utils.translation import gettext_lazy as _

class SupplierForm(ModelForm):
    class Meta:
        model = Supplier
        fields = ["name", "address", "phone", "email", "notes"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.TextInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control"})
        }

class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = ["name", "address", "phone", "email", "notes"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.TextInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control"})
        }

class ItemCategoryForm(ModelForm):
    class Meta:
        model = ItemCategory
        fields = ["category", "abbreviation"]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].widget.attrs.update({"class": "form-control"})
        self.fields["abbreviation"].widget.attrs.update({"class": "form-control"})

class ItemBrandForm(ModelForm):
    class Meta:
        model = ItemBrand
        fields = ["brand", "abbreviation"]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["brand"].widget.attrs.update({"class": "form-control"})
        self.fields["abbreviation"].widget.attrs.update({"class": "form-control"})
    
class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ["item_category", "item_brand", "name", "description", "SKU", "inventory_restock_warning"]
        
    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["item_category"].widget.attrs.update({"class": "form-select"})
        self.fields["item_category"].queryset = ItemCategory.objects.filter(user=user)
        self.fields["item_brand"].widget.attrs.update({"class": "form-select"})
        self.fields["item_brand"].queryset = ItemBrand.objects.filter(user=user)
        self.fields["name"].widget.attrs.update({"class": "form-control"})
        self.fields["description"].widget.attrs.update({"class": "form-control"})
        self.fields["SKU"].widget.attrs.update({"class": "form-control"})
        self.fields["inventory_restock_warning"].widget.attrs.update({"class": "form-control"})

class PurchaseForm(ModelForm):
    class Meta:
        model = Purchase
        fields = ["supplier", "date", "notes"]
        widgets = {
            "date": forms.TextInput(attrs={"type": "date", "class": "form-control"})
        }
        
    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["supplier"].widget.attrs.update({"class": "form-select"})
        self.fields["supplier"].queryset = Supplier.objects.filter(user=user)
        self.fields["notes"].widget.attrs.update({"class": "form-control"})

class SaleForm(ModelForm):
    class Meta:
        model = Sale
        fields = ["customer", "date", "notes"]
        widgets = {
            "date": forms.TextInput(attrs={"type": "date", "class": "form-control"})
        }
        
    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["customer"].widget.attrs.update({"class": "form-select"})
        self.fields["customer"].queryset = Customer.objects.filter(user=user)
        self.fields["notes"].widget.attrs.update({"class": "form-control"})


class SerializedForm(ModelForm):
    class Meta:
        model = SerializedItem
        fields=["item", "status", "unit_purchase_price", "unique_id_type", "unique_id"]
        
        labels = {
            "unit_purchase_price": _("Unit Cost($)"),
        }



class NonSerializedPurchaseForm(ModelForm):
    class Meta:
        model = NonSerializedItemPurchaseList
        fields = ["item", "count", "unit_price"]
        
        labels = {
            "unit_price": _("Unit Cost($)"),
        }
    

class NonSerializedSaleForm(ModelForm):
    class Meta:
        model = NonSerializedItemSaleList
        fields = ["item", "count", "unit_price"]

        labels = {
            "unit_price": _("Unit Price($)"),
        }

class PurchaseOtherCostForm(ModelForm):
    class Meta:
        model = PurchaseOtherCost
        fields = ["cost_type", "cost"]

        labels = {
            "cost": _("Cost($):")
        }

class SaleOtherCostForm(ModelForm):
    class Meta:
        model = SaleOtherCost
        fields = ["cost_type", "cost"]

        labels = {
            "cost": _("Cost($):")
        }



