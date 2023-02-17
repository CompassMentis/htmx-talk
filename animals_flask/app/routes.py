from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import file_html
from flask import render_template
from flask import request
from sqlalchemy import func

from app import app
from app import db
from app import models


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/locations')
def locations():
    return render_template(
        'locations.html',
        locations=all_rows(models.Location)
    )


@app.route('/edit_location/<id>')
def edit_location(id):
    location = db.session.query(models.Location).get(id)
    return render_template(
        'partials/edit_location.html',
        location=location
    )


@app.route('/view_location/<id>')
def view_location(id):
    location = db.session.query(models.Location).get(id)
    return render_template(
        'partials/single_location.html',
        location=location
    )


@app.route('/update_location/<id>', methods=['POST'])
def update_location(id):
    location = db.session.query(models.Location).get(id)
    # TODO: Also handle empty name entry
    # TODO: Is there a better way to get the name?
    name = [n for n in request.form.getlist('name') if n][0]
    location.name = name
    db.session.commit()
    return render_template(
        'partials/single_location.html',
        location=location
    )


@app.route('/delete_location/<id>', methods=['DELETE'])
def delete_location(id):
    location = db.session.query(models.Location).get(id)
    db.session.delete(location)
    db.session.commit()
    return render_template(
        'partials/deleted_location.html',
        location=location
    )


@app.route('/create_location')
def create_location():
    return render_template(
        'partials/create_location.html'
    )


@app.route('/save_new_location', methods=['POST'])
def save_new_location():
    # TODO: Is there a better way to get the name?
    name = [n for n in request.form.getlist('name') if n][0]
    location = models.Location(name=name)
    db.session.add(location)
    db.session.commit()
    return render_template(
        'partials/locations_list.html',
        locations=all_rows(models.Location)
    )


def dinosaur_chart_html(start, end):
    count = {n: 0 for n in range(end, start + 1)}
    for dinosaur in db.session.query(models.Dinosaur).all():
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


@app.route('/dinosaur_chart')
def dinosaur_chart():
    # TODO: tidy up start/end, handling of 'years ago'
    """
        For each 'year' between first and last, calculate the number of known dinosaur species
    """
    start_end = db.session.query(
        func.max(models.Dinosaur.period_start).label('start'),
        func.min(models.Dinosaur.period_end).label('end')
    ).one()
    start = start_end.start
    end = start_end.end
    chart_html = dinosaur_chart_html(start, end)
    return render_template(
        'dinosaur_chart.html',
        chart=chart_html,
        period_start=start,
        period_end=end,
    )


@app.route('/dinosaur_chart_partial')
def dinosaur_chart_partial():
    print(request)
    start = int(request.args.get('start'))
    end = int(request.args.get('end'))
    return dinosaur_chart_html(start, end)


@app.route('/dinosaurs')
def dinosaurs():
    dinosaurs = all_rows(models.Dinosaur)
    dinosauria_taxon = db.session.query(models.Taxon).filter(models.Taxon.parent_id == None).one()
    taxons = db.session.query(models.Taxon).filter(models.Taxon.parent_id == dinosauria_taxon.id).order_by('name')
    return render_template(
        'dinosaurs.html',
        taxons=taxons,
        dinosaurs=dinosaurs
    )


@app.route('/update_dinosaurs_from_selection')
def update_dinosaurs_from_selection():
    # -1: all, -2: no value
    taxon_ids = [
        int(request.args.get(f'taxon_id_{level}', -2))
        for level in [1, 2, 3]
    ]
    select_level = int(request.args.get('select_level'))

    id = taxon_ids[select_level - 1]
    if id == -1:
        select_level -= 1
        if select_level > 0:
            id = taxon_ids[select_level - 1]

    context = {}
    context['level'] = select_level

    if select_level > 0:
        selected_taxon = db.session.query(models.Taxon).get(id)
        context['dinosaurs'] = [
            dinosaur
            for dinosaur in all_rows(models.Dinosaur)
            if selected_taxon in dinosaur.full_taxonomy()
        ]
        context['sub_taxons'] = db.session.query(models.Taxon).filter(models.Taxon.parent_id == selected_taxon.id).order_by('name').all()
        context['filter_description'] = ' -> '.join(taxon.name for taxon in selected_taxon.full_taxonomy())
    else:
        context['dinosaurs'] = all_rows(models.Dinosaur)
        context['filter_description'] = 'All dinosaurs'

    return render_template(
        'partials/dinosaur_list_plus_dropdown.html',
        **context
    )


@app.route('/dinosearch')
def dinosearch():
    return render_template(
        'dinosearch.html',
        dinosaurs=all_rows(models.Dinosaur),
        types=['all', 'name', 'diet', 'period', 'location', 'species'],
    )


def dinosaurs_for_search_key(search_key):
    if search_key.isdigit():
        period = int(search_key)
        return (
                db.session.query(models.Dinosaur)
                .filter(models.Dinosaur.period_start >= period)
                .filter(models.Dinosaur.period_end <= period)
                .order_by('name')
                .all()
        )

    # Todo: Also search in diet, lived_in and species
    return db.session.query(models.Dinosaur).filter(
        func.lower(models.Dinosaur.name).contains(search_key)
    ).order_by('name').all()


@app.route('/dinosearch_list')
def dinosearch_list():
    search_key = request.args.get('search').lower()
    dinosaurs = dinosaurs_for_search_key(search_key)

    return render_template(
        'partials/dinosaur_list.html',
        dinosaurs=dinosaurs,
    )


@app.route('/scrolling_dinosaur_list')
def scrolling_dinosaur_list():
    return render_template(
        'scrolling_dinosaur_list.html'
    )


@app.route('/dinosaur_page_list/<page_number>')
def dinosaur_list_next_10(page_number=0):
    dinosaurs = all_rows(models.Dinosaur)
    rows_per_page = 10
    page_number = int(page_number)
    if page_number * rows_per_page > len(dinosaurs):
        return ''

    return render_template(
        'partials/dinosaur_list_page.html',
        dinosaurs=dinosaurs[page_number * rows_per_page:(page_number + 1) * rows_per_page],
        next_page_number=page_number + 1
    )


@app.route('/dinosaur_favourites')
def dinosaur_favourites():
    dinosaurs = db.session.query(models.Dinosaur).filter(models.Dinosaur.ranking == None)[:15]
    favourite_dinosaurs = db.session.query(models.Dinosaur).filter(models.Dinosaur.ranking != None).order_by(models.Dinosaur.ranking)
    return render_template(
        'dinosaur_favourites.html',
        dinosaurs=dinosaurs,
        favourite_dinosaurs=favourite_dinosaurs
    )


@app.route('/update_dinosaur_favourites', methods=['POST'])
def update_dinosaur_favourites():
    ids = request.form.getlist('item')
    separator_index = ids.index('separator')
    ids = ids[:separator_index]
    ranked_ids = [int(id) for id in ids]
    for dinosaur in db.session.query(models.Dinosaur).filter(models.Dinosaur.id.not_in(ids)):
        dinosaur.ranking = None
    for rank, id in enumerate(ranked_ids):
        dinosaur = db.session.query(models.Dinosaur).get(id)
        dinosaur.ranking = rank

    db.session.commit()
    return ''


def dinosaurs_for_diet(diet):
    return (
        db.session.query(models.Dinosaur)
        .join(models.dinosaur_diet)
        .filter(models.dinosaur_diet.columns.diet_id == diet.id)
        .order_by('name')
        .all()
    )


@app.route('/dinosaurs_by_diet')
def dinosaurs_by_diet():
    diets = all_rows(models.Diet)
    first_diet = diets[0]
    dinosaurs = dinosaurs_for_diet(first_diet)
    return render_template(
        'dinosaurs_by_diet.html',
        diets=diets,
        active_diet=first_diet,
        dinosaurs=dinosaurs,
    )


@app.route('/about')
def about():
    return render_template(
        'about.html'
    )


@app.route('/set_dinosaurs_for_diet')
def set_dinosaurs_for_diet():
    diet_id = request.args.get('diet_id')
    diets = all_rows(models.Diet)
    active_diet = db.session.query(models.Diet).get(diet_id)
    dinosaurs = dinosaurs_for_diet(active_diet)
    return render_template(
        'partials/set_dinosaurs_for_diet.html',
        diets=diets,
        active_diet=active_diet,
        dinosaurs=dinosaurs,
    )


def all_rows(model):
    return db.session.query(model).order_by(model.name).all()


@app.route('/dinosaurs_by_period')
def dinosaurs_by_period():
    return render_template(
        'dinosaurs_by_period.html',
        periods=db.session.query(models.Period).all(),
        dinosaurs=all_rows(models.Dinosaur)
    )


@app.route('/dinosaurs_for_period')
def dinosaurs_for_period():
    period_id = int(request.args.get('period'))
    if period_id != -1:
        dinosaurs = db.session.query(models.Dinosaur).filter(models.Dinosaur.period_id == period_id).order_by(models.Dinosaur.name).all()
    else:
        dinosaurs = all_rows(models.Dinosaur)
    return render_template(
        'partials/dinosaur_list.html',
        dinosaurs=dinosaurs,
    )
