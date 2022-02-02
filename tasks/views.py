from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from django.views import View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView

# from django.views.generic.delete import DeleteView

from django.forms import ModelForm

from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin

from tasks.models import Task


def index(request):
    auth_status = (
        "authenticated" if request.user.is_authenticated else "not authenticated"
    )
    return render(
        request,
        "index.html",
        {"username": request.user, "auth_status": auth_status},
    )


class UserLoginView(LoginView):
    template_name = "user_login.html"


class UserCreateView(CreateView):
    form_class = UserCreationForm
    template_name = "user_create.html"
    success_url = "/user/login/"


class TaskCreateForm(ModelForm):
    def clean_title(self):  # Format: create_<field>
        # raise ValidationError("Title isn't clean")
        title = self.cleaned_data["title"]

        if len(title) == 0:
            raise ValidationError("Title is required")

        return title

    # def clean(self):
    # queryset = Task.objects.filter(
    #     deleted=False,
    #     priority=self.cleaned_data["priority"],
    #     # user=self.request.user,
    # ).exists()

    # if queryset:
    #     queryset = Task.objects.filter(
    #         deleted=False,
    #         priority__gte=self.cleaned_data["priority"],
    #         user=self.request.user,
    #     )

    #     for i in range(len(queryset) - 1):
    #         if queryset[i].priority == self.cleaned_data["priority"]:
    #             queryset[i].priority += 1
    #             queryset[i].save()

    #         if queryset[i].priority == queryset[i + 1].priority:
    #             queryset[i + 1].priority += 1
    #             queryset[i + 1].save()

    class Meta:
        model = Task
        fields = ("priority", "title", "description")


class GenericTaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskCreateForm
    template_name = "task_update.html"
    success_url = "/tasks"

    def get_queryset(self):
        print("Method GET_Queryset() called.")
        queryset = Task.objects.filter(id=self.kwargs["pk"])
        self.updateViewQueryObject = queryset

        return queryset

    def form_valid(self, form):
        print(self.__dict__)
        print("Form_Valid() for Update called.")
        # self.object = form.save()

        _ = self.updateViewQueryObject.update(
            priority=form.cleaned_data["priority"],
            title=form.cleaned_data["title"],
            description=form.cleaned_data["description"],
        )

        # _ = (
        #     print(self.updateViewQueryObject.__dict__)
        #     if query is not None
        #     else print("Query unsuccessful")
        # )

        newQuery = Task.objects.filter(priority=form.cleaned_data["priority"])

        if newQuery:
            queryset = Task.objects.filter(
                completed=False,
                deleted=False,
                priority__gte=form.cleaned_data["priority"],
                user=self.request.user,
            )

            for i in range(len(queryset) - 1):
                if queryset[i].priority == form.cleaned_data["priority"]:
                    queryset[i].priority += 1

                if queryset[i].priority == queryset[i + 1].priority:
                    queryset[i + 1].priority += 1

            for i in range(len(queryset)):
                queryset[i].save()

        # self.object = form.save(commit=False)
        # self.object.user = self.request.user
        # self.object.save()
        self.updateViewQueryObject[0].save()

        return HttpResponseRedirect(self.get_success_url())
        # return HttpResponseRedirect("/tasks")


class GenericTaskCreateView(LoginRequiredMixin, CreateView):
    # model = Task
    # fields = ("title", "description")
    login_url = "/user/login"
    form_class = TaskCreateForm
    template_name = "task_create.html"
    success_url = "/tasks"

    def form_valid(self, form):
        print("Form_Valid() for Create called.")
        # self.object = form.save()

        queryset = Task.objects.filter(
            deleted=False,
            priority=form.cleaned_data["priority"],
            user=self.request.user,
        ).exists()

        if queryset:
            queryset = Task.objects.filter(
                completed=False,
                deleted=False,
                priority__gte=form.cleaned_data["priority"],
                user=self.request.user,
            )

            for i in range(len(queryset) - 1):
                if queryset[i].priority == form.cleaned_data["priority"]:
                    queryset[i].priority += 1

                if queryset[i].priority == queryset[i + 1].priority:
                    queryset[i + 1].priority += 1

            for i in range(len(queryset)):
                queryset[i].save()

        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())
        # return HttpResponseRedirect("/tasks")


class GenericTaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "task_detail.html"
    # queryset = Task

    def get_success_url(self):
        return Task.objects.filter(
            deleted=False, completed=False, user=self.request.user
        )


class GenericTaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = "task_delete.html"
    success_url = "/tasks"

    def get_success_url(self):
        # return Task.objects.filter(
        #     deleted=False, completed=False, user=self.request.user
        # )
        return "/tasks"


class GenericTaskView(LoginRequiredMixin, ListView):
    queryset = Task.objects.filter(deleted=False, completed=False)
    template_name = "tasks.html"
    context_object_name = "tasks"
    paginate_by = 5

    def get_queryset(self):
        search_term = self.request.GET.get("search")
        if self.request.user.is_authenticated:
            tasks = Task.objects.filter(
                deleted=False, completed=False, user=self.request.user
            )

            if search_term:
                tasks = tasks.filter(
                    title__icontains=search_term, user=self.request.user
                )

            return tasks
        else:
            return []


# class CreateTaskView(View):
#     queryset = Task.objects.filter(deleted=False)
#     template_name = "task_create.html"

#     def get(self, request):
#         return render(request, "task_create.html")

#     def post(self, request):
#         task_obj = Task(
#             priority=request.POST.get("priority"),
#             title=request.POST.get("heading"),
#             description=request.POST.get("task"),
#             completed=False,
#             deleted=False,
#         )

#         task_obj.save()
#         queryset = Task.objects.get(deleted=False)

#         for i in range(len(queryset) - 1):
#             ob1 = queryset[i]
#             ob2 = queryset[i + 1]

#             if ob1.priority == ob2.priority:
#                 # ob2.priority += 1

#                 ob2.update(priority=ob2.priority + 1)
#                 print(ob2.title, ob2.description, ob2.priority)
#                 ob2.save()

#         return HttpResponseRedirect("/tasks")


# class DeleteTaskView(View):
#     def get(self, request, index):
#         tasks = Task.objects.filter(id=index, user=self.request.user)
#         tasks.update(deleted=True)

#         return HttpResponseRedirect("/tasks")


class CompleteTaskView(LoginRequiredMixin, View):
    def get(self, request, index):
        tasks = Task.objects.filter(id=index, user=self.request.user)
        tasks.update(completed=True)

        return HttpResponseRedirect("/tasks")


class CompletedTasksView(LoginRequiredMixin, ListView):
    queryset = Task.objects.filter(deleted=False)
    template_name = "completed.html"
    context_object_name = "completed"
    paginate_by = 5

    def get_queryset(self):
        search_term = self.request.GET.get("search")
        tasks = Task.objects.filter(deleted=False, user=self.request.user)

        if search_term:
            tasks = Task.objects.filter(
                title__icontains=search_term, completed=True, user=self.request.user
            )

        return tasks


def session_storage_view(request):
    total_views = (
        int(request.session.get("total_views"))
        if request.session.get("total_views") is not None
        else 0
    )
    request.session["total_views"] = total_views + 1

    return HttpResponse(f"<h1>Total number of views = {total_views}</h1>")
