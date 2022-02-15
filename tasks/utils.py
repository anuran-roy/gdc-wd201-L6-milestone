from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from tasks.models import Task


def process_priorities(priority: int, user):
    """
    This function processes the priority of the incoming task
    and updates the priorities of the existing tasks accordingly.
    """
    concerned_priority: int = priority
    affected_queries = Task.objects.filter(
        user=user, priority__gte=concerned_priority, completed=False, deleted=False
    ).order_by("priority")

    print(
        f"\n\nNumber of entries affected by this operation = {affected_queries.count()}\n\n"
    )
    for i in affected_queries:
        if i.priority == concerned_priority:
            i.priority += 1
            concerned_priority += 1

    Task.objects.bulk_update(affected_queries, ["priority"])


class AuthMixin(LoginRequiredMixin):
    """
    Mixin class for extending the LoginRequiredMixin for the project.
    Helps to remove redundant variable values and logic
    """

    login_url = "/user/login"
    success_url = "/tasks"
    model = Task

    def get_success_url(self):
        return "/tasks"


class ViewMixin(LoginRequiredMixin):
    pass


class ListViewWithSearch(ListView):
    """
    Extends ListView class with appropriate querying functionality for searching
    tasks accordingly. Needs a custom queryset that varies over classes to operate.
    """

    def get_queryset(self):
        search_term = self.request.GET.get("search")
        tasks = self.queryset.filter(user=self.request.user)

        if search_term:
            tasks = self.queryset.filter(
                title__icontains=search_term, user=self.request.user
            )

        return tasks
