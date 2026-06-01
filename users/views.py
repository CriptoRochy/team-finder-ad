from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import UserRegistrationForm, UserLoginForm, UserProfileEditForm
from django.contrib.auth.forms import PasswordChangeForm
from .models import User
from projects.models import Project
import os


def register_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("projects:list")
    else:
        form = UserRegistrationForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("projects:list")
        else:
            form.add_error(None, "Неверный email или пароль")
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
        form = UserProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            if 'avatar' in request.FILES and request.user.avatar:
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
    users_list = User.objects.all().order_by("id")
    active_filter = request.GET.get("filter")

    if request.user.is_authenticated and active_filter:
        if active_filter == "owners-of-favorite-projects":
            users_list = User.objects.filter(owned_projects__interested_users=request.user).distinct()
        elif active_filter == "owners-of-participating-projects":
            users_list = User.objects.filter(owned_projects__participants=request.user).distinct()
        elif active_filter == "interested-in-my-projects":
            users_list = User.objects.filter(favorites__owner=request.user).distinct()
        elif active_filter == "participants-of-my-projects":
            users_list = User.objects.filter(participated_projects__owner=request.user).distinct()
        else:
            active_filter = None

    paginator = Paginator(users_list, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    query_prefix = ""
    if active_filter:
        query_prefix = f"filter={active_filter}&"

    return render(request, "users/participants.html", {
        "page_obj": page_obj,
        "active_filter": active_filter,
        "query_prefix": query_prefix,
    })