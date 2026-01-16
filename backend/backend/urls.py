from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.contrib.auth import views as auth_views

def landing(request):
    return render(request, "pages/landing.html")

def pricing(request):
    return render(request, "pages/pricing.html")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),

    # ✅ THIS MUST EXIST
    path("api/", include("api.urls")),

    path("chat/", include("chat.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("", landing),
    path("pricing/", pricing),
    path("", include("newuser.urls")),
    path("login/", auth_views.LoginView.as_view(
        template_name="auth/login.html"
    )),
    path("logout/", auth_views.LogoutView.as_view()),
    path("dashboard/", include("dashboard.urls")),
    path("billing/", include("billing.urls")),

]
