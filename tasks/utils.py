from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from tasks.models import Task


def process_priorities(priority: int, user):
    # redundant_priorities: bool = True
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
    login_url = "/user/login"
    success_url = "/tasks"
    model = Task

    def get_success_url(self):
        return "/tasks"


class ViewMixin(LoginRequiredMixin):
    pass


class ListViewWithSearch(ListView):
    def get_queryset(self):
        search_term = self.request.GET.get("search")
        tasks = self.queryset.filter(user=self.request.user)

        if search_term:
            tasks = self.queryset.filter(
                title__icontains=search_term, user=self.request.user
            )

        return tasks
