import os

from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import UserLoginForm, UserProfileEditForm, UserRegistrationForm
from .models import User


FILTER_OWNERS_OF_FAVORITE_PROJECTS = "owners-of-favorite-projects"
FILTER_OWNERS_OF_PARTICIPATING_PROJECTS = "owners-of-participating-projects"
FILTER_INTERESTED_IN_MY_PROJECTS = "interested-in-my-projects"
FILTER_PARTICIPANTS_OF_MY_PROJECTS = "participants-of-my-projects"


def paginate_queryset(request, queryset, per_page=12):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def register_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("users:login")
    else:
        form = UserRegistrationForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = UserLoginForm(data=request.POST, request=request)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("projects:list")
    else:
        form = UserLoginForm()
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("projects:list")


def user_detail_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, "users/user-details.html", {"user": user})


@login_required
def edit_profile_view(request):
    if request.method == "POST":
        form = UserProfileEditForm(
            request.POST, request.FILES, instance=request.user
        )
        if form.is_valid():
            if "avatar" in request.FILES and request.user.avatar:
                old_avatar_path = request.user.avatar.path
                if os.path.exists(old_avatar_path):
                    os.remove(old_avatar_path)
            form.save()
            return redirect("users:detail", user_id=request.user.id)
    else:
        form = UserProfileEditForm(instance=request.user)
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password_view(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect("users:detail", user_id=request.user.id)
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "users/change_password.html", {"form": form})


def users_list_view(request):
    users_list = User.objects.select_related().all().order_by("-date_joined")
    active_filter = request.GET.get("filter")

    if request.user.is_authenticated and active_filter:
        if active_filter == FILTER_OWNERS_OF_FAVORITE_PROJECTS:
            users_list = User.objects.filter(
                owned_projects__interested_users=request.user
            ).distinct()
        elif active_filter == FILTER_OWNERS_OF_PARTICIPATING_PROJECTS:
            users_list = User.objects.filter(
                owned_projects__participants=request.user
            ).distinct()
        elif active_filter == FILTER_INTERESTED_IN_MY_PROJECTS:
            users_list = User.objects.filter(
                favorites__owner=request.user
            ).distinct()
        elif active_filter == FILTER_PARTICIPANTS_OF_MY_PROJECTS:
            users_list = User.objects.filter(
                participated_projects__owner=request.user
            ).distinct()
        else:
            active_filter = None

    page_obj = paginate_queryset(request, users_list)

    query_prefix = ""
    if active_filter:
        query_prefix = f"filter={active_filter}&"

    return render(
        request,
        "users/participants.html",
        {
            "page_obj": page_obj,
            "active_filter": active_filter,
            "query_prefix": query_prefix,
        },
    )
