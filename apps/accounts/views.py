from datetime import date

from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def home(request):
    """Landing page."""
    return render(request, "home.html", {"year": date.today().year})


@login_required
def dashboard(request):
    organiser = getattr(request.user, "organiser", None)
    forms = []
    return render(
        request,
        "accounts/dashboard.html",
        {"organiser": organiser, "forms": forms, "year": date.today().year},
    )
