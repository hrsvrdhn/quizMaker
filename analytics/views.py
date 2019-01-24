import datetime
import csv

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse

# Create your views here.
from .models import ObjectViewed


@login_required
def analytics_page(request):
    if not request.user.is_superuser:
        raise Http404

    return render(request, "main_page.html", {})


@login_required
def analytics_download(request):
    if not request.user.is_superuser:
        raise Http404

    from_date, to_date = None, None
    try:
        from_date = datetime.datetime.strptime(request.POST.get("from"), "%Y-%m-%d")
        to_date = datetime.datetime.strptime(request.POST.get("to"), "%Y-%m-%d")
    except:
        raise Http404

    if from_date > to_date:
        from_date, to_date = to_date, from_date

    objs = ObjectViewed.objects.filter(timestamp__gte=from_date, timestamp__lte=to_date)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="{}-{}.csv"'.format(
        from_date.date(), to_date.date()
    )

    writer = csv.writer(response)
    for obj in objs:
        try:
            writer.writerow(
                [
                    obj.user.user.user.username,
                    obj.ip_address,
                    obj.content_type,
                    obj.content_object,
                    obj.timestamp,
                ]
            )
        except:
            pass

    return response
