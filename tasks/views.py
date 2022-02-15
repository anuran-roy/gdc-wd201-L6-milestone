from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseRedirect

from django.views import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView

# from django.views.generic.delete import DeleteView

from django.forms import ModelForm

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin

from tasks.models import Task
from tasks.utils import process_priorities, AuthMixin, ListViewWithSearch


def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("/tasks")
    else:
        return HttpResponseRedirect("/user/login")


class UserCreationFormCustom(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["class"] = "p-4 m-4 bg-gray-200/75"
        self.fields["password1"].widget.attrs["class"] = "p-4 m-4 bg-gray-200/75"
        self.fields["password2"].widget.attrs["class"] = "p-4 m-4 bg-gray-200/75"
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs[
                "autofocus"
            ] = True


class UserAuthenticationForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

        # Set the max length and label for the "username" field.
        self.username_field = User._meta.get_field(User.USERNAME_FIELD)
        username_max_length = self.username_field.max_length or 254
        self.fields["username"].max_length = username_max_length
        self.fields["username"].widget.attrs["maxlength"] = username_max_length
        if self.fields["username"].label is None:
            self.fields["username"].label = capfirst(self.username_field.verbose_name)

        self.fields["username"].widget.attrs["class"] = "p-4 m-4 bg-gray-200/75"
        self.fields["password"].widget.attrs["class"] = "p-4 m-4 bg-gray-200/75"


class UserLoginView(LoginView):
    form_class = UserAuthenticationForm
    template_name = "user_login.html"
    success_url = "/user/login/"


class UserCreateView(CreateView):
    form_class = UserCreationFormCustom
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
        if "priority" in form.changed_data:
            process_priorities(
                priority=form.cleaned_data["priority"], user=self.request.user
            )

        self.object = form.save()

        return HttpResponseRedirect(self.get_success_url())


class GenericTaskCreateView(AuthMixin, CreateView):
    form_class = TaskCreateForm
    template_name = "task_create.html"

    def form_valid(self, form):
        process_priorities(
            priority=form.cleaned_data["priority"], user=self.request.user
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
        ).order_by("priority")


class GenericTaskDeleteView(AuthMixin, DeleteView):
    template_name = "task_delete.html"


class GenericTaskView(LoginRequiredMixin, ListViewWithSearch):
    queryset = Task.objects.filter(deleted=False, completed=False).order_by("priority")
    template_name = "tasks.html"
    context_object_name = "tasks"
    paginate_by = 5


class CompleteTaskView(AuthMixin, View):
    def get(self, request, pk):
        tasks = Task.objects.filter(id=pk, user=self.request.user).order_by("priority")
        tasks.update(completed=True)

        return HttpResponseRedirect("/tasks")


class CompletedTasksView(AuthMixin, ListViewWithSearch):
    queryset = Task.objects.filter(completed=True).order_by("priority")
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


def delete_all(request):
    queryset = Task.objects.filter(user=request.user).order_by("priority")
