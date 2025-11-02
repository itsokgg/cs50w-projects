# InvoGen
## Overview And Features
InvoGen is an application, built with [Django](https://www.djangoproject.com/), which allows business to keep track of their items, purchases, sales, and Inventory. It supports purchasing, selling, and inventory keeping of serialized and non-serialized items. You can add new and view existing `Purchases`, `Sales` and `Items` by clicking the corresponding link in the navbar. Purchasing and selling items will corespondigly increase and decrease your inventory. Your `Inventory` can be filtered by `Item`, `Purchases` by `Supplier`, `Sales` by `Customer`, and `Items` by `Category` and `Brand`. Also, when viewing your `Inventory`, `Purchases`, `Sales` or `Items`, you can click on any `Item`, `Purchase`, or `Sale` listed to view its contents.

## Contents
These are files and folders, for InvoGen, that I have created or significantly altered from the base Django project. They are in the `exchange` folder, InvoGen's only app.
- `urls.py`: contains all the URL paths for InvoGen
- `views.py`: contains all of the routes used by `urls.py`
- `/templates/exchange`: a folder with all the HTML templates for views.py to render GET and POST requests 
- `utils.py`: contains three helper functions used in `views.py`
- `models.py`: contains the .`schema` for the SQL database in Python using [Django Models](https://docs.djangoproject.com/en/5.2/topics/db/models/)
- `forms.py`: contains the [Django Model Forms](https://docs.djangoproject.com/en/5.2/topics/forms/modelforms/), used in `views.py`, to render as HTML forms in HTML templates in `templates/exchange/`
- `admin.py`: registers the models from `models.py` to the admin interface

## Usage
To run InvoGen, if you haven't already, install [Python](https://www.python.org/downloads/) and [Django](https://docs.djangoproject.com/en/5.2/topics/install/).
Open a terminal in the project's directory. cd into `InvoGen` and then run:
```bash
python manage.py runserver
```
A development server will run on http://127.0.0.1:8000/. Open your browse in it.
### Register
To use InvoGen you need an account. Click on register in the navbar, and then fill and submit the resulting form to create an account.

### Add An Item
To add an `Item`, you need to first add an `Item Brand` and `Item Category`. Click on `New` -> `Item`. Then click `Make New Item Category` on the right of the window, enter a name and abrv, and click `Add Category`. Repeat for `Item Brand`, also on the right side of the window. Now you can enter the information for your item and save it.
### Add A Purchase
To add a `Purchase` you need to first add a `Supplier`. Click `New` -> `Supplier`, enter supplier information and click `add`. You can only purchase items that you have added to `Items`, so make sure to add all your items before you add the `Purchase`. Once you have added `Items` and a `Supplier` , click `New` -> `Purchase`. Enter information and then click `Save And Add Items` to save the Purchase. Now, you will be redirected to add items to the purchase. Enter the `Items` purchased, and optionally `Other Costs`, then click `Save`. Items purchased will be saved to your `Inventory`, which you can view by clicking `Inventory` in the navbar.
### Add A Sale
Adding a `Sale` follows the same process as [Add a Purchase](#add-a-purchase) except you must have a `Customer` added instead of a `Supplier` and have `Items` in your `Inventory` to sell.

## Distinctiveness and Complexity
InvoGen is distinct from the other projects in cs50W as it is an application for buisiness to track their `Items`, `Purchases`, `Sales`, and `Inventory`. It doesn't give users the ability to interact with others - through emailing, selling/buying, or posting social content - like projects Mail, Commerce and Network do respectively. Also, it doesn't allow users to Google search like Search does or query an encyclopedia database like Wiki.

InvoGen has multiple features that make it complex. 

First, for `add-purchase-items.html` and `add-sale-items.html` you can dynamically render extra formsets for `Serialized Items`, `Non-Serialized Items`, and `Other Costs` by clicking a button. Clicking the button will trigger a JS function that will update the total `formsets` in the `management form`, copy the `empty formset` and render it to the DOM - replacing `__prefix__` with the formset number, and heading the form with the correct item number. Also, `add-purchase-items.html` and `add-sale-items.html`, have a `+` button which, when clicked, will trigger custom JS functions to add extra HTML `input`s.

Second, all forms submitted are first checked for invalid inputs before any of their data is saved into the database. This is helpful when one form in the submission is valid but another is not. Instead of the backend, `views.py`, first validating and saving the first form and then validating and saving the second form, it will first validate all the forms and then save them. This was especially hard to accomplish for routes `add_purchase_items(request, purchase_id)` and `add_sale_items(request, sale_id)` in `views.py` because they both handle many forms - Django Model Forms and regular HTML forms.

Third, HTML doesnt allow wrapping of a table row in an anchor tag to make the entire row a link to another page like this:
```bash
<a><tr><tr></a>
```
Therefore - in `index.html`, `view-purchase.html` and `view-sale.html`- I added a dataset to the table row so that when it is clicked, a custom JS function will dynamicaly redirect the user:
```bash
<tr class="item" data-anchor="{% url 'view_item' sku=item.item.SKU %}">
<script>
    document.addEventListener("DOMContentLoaded", ()=> {
        let items = document.querySelectorAll(".item");
        items.forEach((tr)=>{
            tr.addEventListener("click", ()=> {
            window.location.href = tr.dataset.anchor
        })
        })
    } )
</script>
```

Fourth, every `Serialized Item` and `Non-Serialized Item`, is saved with its purchase cost and sale price so you can see profits from each `Item`. If you bought 5 of an `Item` for $5 and 5 more of the same `Item` for $6 and you sold all 10 of the `Item` for $10, in `/view-sale/sale_id=?` you will see the cost and price sold for of each `Item`. 

Fifth, every `Inventory`, `Purchase`, `Sale` and `Item` are viewable with their respective filters. `Inventory` by `Item`, `Purchase` by `supplier`, `sale` by `customer`, and `Item` by `Category` and `Brand`. Also, when viewing your `inventory`, `purchases`, `sales` and `items`, you can click on any `item`, `purchase`, or `sale` listed to view its contents.

Sixth, setting a `Restock Warning` for an `Item` will warn you when the `Item`'s `Serialized` and `Non-Serialized` `Inventory` reaches its minimum. This is because `get_restock_warning(user)` in `utils.py`, counts both the `Serialized` and `Non-Serialized` `Inventory` before giving a `Restock Warning`.

Last, all `Model Forms` that I instantiated in `forms.py` have Bootstrap classes, and many of them have custom labels, changing them from their default labels in `models.py`.