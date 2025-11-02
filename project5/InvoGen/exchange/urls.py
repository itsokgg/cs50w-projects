from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register_view, name="register"),
    path("new-supplier", views.new_supplier, name="new_supplier"),
    path("new-customer", views.new_customer, name="new_customer"),
    path("new-item", views.new_item, name="new_item"),
    path("new-purchase", views.new_purchase, name="new_purchase"),
    path("add-purchase-items/<int:purchase_id>", views.add_purchase_items, name="add_purchase_items"),
    path("new-sale", views.new_sale, name="new_sale"),
    path("add-sale-items/<int:sale_id>", views.add_sale_items, name="add_sale_items"),
    path("purchases", views.purchases_view, name="purchases"),
    path("purchases/supplier_id=<int:supplier_id>", views.purchases_view, name="supplier_purchases"),
    path("purchase/<int:purchase_id>", views.view_purchase, name="view_purchase"),
    path("sales", views.sales_view, name="sales"),
    path("sales/customer_id=<int:customer_id>", views.sales_view, name="customer_sales"),
    path("sale/<int:sale_id>", views.view_sale, name="view_sale"),
    path("inventory/item_id=<int:item_id>", views.index, name="item_inventory"),
    path("view-item/<str:sku>", views.view_item, name="view_item"),
    path("items/", views.items, name="items"),
    path("items/category=<int:category_id>", views.items, name="category_items"),
    path("items/brand=<int:brand_id>", views.items, name="brand_items")
]