import os
from random import choice

from django import forms
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

import markdown2

from . import util

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    if content := util.get_entry(title):
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": markdown2.markdown(content)
        })
    else:
        return render(request, "encyclopedia/error.html", {
            "title": f"Error: {title} not found",
            "content": f"<i>{title}</i> does not match any wiki entry title"
        })

def search(request):
    query = request.POST["q"] 
    entries = []
    
    for entry in util.list_entries():
        if query in entry and query != entry:
            entries.append(entry)

    # if query is a substring in list
    if entries:
        return render(request, "encyclopedia/search.html", {
            "search": query,
            "entries": entries
        })
    
    # if query is in list or query is not a substring of entry in list
    return HttpResponseRedirect(reverse("wiki:entry", kwargs = {
        "title": query
    }))

def new_page(request):
    if request.method == "POST":
        title = request.POST["title"]
        content = request.POST["content"]
        if os.path.isfile(f"entries/{title}.md"):
            return render(request, "encyclopedia/error.html", {
                "title": f"Error: {title} exists",
                "content": f"Can not save {title} as a new Wiki page because it already exists!"
            })
        else:
            util.save_entry(title, content)
            
            return HttpResponseRedirect(reverse("wiki:entry", kwargs = {
                "title": title
            }))

    return render(request, "encyclopedia/new-page.html")

def edit_page(request, title):
    if request.method == "POST":
        util.save_entry(title, request.POST["content"])
        return HttpResponseRedirect(reverse("wiki:entry", kwargs = {
                "title": title
            }))

    content = util.get_entry(title)
    return render(request, "encyclopedia/edit-page.html", {
        "title": title,
        "content": content
    })

def random(request):
    random_entry = choice(os.listdir("entries")).rstrip(".md")
    return HttpResponseRedirect(reverse("wiki:entry", kwargs = {
                "title": random_entry
            }))