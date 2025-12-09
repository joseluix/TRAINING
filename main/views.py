from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    """Renders the home page."""
    return render(request, 'main/home.html')
