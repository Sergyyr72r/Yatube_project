from django.conf import settings
from django.core.paginator import Paginator


def paginator(posts_list, request):
    paginator = Paginator(posts_list, settings.POSTS_NUMBER)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
