import csv

from app import app, db
from app import models

app.app_context().push()


def delete_data():
    for model in (
            models.Dinosaur,
            models.Diet,
            models.Period,
            models.Location,
            models.Taxon,
            models.Species,
    ):
        for row in model.query.all():
            db.session.delete(row)
    db.session.commit()


def get_or_create(model, name):
    s = db.session.query(model).filter(model.name == name).one_or_none()
    if s:
        return s

    s = model(name=name)
    db.session.add(s)
    db.session.commit()
    return s


def process_species(species):
    return get_or_create(models.Species, species)


def process_period(raw_period):
    # Early Cretaceous 127-121 million years ago
    # or Late Cretaceous 69 million years ago
    # or just Early Jurassic
    parts = raw_period.split()
    if len(parts) == 2:
        period_name = raw_period
        period_start = None
        period_end = None
    else:
        period_name = ' '.join(parts[:2])
        start_end = parts[2]
        if '-' in start_end:
            period_start, period_end = [int(n) for n in start_end.split('-')]
        else:
            period_start = period_end = int(start_end)
    period = get_or_create(models.Period, period_name)
    return period, period_start, period_end


def process_location(name):
    return get_or_create(models.Location, name)


def process_length(raw_length):
    if raw_length:
        return int(float(raw_length.replace('m', '')) * 100)
    return None


def process_taxonomy(raw_taxonomy):
    parent = None
    for name in raw_taxonomy.split(' '):
        taxon = db.session.query(models.Taxon).filter(models.Taxon.name == name).one_or_none()
        parent_id = parent.id if parent else None
        if taxon:
            assert taxon.parent_id == parent_id
        else:
            taxon = models.Taxon(
                name=name,
                parent_id=parent_id
            )
            db.session.add(taxon)
            db.session.commit()
        parent = taxon

    return taxon  # noqa


def process_diet(raw_diet):
    return [
        get_or_create(models.Diet, name.strip())
        for name in raw_diet.split('/')
    ]


def import_one_dinosaur(csv_row):
    name, raw_diet, raw_period, lived_in_name, type_name, raw_length, raw_taxonomy, _, species, *ignore = csv_row
    diets = process_diet(raw_diet)
    period, period_start, period_end = process_period(raw_period)
    length = process_length(raw_length)
    lived_in = process_location(name=lived_in_name)
    taxonomy = process_taxonomy(raw_taxonomy)
    species = process_species(species)
    dinosaur = models.Dinosaur(
        name=name,
        period_id=period.id,
        period_start=period_start,
        period_end=period_end,
        lived_in_id=lived_in.id,
        length_in_cms=length,
        taxonomy_id=taxonomy.id,
        species_id=species.id,
    )
    for diet in diets:
        dinosaur.diet.append(diet)
    db.session.add(dinosaur)
    db.session.commit()
    print(name)


def import_csv(source_file):
    with open(source_file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            import_one_dinosaur(row)
    print('File imported')

delete_data()
import_csv('../data/data.csv')
