from rest_framework.pagination import PageNumberPagination


class HabitPagination(PageNumberPagination):
    """Пагинатор для вывода списка привычек"""

    page_size = 5
    page_size_query_param = "page_size"
    page_query_param = 20
