from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def paginate(request, collection, per=12):
    paginator = Paginator(collection, per)
    page = request.GET.get('page')
    try:
        collection = paginator.page(page)
    except PageNotAnInteger:
        collection = paginator.page(1)
    except EmptyPage:
        collection = paginator.page(paginator.num_pages)
    return collection
