from django.shortcuts import render, redirect
from django.contrib.auth import login

from .forms import SignupForm
from organizations.models import Organization, OrganizationMember
from billing.models import Plan


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()

            # 🔹 Assign Free plan
            free_plan = Plan.objects.get(name="Free")

            # 🔹 Create organization
            org = Organization.objects.create(
                name=form.cleaned_data["organization_name"],
                plan=free_plan,
            )

            # 🔹 Link user
            OrganizationMember.objects.create(
                user=user,
                organization=org,
                role="owner",
            )

            login(request, user)
            return redirect("/dashboard/")

    else:
        form = SignupForm()

    return render(request, "auth/signup.html", {"form": form})

