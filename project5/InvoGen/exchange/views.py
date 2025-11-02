import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.exceptions import ValidationError, FieldError
from django.db.utils import IntegrityError
from django.utils.datastructures import MultiValueDictKeyError
from django.forms import ModelForm, modelformset_factory
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import User, Item, SerializedItem, NonSerializedItemPurchaseList, Supplier, Customer,\
    Purchase, Sale, PurchaseOtherCost, NonSerializedItemSaleList, SaleOtherCost, Inventory,\
    PurchaseOtherCost, SaleOtherCost, ItemCategory, ItemBrand
from .forms import SupplierForm, CustomerForm, ItemForm, ItemCategoryForm, ItemBrandForm, PurchaseForm,\
    SerializedForm, NonSerializedPurchaseForm, SaleForm, NonSerializedSaleForm, PurchaseOtherCostForm, \
    SaleOtherCostForm
from .utils import remove_from_inventory, count_inventory, get_restock_warning

@login_required()
def index(request, item_id=None):
    if item_id:
        try:
            item = Item.objects.get(user=request.user, pk=item_id)
        except FieldError:
            return HttpBadRequestError(request, f"Item {item_id} wasnt made by you")

        serialized_items = SerializedItem.objects.filter(user=request.user, status="INV", item=item)
        nonserialized_inventories = Inventory.objects.filter(user=request.user, active_until=None, item=item)
    else:
        item = None
        serialized_items = SerializedItem.objects.filter(user=request.user, status="INV").order_by("item")
        nonserialized_inventories = "all"

    nsi = count_inventory(request.user, nonserialized_inventories)
    items = Item.objects.filter(user=request.user)
    restock_warnings = get_restock_warning(request.user)       
    return render(request, "exchange/index.html", {
        "restock_warnings": restock_warnings,
        "serialized_inventory": serialized_items,
        "nonserialized_inventory": nsi,
        "items": items,
        "item": item
    })

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.add_message(request, messages.SUCCESS, f"Successfully loged in as {username}")
            return HttpResponseRedirect(reverse("index"))
        else:
            messages.add_message(request, messages.WARNING, "Invalid username and/or password")
            return render(request, "exchange/login.html")
    
    return render(request, "exchange/login.html")

def logout_view(request):
    logout(request)
    messages.add_message(request, messages.SUCCESS, "Successfully logged out")
    return HttpResponseRedirect(reverse("login"))


def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if password != confirmation:
            return render(request, "exchange/register.html", {
                "message": "password does not match comfirmation."
            })
        
        try:
            user = User.objects.create_user(username, email, password )
            user.save()
        except IntegretyError:
            return render(request, "exchange/register.html", {
                "message": f"{username} already taken."
            })
        login(request, user)
        messages.add_message(request, messages.SUCCESS, f"Successfully registered and logged in as {username}")
        return HttpResponseRedirect(reverse("index"))
    
    return render(request, "exchange/register.html")

@login_required()
def new_supplier(request):
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            messages.add_message(request, messages.SUCCESS, f"Successfully created supplier: {instance}")
        else:
             return render(request, "exchange/new-supplier.html", {
                "form": form,
            })
        

    supplier_form = SupplierForm
    return render(request, "exchange/new-supplier.html", {
        "form": supplier_form
    })

@login_required()
def new_customer(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            messages.add_message(request, messages.SUCCESS, f"Successfully created customer: {instance}")
        else:
             return render(request, "exchange/new-customer.html", {
                "form": form
            })
        

    customer_form = CustomerForm
    return render(request, "exchange/new-customer.html", {
        "form": customer_form
    })

@login_required()
def new_item(request):
    if request.method == "POST":
        if request.POST.get("action") == "new-item":
            form = ItemForm(request.POST, user=request.user)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.user = request.user
                try:
                    instance.save()
                except IntegrityError:
                    messages.add_message(request, messages.WARNING, f"you already have an item with SKU:{instance.SKU}")
                messages.add_message(request, messages.SUCCESS, f"Successfully created new item: {instance}")
                return HttpResponseRedirect(reverse("view_item", kwargs={"sku": instance.SKU}))
            else:
                return render(request, "exchange/new-item.html", {
                    "item-form": form
                })
        elif request.POST.get("action") == "new-category":
            form = ItemCategoryForm(request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.user = request.user
                instance.save()
                messages.add_message(request, messages.SUCCESS, f"Successfully created item category: {instance}")
            else:
                return render(request, "exchange/new-item.html", {
                    "item_category_form": form
                })
        elif request.POST.get("action") == "new-brand":
            form = ItemBrandForm(request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.user = request.user
                instance.save()
                messages.add_message(request, messages.SUCCESS, f"Successfully created item brand: {instance}")
            else:
                return render(request, "exchange/new-item.html", {
                    "item_brand_form": form
                })
        
    
    item_form = ItemForm(user=request.user)
    item_category_form = ItemCategoryForm()
    item_brand_form = ItemBrandForm()
    return render(request, "exchange/new-item.html", {
        "item_form": item_form,
        "item_category_form": item_category_form,
        "item_brand_form": item_brand_form
    })

@login_required()
def new_purchase(request):
    if request.method == "POST":
        form = PurchaseForm(request.POST, prefix="form", user=request.user)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            messages.add_message(request, messages.SUCCESS, f"Successfully created purchase: {instance}")
            return HttpResponseRedirect(reverse("add_purchase_items", kwargs={"purchase_id": instance.id}))
        else:
            return render(request, "exchange/new-purchase.html", {
                "purchase_form": form,
            })
    purchase_form = PurchaseForm(prefix="form", user=request.user)
    return render(request, "exchange/new-purchase.html", {
        "purchase_form": purchase_form,
    })

@login_required()
def add_purchase_items(request, purchase_id):
    purchase = Purchase.objects.get(pk=purchase_id)
    class SerializedForm(ModelForm):
        class Meta:
            model = SerializedItem
            fields=["item", "status", "unit_purchase_price", "unique_id_type", "unique_id"]
            
            labels = {
                "unit_purchase_price": _("Unit Cost($)"),
            }
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields["item"].queryset = Item.objects.filter(user=request.user)
    
    class NonSerializedPurchaseForm(ModelForm):
        class Meta:
            model = NonSerializedItemPurchaseList
            fields = ["item", "count", "unit_price"]
            
            labels = {
                "unit_price": _("Unit Cost($)"),
            }        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields["item"].queryset = Item.objects.filter(user=request.user)

    SerializedFormset = modelformset_factory(
        SerializedItem,
        form=SerializedForm,
        
        fields=["item", "unit_purchase_price", "unique_id_type", "unique_id"],
        widgets={
            "item": forms.Select(attrs={"class": "form-select"}),
            "unit_purchase_price": forms.NumberInput(attrs={"class": "form-control"}),
            "unique_id_type": forms.TextInput(attrs={"class": "form-control"}),
            "unique_id": forms.TextInput(attrs={"class": "form-control"})   
        }   
    )
    NonSerializedFormset = modelformset_factory(
        NonSerializedItemPurchaseList,
        form=NonSerializedPurchaseForm,
        fields=["item", "count", "unit_price"],
        widgets={
            "item": forms.Select(attrs={"class": "form-select"}),
            "count": forms.TextInput(attrs={"class": "form-control"}),
            "unit_price": forms.NumberInput(attrs={"class": "form-control"})
        }
    )
    PurchaseOtherCostFormset = modelformset_factory(
        PurchaseOtherCost,
        form=PurchaseOtherCostForm,
        fields=["cost_type", "cost"],
        widgets={
            "cost_type": forms.Select(attrs={"class": "form-select"}),
            "cost": forms.NumberInput(attrs={"class": "form-control"})
        }
    )
    
    if request.method == "POST":
        serialized_formset = SerializedFormset(request.POST, prefix="formset1")
        nonserialized_formset = NonSerializedFormset(request.POST, prefix="formset2")
        other_cost_formset = PurchaseOtherCostFormset(request.POST, prefix="formset3")
        if serialized_formset.is_valid() and nonserialized_formset.is_valid() and other_cost_formset.is_valid():
            instances = serialized_formset.save(commit=False)
            for index, instance in enumerate(instances):
                instance.user = request.user
                instance.purchase = purchase
                instance.save()
                messages.add_message(request, messages.SUCCESS, "successfully saved serialized items")
                    
                if item_inputs := request.POST.getlist(f"item-{index + 1}-input"):
                    for unique_id in item_inputs:
                        serialized_item = SerializedItem(
                            user=request.user,
                            item=instance.item,
                            status="INV", 
                            purchase=instance.purchase,
                            sale=None,
                            unit_purchase_price=instance.unit_purchase_price,
                            unit_sold_price=None,
                            unique_id_type=instance.unique_id_type,
                            unique_id=unique_id
                        )
                        serialized_item.full_clean()
                        serialized_item.save()
                    

            # nonserialized formset save
            instances = nonserialized_formset.save(commit=False)
            for instance in instances:
                instance.user = request.user
                instance.purchase = purchase
                instance.save()
                messages.add_message(request, messages.SUCCESS, "successfully saved non serialized items")
                inventory = Inventory(
                    user=request.user,
                    item=instance.item, 
                    count=instance.count,
                    purchase_cost = instance.unit_price,
                    nsi_purchase_l = instance
                )
                
                inventory.full_clean()
                inventory.save()
                message = f"successfully updated inventory of {instance.item}"
                messages.add_message(request, messages.SUCCESS, message)
            
            # other cost formset save
            instances = other_cost_formset.save(commit=False)
            for instance in instances:
                instance.user = request.user
                instance.purchase = purchase
                instance.save()
    
            return HttpResponseRedirect(reverse("view_purchase", kwargs={"purchase_id": purchase_id}))

        # if formsets aren't valid
        else:
            return render(request, "exchange/add-purchase-items.html", {
                "purchase_id": purchase_id,
                "purchase": purchase,
                "formset1": serialized_formset,
                "formset2": nonserialized_formset,
                "formset3": other_cost_formset
            })

    
    return render(request, "exchange/add-purchase-items.html", {
        "purchase_id": purchase_id,
        "purchase": purchase,
        "formset1": SerializedFormset(queryset=SerializedItem.objects.none(), prefix="formset1"),
        "formset2": NonSerializedFormset(queryset=NonSerializedItemPurchaseList.objects.none(), prefix="formset2"),
        "formset3": PurchaseOtherCostFormset(queryset=PurchaseOtherCost.objects.none(), prefix="formset3")
    })

@login_required()
def new_sale(request):
    if request.method == "POST":
        form = SaleForm(request.POST, prefix="form", user=request.user)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            messages.add_message(request, messages.SUCCESS, f"Successfully created sale: {instance}")
            return HttpResponseRedirect(reverse("add_sale_items", kwargs={"sale_id": instance.id}))
        else:
            return render(request, "exchange/new-sale.html", {
                "sale_form": form,
            })
    sale_form = SaleForm(prefix="form", user=request.user)
    return render(request, "exchange/new-sale.html", {
        "sale_form": sale_form
    })


@login_required()
def add_sale_items(request, sale_id):
    sale = Sale.objects.get(pk=sale_id)
    items = SerializedItem.objects.filter(user=request.user, status="INV")
    class NonSerializedSaleForm(ModelForm):
        class Meta:
            model = NonSerializedItemSaleList
            fields = ["item", "count", "unit_price"]

            labels = {
                "unit_price": _("Unit Price($)"),
            }
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields["item"].queryset = Item.objects.filter(user=request.user)

    NonSerializedFormset = modelformset_factory(
        NonSerializedItemSaleList,
        form=NonSerializedSaleForm,
        fields=["item", "count", "unit_price"],
        widgets={
            "item": forms.Select(attrs={"class": "form-select"}),
            "count": forms.TextInput(attrs={"class": "form-control"}),
            "unit_price": forms.NumberInput(attrs={"class": "form-control"})
        }
    )
    SaleOtherCostFormset = modelformset_factory(
        SaleOtherCost,
        form=SaleOtherCostForm,
        fields=["cost_type", "cost"],
        widgets={
            "cost_type": forms.Select(attrs={"class": "form-select"}),
            "cost": forms.NumberInput(attrs={"class": "form-control"})
        }
    )
    
    if request.method == "POST":
        serialized_items = request.POST.getlist("serialized-item")
        nonserialized_formset = NonSerializedFormset(request.POST, prefix="formset1")
        other_cost_formset = SaleOtherCostFormset(request.POST, prefix="formset2")
        
        for index, item in enumerate(serialized_items):
            if item == "":
                continue
            if request.POST.get(f"price-sold-{index}") == "":
                item_object = SerializedItem.objects.get(pk=item, user=request.user)
                message =  f"you need to set a valid price for {item_object}"
                messages.add_message(request, messages.WARNING, message)
                return render(request, "exchange/add-sale-items.html", {
                    "sale_id": sale_id,
                    "sale": sale,
                    "formset1": nonserialized_formset,
                    "formset2": other_cost_formset,
                    "items": items
                })
            if item in serialized_items[(index + 1):]:
                message =  f"you cannot sell the same item twice"
                messages.add_message(request, messages.WARNING, message)
                return render(request, "exchange/add-sale-items.html", {
                    "sale_id": sale_id,
                    "sale": sale,
                    "formset1": nonserialized_formset,
                    "formset2": other_cost_formset,
                    "items": items
                })
            try:
                float_item = float(item)
            except ValueError:
                message =  f"you need to set a valid price for {item_object}"
                messages.add_message(request, messages.WARNING, message)
                return render(request, "exchange/add-sale-items.html", {
                    "sale_id": sale_id,
                    "sale": sale,
                    "formset1": nonserialized_formset,
                    "formset2": other_cost_formset,
                    "items": items
                })

        if nonserialized_formset.is_valid() and other_cost_formset.is_valid():
            instances = nonserialized_formset.save(commit=False)
            inventories = count_inventory(request.user)
            for instance in instances:
                if item_count := inventories.get(str(instance.item.SKU)):
                    # if user is trying to sell more than inventory
                    if item_count < instance.count:
                        message = f"You only have {item_count} of {instance.item} in non-serialized inventory, not {instance.count}"
                        messages.add_message(request, messages.WARNING, message)
                        return render(request, "exchange/add-sale-items.html", {
                            "sale_id": sale_id,
                            "sale": sale,
                            "formset1": nonserialized_formset,
                            "formset2": other_cost_formset,
                            "items": items
                        })
                # if item_count is none because there is no inventory    
                else:
                    message = f"No non-serialized inventory for {instance.item}"
                    messages.add_message(request, messages.WARNING, message)
                    return render(request, "exchange/add-sale-items.html", {
                        "sale_id": sale_id,
                        "sale": sale,
                        "formset1": nonserialized_formset,
                        "formset2": other_cost_formset,
                        "items": items
                    })
            for instance in instances:
                instance.user = request.user
                instance.sale = sale
                
                inventories = remove_from_inventory(
                    user=request.user,
                    item=instance.item, 
                    count=instance.count,
                    sale_price=instance.unit_price
                )
                message = "successfully updated inventory"
                messages.add_message(request, messages.SUCCESS, message)
                
                # save instance only if inventory is saved
                instance.save()
                for inv in inventories:
                    inv.nsi_sale_l = instance
                    inv.save()
                messages.add_message(request, messages.SUCCESS, "successfully added non serialized items")

            # other cost formset save
            instances = other_cost_formset.save(commit=False)
            for instance in instances:
                instance.user = request.user
                instance.sale = sale
                instance.save()
        
        # if formsets aren't valid
        else:
            return render(request, "exchange/add-sale-items.html", {
                "sale_id": sale_id,
                "sale": sale,
                "formset1": nonserialized_formset,
                "formset2": other_cost_formset,
                "items": items
            })
        #save serialized_items even if formsets arent submitted
        for index, item_id in enumerate(serialized_items):
            if item_id == "":
                continue
            item = SerializedItem.objects.get(user=request.user, pk=item_id)
            item.unit_sold_price = request.POST.get(f"price-sold-{index}")
            item.sale = sale
            item.status = "SLD"
            item.full_clean()
            item.save()
            messages.add_message(request, messages.SUCCESS, "successfully added serialized items")

        return HttpResponseRedirect(reverse("view_sale", kwargs={"sale_id": sale_id}))    

    items = SerializedItem.objects.filter(user=request.user, status="INV")
    return render(request, "exchange/add-sale-items.html", {
        "sale_id": sale_id,
        "sale": sale,
        "formset1": NonSerializedFormset(queryset=NonSerializedItemSaleList.objects.none(), prefix="formset1"),
        "formset2": SaleOtherCostFormset(queryset=SaleOtherCost.objects.none(), prefix="formset2"),
        "items": items
    })

@login_required()
def view_purchase(request, purchase_id):
    try:
        purchase = Purchase.objects.get(user=request.user, pk=purchase_id)
    except FieldError:
        return HttpBadRequestError(request, f"Purchase {purchase_id} wasnt made by you")
    other_costs = PurchaseOtherCost.objects.filter(user=request.user, purchase=purchase)
    serialized_items = purchase.serializeditem_set.all()
    item_list = purchase.ns_item_list.all()
    return render(request, "exchange/view-purchase.html", {
        "purchase": purchase,
        "serialized_items": serialized_items,
        "non_serialized": item_list,
        "other_costs": other_costs
    })

@login_required()
def purchases_view(request, supplier_id=None):
    if supplier_id:
        supplier = Supplier.objects.get(user=request.user, pk=supplier_id)
        purchases = Purchase.objects.filter(user=request.user, supplier=supplier).order_by("-date", "-pk")
    else:
        purchases = Purchase.objects.filter(user=request.user).order_by("-date", "-pk")
        supplier = None
    suppliers = Supplier.objects.filter(user=request.user)
    return render(request, "exchange/purchases.html", {
        "purchases": purchases,
        "suppliers": suppliers,
        "supplier": supplier
    })

@login_required()
def sales_view(request, customer_id=None):
    if customer_id:
        customer = Customer.objects.get(user=request.user, pk=customer_id)
        sales = Sale.objects.filter(user=request.user, customer=customer_id).order_by("-date", "-pk")
    else:
        sales = Sale.objects.filter(user=request.user).order_by("-date", "-pk")
        customer = None
    customers = Customer.objects.filter(user=request.user)
    
    return render(request, "exchange/sales.html", {
        "sales": sales,
        "customers": customers,
        "customer": customer
    })

@login_required()
def view_sale(request, sale_id):
    try:
        sale = Sale.objects.get(user=request.user, pk=sale_id)
    except FieldError:
        return HttpBadRequestError(request, f"Sale {sale_id} wasnt made by you")
    other_costs = SaleOtherCost.objects.filter(user=request.user, sale=sale)
    serialized_items = sale.serializeditem_set.all()
    item_list = sale.ns_item_list.all()
    return render(request, "exchange/view-sale.html", {
        "sale": sale,
        "serialized_items": serialized_items,
        "non_serialized": item_list,
        "other_costs": other_costs
    })

@login_required()
def view_item(request, sku):
    try:
        item = Item.objects.get(user=request.user, SKU=sku)
    except FieldError:
        return HttpBadRequestError(request, f"Item {item_id} wasnt made by you")
    serialized_items = SerializedItem.objects.filter(user=request.user, status="INV", item=item)
    # get current inventory for non serialized items
    inventory = Inventory.objects.filter(user=request.user, active_until=None, item=item)
    unserialized_count = 0
    for i in inventory:
        unserialized_count += i.count
    return render(request, "exchange/view-item.html", {
        "item": item,
        "serialized_items": serialized_items,
        "inventory": inventory
    })



@login_required()
def items(request, category_id=None, brand_id=None):
    if category_id:
        category = ItemCategory.objects.get(user=request.user, pk=category_id)
        brand = None
        items = Item.objects.filter(user=request.user, item_category=category)
    elif brand_id:
        category = None
        brand = ItemBrand.objects.get(user=request.user, pk=brand_id)
        items = Item.objects.filter(user=request.user, item_brand=brand)
    else:
        items = Item.objects.filter(user=request.user)
        category = None
        brand = None

    categories = ItemCategory.objects.filter(user=request.user)
    brands = ItemBrand.objects.filter(user=request.user)
    return render(request, "exchange/items.html", {
        "items": items,
        "categories": categories,
        "brands": brands,
        "category": category,
        "brand": brand
    })
