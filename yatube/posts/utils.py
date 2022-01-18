from django.conf import settings
from django.core.paginator import Paginator


def get_page_obj(obj_list, request):
    paginator = Paginator(obj_list, settings.POST_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
