from django import shortcuts
from django import http
from django import shortcuts
from django.db import models as django_models
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import file_html

from . import models


def locations(request):
    return shortcuts.render(
        request,
        template_name='locations.html',
        context=dict(
            locations=models.Location.objects.order_by('name')
        )
    )


def edit_location(request, id):
    location = shortcuts.get_object_or_404(models.Location, id=id)
    return shortcuts.render(
        request,
        template_name='partials/edit_location.html',
        context=dict(
            location=location
        )
    )


def view_location(request, id):
    location = shortcuts.get_object_or_404(models.Location, id=id)
    return shortcuts.render(
        request,
        template_name='partials/single_location.html',
        context=dict(
            location=location
        )
    )


def update_location(request, id):
    location = shortcuts.get_object_or_404(models.Location, id=id)
    location.name = request.POST['name']
    location.save()
    return shortcuts.render(
        request,
        template_name='partials/single_location.html',
        context=dict(
            location=location
        )
    )


def delete_location(request, id):
    location = shortcuts.get_object_or_404(models.Location, id=id)
    location.delete()
    return shortcuts.render(
        request,
        template_name='partials/deleted_location.html',
        context=dict(
            location=location
        )
    )


def save_new_location(request):
    name = request.POST['name']
    models.Location.objects.create(name=name)
    return shortcuts.render(
        request,
        template_name='partials/locations_list.html',
        context=dict(
            locations=models.Location.objects.order_by('name')
        )
    )


def dinosaur_chart_html(start, end):
    count = {n: 0 for n in range(end, start + 1)}
    for dinosaur in models.Dinosaur.objects.all():
        if dinosaur.period_start is None:
            continue
        for period in range(dinosaur.period_end, dinosaur.period_start + 1):
            # TODO Tidy this up?
            if period > start or period < end:
                continue
            count[period] += 1
    plot = figure(tools=[])
    plot.toolbar.logo = None
    plot.line([-x for x in count.keys()], list(count.values()), line_width=2)

    return file_html(plot, CDN, "my plot")


def dinosaur_chart(request):
    # TODO: tidy up start/end, handling of 'years ago'
    # For each 'year' between first and last, calculate the number of known dinosaur species
    start_end = models.Dinosaur.objects.aggregate(
        start=django_models.Max('period_start'),
        end=django_models.Min('period_end')
    )
    start = start_end['start']
    end = start_end['end']
    chart_html = dinosaur_chart_html(start, end)
    return shortcuts.render(
        request,
        'dinosaur_chart.html',
        context=dict(
            chart=chart_html,
            period_start=start,
            period_end=end,
        )
    )


# TODO: Better naming - distinguish between chart page and chart only?
def dinosaur_chart_partial(request):
    start = int(request.GET['start'])
    end = int(request.GET['end'])
    # TODO: tidy up start/end, handling of 'years ago'
    return http.HttpResponse(dinosaur_chart_html(start, end))


def dinosaurs(request):
    dinosaurs = models.Dinosaur.objects.order_by('name')
    dinosauria_taxon = models.Taxon.objects.get(parent=None)
    taxons = models.Taxon.objects.filter(parent=dinosauria_taxon)
    return shortcuts.render(
        request,
        'dinosaurs.html',
        context=dict(
            taxons=taxons,
            dinosaurs=dinosaurs
        )
    )


def update_dinosaurs_from_selection(request):
    # -1: all, -2: no value
    taxon_ids = [
        int(request.GET.get(f'taxon_id_{level}', -2))
        for level in [1, 2, 3]
    ]
    select_level = int(request.GET.get('select_level'))

    id = taxon_ids[select_level - 1]
    if id == -1:
        select_level -= 1
        if select_level > 0:
            id = taxon_ids[select_level - 1]

    context = {}
    context['level'] = select_level

    if select_level > 0:
        selected_taxon = shortcuts.get_object_or_404(models.Taxon, id=id)
        context['dinosaurs'] = [
            dinosaur
            for dinosaur in models.Dinosaur.objects.order_by('name')
            if selected_taxon in dinosaur.full_taxonomy()
        ]
        context['sub_taxons'] = selected_taxon.taxon_set.order_by('name')
        context['filter_description'] = ' -> '.join(taxon.name for taxon in selected_taxon.full_taxonomy())
    else:
        context['dinosaurs'] = models.Dinosaur.objects.order_by('name')
        context['filter_description'] = 'All dinosaurs'

    return shortcuts.render(
        request,
        'partials/dinosaur_list_plus_dropdown.html',
        context=context
    )


def dinosearch(request):
    return shortcuts.render(
        request,
        'dinosearch.html',
        context=dict(
            dinosaurs=models.Dinosaur.objects.order_by('name'),
            types=['all', 'name', 'diet', 'period', 'location', 'species'],
        )
    )


def dinosearch_list(request):
    search_key = request.GET.get('search')
    dinosaurs = models.Dinosaur.objects.order_by('name')

    if search_key.isdigit():
        period = int(search_key)
        period_query = django_models.Q(period_start__gte=period, period_end__lte=period)
    else:
        period_query = django_models.Q(period__name__icontains=search_key)

    dinosaurs = dinosaurs.filter(
        django_models.Q(name__icontains=search_key) |
        django_models.Q(diet__name__icontains=search_key) |
        period_query |
        django_models.Q(lived_in__name__icontains=search_key) |
        django_models.Q(species__name__icontains=search_key)
    )

    return shortcuts.render(
        request,
        'partials/dinosaur_list.html',
        context=dict(
            dinosaurs=dinosaurs,
        )
    )


def dinosaur_list_next_10(request, page_number):
    dinosaurs = models.Dinosaur.objects.order_by('name')
    rows_per_page = 10
    if page_number * rows_per_page > dinosaurs.count():
        return http.HttpResponse('')

    return shortcuts.render(
        request,
        template_name='partials/dinosaur_list_page.html',
        context=dict(
            dinosaurs=dinosaurs[page_number * rows_per_page:(page_number + 1) * rows_per_page],
            next_page_number=page_number + 1
        )
    )


def dinosaur_favourites(request):
    dinosaurs = models.Dinosaur.objects.order_by('name').filter(ranking__isnull=True)[:15]
    favourite_dinosaurs = models.Dinosaur.objects.exclude(ranking__isnull=True).order_by('ranking')
    return shortcuts.render(
        request,
        template_name='dinosaur_favourites.html',
        context=dict(
            dinosaurs=dinosaurs,
            favourite_dinosaurs=favourite_dinosaurs
        )
    )


def update_dinosaur_favourites(request):
    ids = request.POST.getlist('item')
    separator_index = ids.index('separator')
    ids = ids[:separator_index]
    ranked_ids = [int(id) for id in ids]
    models.Dinosaur.objects.exclude(id__in=ranked_ids).update(ranking=None)
    for rank, id in enumerate(ranked_ids):
        dinosaur = models.Dinosaur.objects.get(id=id)
        dinosaur.ranking = rank
        dinosaur.save()

    return http.HttpResponse('')


def dinosaurs_by_diet(request):
    diets = models.Diet.objects.order_by('name')
    first_diet = diets.first()
    dinosaurs = first_diet.dinosaur_set.order_by('name')
    return shortcuts.render(
        request,
        'dinosaurs_by_diet.html',
        context=dict(
            diets=diets,
            active_diet=first_diet,
            dinosaurs=dinosaurs,
        )
    )


def set_dinosaurs_for_diet(request):
    diet_id = request.GET.get('diet_id')
    diets = models.Diet.objects.order_by('name')
    active_diet = models.Diet.objects.get(id=diet_id)
    dinosaurs = active_diet.dinosaur_set.order_by('name')
    return shortcuts.render(
        request,
        'partials/set_dinosaurs_for_diet.html',
        context=dict(
            diets=diets,
            active_diet=active_diet,
            dinosaurs=dinosaurs,
        )
    )


def dinosaurs_for_period(request):
    period_id = int(request.GET.get('period'))
    dinosaurs = models.Dinosaur.objects.all()
    if period_id != -1:
        dinosaurs = dinosaurs.filter(period_id=period_id)
    return shortcuts.render(
        request,
        'partials/dinosaur_list.html',
        context=dict(
            dinosaurs=dinosaurs,
        )
    )
