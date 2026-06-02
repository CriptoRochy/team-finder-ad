from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from http import HTTPStatus

from .models import Project
from .forms import ProjectForm


def paginate_queryset(request, queryset, per_page=12):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def project_list_view(request):
    projects_list = (
        Project.objects
        .select_related('owner')
        .all()
        .order_by("-created_at")
    )
    page_obj = paginate_queryset(request, projects_list)
    return render(
        request,
        "projects/project_list.html",
        {"page_obj": page_obj, "query_prefix": ""},
    )


def project_detail_view(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related('owner'),
        id=project_id
    )
    return render(
        request,
        "projects/project-details.html",
        {"project": project},
    )


@login_required
def create_project_view(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect("projects:detail", project_id=project.id)
    else:
        form = ProjectForm()
    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": False},
    )


@login_required
def edit_project_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.owner != request.user:
        return redirect("projects:detail", project_id=project.id)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("projects:detail", project_id=project.id)
    else:
        form = ProjectForm(instance=project)
    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": True},
    )


@login_required
@require_POST
def toggle_favorite_view(request, project_id):
    project = Project.objects.filter(id=project_id).first()
    if not project:
        return JsonResponse(
            {"status": "error", "message": "Project not found"},
            status=HTTPStatus.NOT_FOUND
        )

    is_favorited = request.user.favorites.filter(id=project_id).exists()
    if is_favorited:
        request.user.favorites.remove(project)
        favorited = False
    else:
        request.user.favorites.add(project)
        favorited = True

    return JsonResponse({"status": "ok", "favorited": favorited})


@login_required
@require_POST
def toggle_participate_view(request, project_id):
    project = Project.objects.filter(id=project_id).first()
    if not project:
        return JsonResponse(
            {"status": "error", "message": "Project not found"},
            status=HTTPStatus.NOT_FOUND
        )

    is_participating = project.participants.filter(id=request.user.id).exists()
    if is_participating:
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)

    return JsonResponse({
        "status": "ok",
        "is_participating": not is_participating,
        "participants_count": project.participants.count()
    })


@login_required
@require_POST
def complete_project_view(request, project_id):
    project = Project.objects.filter(id=project_id).first()
    if not project:
        return JsonResponse(
            {"status": "error", "message": "Project not found"},
            status=HTTPStatus.NOT_FOUND
        )

    if (project.owner != request.user
            or project.status != Project.STATUS_OPEN):
        return JsonResponse(
            {"status": "error", "message": "Forbidden"},
            status=HTTPStatus.FORBIDDEN,
        )

    project.status = Project.STATUS_CLOSED
    project.save()
    return JsonResponse(
        {"status": "ok", "project_status": Project.STATUS_CLOSED}
    )


@login_required
def favorites_list_view(request):
    projects = (
        request.user.favorites
        .select_related('owner')
        .all()
        .order_by("-created_at")
    )
    return render(
        request,
        "projects/favorite_projects.html",
        {"projects": projects},
    )
