from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseRedirect

from django.views import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView

# from django.views.generic.delete import DeleteView

from django.forms import ModelForm

from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin

from tasks.models import Task
from tasks.utils import sortPriorities, AuthMixin, ListViewWithSearch


def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("/tasks")
    else:
        return HttpResponseRedirect("/user/login")


class UserLoginView(LoginView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    template_name = "user_login.html"


class UserCreateView(CreateView):
    form_class = UserCreationForm
    template_name = "user_create.html"
    success_url = "/user/login/"


class TaskCreateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs["class"] = "p-4 m-4 bg-gray-200/75"
        self.fields["description"].widget.attrs["class"] = "p-4 m-4 bg-gray-200/75"
        self.fields["priority"].widget.attrs["class"] = "p-4 m-4 bg-gray-200/75"
        self.fields["completed"].widget.attrs["class"] = "p-4 m-4 bg-gray-200/75"

    def clean_title(self):  # Format: create_<field>
        title = self.cleaned_data["title"]

        if len(title) == 0:
            raise ValidationError("Title is required")

        return title

    class Meta:
        model = Task
        fields = ("priority", "title", "description", "completed")


class GenericTaskUpdateView(AuthMixin, UpdateView):
    form_class = TaskCreateForm
    template_name = "task_update.html"

    def form_valid(self, form):
        if Task.objects.filter(priority=form.cleaned_data["priority"]).exists():
            self.object.priority = form.cleaned_data["priority"]

            queryset = (
                Task.objects.filter(
                    completed=False,
                    deleted=False,
                    priority__gte=form.cleaned_data["priority"],
                    user=self.request.user,
                )
                .select_for_update()
                .exclude(priority=self.object.priority)
            )

            Task.objects.bulk_update(
                sortPriorities(form.cleaned_data["priority"], queryset),
                ["priority", "title", "description", "completed"],
            )

        self.object.save()

        return HttpResponseRedirect(self.get_success_url())


class GenericTaskCreateView(AuthMixin, CreateView):
    form_class = TaskCreateForm
    template_name = "task_create.html"

    def form_valid(self, form):
        if Task.objects.filter(
            deleted=False,
            priority=form.cleaned_data["priority"],
            user=self.request.user,
        ).exists():
            queryset = (
                Task.objects.filter(
                    completed=False,
                    deleted=False,
                    priority__gte=form.cleaned_data["priority"],
                    user=self.request.user,
                )
                .select_for_update()
                .order_by("priority")
            )

            Task.objects.bulk_update(
                sortPriorities(form.cleaned_data["priority"], queryset),
                ["priority"],
            )

        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())


class GenericTaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "task_detail.html"

    def get_success_url(self):
        return Task.objects.filter(
            deleted=False, completed=False, user=self.request.user
        )


class GenericTaskDeleteView(AuthMixin, DeleteView):
    template_name = "task_delete.html"


class GenericTaskView(LoginRequiredMixin, ListViewWithSearch):
    queryset = Task.objects.filter(deleted=False, completed=False)
    template_name = "tasks.html"
    context_object_name = "tasks"
    paginate_by = 5


class CompleteTaskView(AuthMixin, View):
    def get(self, request, pk):
        tasks = Task.objects.filter(id=pk, user=self.request.user)
        tasks.update(completed=True)

        return HttpResponseRedirect("/tasks")


class CompletedTasksView(AuthMixin, ListViewWithSearch):
    queryset = Task.objects.filter(completed=True)
    template_name = "completed.html"
    context_object_name = "completed"
    paginate_by = 5


class AllTasksView(AuthMixin, ListViewWithSearch):
    queryset = Task.objects.all()
    template_name = "all_tasks.html"
    context_object_name = "all_tasks"
    paginate_by = 5


def session_storage_view(request):
    total_views = (
        int(request.session.get("total_views"))
        if request.session.get("total_views") is not None
        else 0
    )
    request.session["total_views"] = total_views + 1

    return HttpResponse(f"<h1>Total number of views = {total_views}</h1>")
