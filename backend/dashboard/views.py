from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import requests
from django.http import HttpResponseForbidden
from organizations.utils import user_has_role
from organizations.models import Organization


from billing.models import TokenUsage


from billing.models import Plan



API_BASE = "http://127.0.0.1:8000/api"


@login_required
def widget_page(request):
    api_key = request.GET.get("api_key")
    snippet = None

    if api_key:
        res = requests.get(
            f"{API_BASE}/widget/snippet/",
            params={"api_key": api_key},
        )
        if res.status_code == 200:
            snippet = res.json()["widget_snippet"]

    return render(request, "dashboard/widget.html", {
        "snippet": snippet,
        "api_key": api_key
    })


@login_required
def upload_page(request):
    status_msg = None

    if request.method == "POST":
        res = requests.post(
            f"{API_BASE}/knowledge/text/",
            json={
                "api_key": request.POST["api_key"],
                "title": request.POST["title"],
                "text": request.POST["text"],
            }
        )
        if res.status_code == 200:
            status_msg = "Uploaded successfully"

    return render(request, "dashboard/upload.html", {
        "status": status_msg
    })


@login_required
def logs_page(request):
    api_key = request.GET.get("api_key")
    logs = []

    if api_key:
        res = requests.get(
            f"{API_BASE}/chat/logs/",
            params={"api_key": api_key},
        )
        if res.status_code == 200:
            logs = res.json()

    return render(request, "dashboard/logs.html", {
        "logs": logs
    })




@login_required
def dashboard_home(request):
    user = request.user

    membership = user.organization_memberships.select_related(
        "organization", "organization__plan"
    ).first()

    organization = membership.organization
    plan = organization.plan

    usage = TokenUsage.objects.filter(
        organization=organization
    ).order_by("-id")[:100]

    total_tokens = sum(u.total_tokens for u in usage)

    return render(
        request,
        "dashboard/home.html",
        {
            "organization": organization,
            "plan": plan,
            "total_tokens": total_tokens,
        },
    )






def pricing_page(request):
    org = Organization.objects.first()  # later: request.user.org
    plans = Plan.objects.all()

    return render(request, "dashboard/pricing.html", {
        "plans": plans,
        "organization": org,
    })
