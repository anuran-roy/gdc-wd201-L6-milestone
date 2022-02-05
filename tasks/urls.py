"""task_manager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("", views.index),
    path("tasks/", views.GenericTaskView.as_view(), name="Tasks"),
    path("add-task/", views.GenericTaskCreateView.as_view(), name="Add Task"),
    path(
        "update-task/<pk>/", views.GenericTaskUpdateView.as_view(), name="Update Task"
    ),
    path(
        "delete-task/<pk>/",
        views.GenericTaskDeleteView.as_view(),
        name="Delete Task",
    ),
    path(
        "complete_task/<pk>/",
        views.CompleteTaskView.as_view(),
        name="Mark a task as completed",
    ),
    path(
        "completed_tasks/", views.CompletedTasksView.as_view(), name="Completed Tasks"
    ),
    path("all_tasks/", views.AllTasksView.as_view(), name="All Tasks"),
    path("task/<pk>/", views.GenericTaskDetailView.as_view(), name="View Task"),
    path("sessiontest/", views.session_storage_view),
    path("user/signup/", views.UserCreateView.as_view()),
    path("user/login/", views.UserLoginView.as_view()),
    path("user/logout/", LogoutView.as_view()),
]
