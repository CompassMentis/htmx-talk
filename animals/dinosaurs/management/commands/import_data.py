import csv

from django.core.management.base import BaseCommand

from ... import models


class Command(BaseCommand):
    help = 'Imports the raw data (.csv) file from ../../data/data.csv'

    @staticmethod
    def delete_data():
        for model in (
                models.Dinosaur,
                models.Diet,
                models.Period,
                models.Location,
                models.Taxon,
                models.Species,
        ):
            model.objects.all().delete()
        print('Old data deleted')

    @staticmethod
    def process_diet(raw_diet):
        return [
            models.Diet.objects.get_or_create(name=name.strip())[0]
            for name in raw_diet.split('/')
        ]

    @staticmethod
    def process_species(species):
        if not species.strip():
            return None
        return models.Species.objects.get_or_create(name=species)[0]

    @staticmethod
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
        period, _ = models.Period.objects.get_or_create(name=period_name)
        return period, period_start, period_end

    @staticmethod
    def process_length(raw_length):
        if raw_length:
            return int(float(raw_length.replace('m', '')) * 100)
        return None

    @staticmethod
    def process_taxonomy(raw_taxonomy):
        parent = None
        for name in raw_taxonomy.split(' '):
            taxon = models.Taxon.objects.filter(name=name).first()
            if taxon:
                assert taxon.parent == parent
            else:
                taxon = models.Taxon.objects.create(
                    name=name,
                    parent=parent
                )
            parent = taxon

        return taxon  # noqa

    def import_one_dinosaur(self, csv_row):
        name, raw_diet, raw_period, lived_in_name, type_name, raw_length, raw_taxonomy, _, species, *ignore = csv_row
        diet = self.process_diet(raw_diet)
        period, period_start, period_end = self.process_period(raw_period)
        length = self.process_length(raw_length)
        lived_in, _ = models.Location.objects.get_or_create(name=lived_in_name)
        taxonomy = self.process_taxonomy(raw_taxonomy)
        species = self.process_species(species)
        dinosaur = models.Dinosaur.objects.create(
            name=name,
            period=period,
            period_start=period_start,
            period_end=period_end,
            lived_in=lived_in,
            length_in_cms=length,
            taxonomy=taxonomy,
            species=species,
        )
        dinosaur.diet.set(diet)
        dinosaur.save()
        print(name)

    def import_csv(self, source_file):
        with open(source_file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                self.import_one_dinosaur(row)
        print('File imported')

    def handle(self, *args, **options):
        self.delete_data()
        self.import_csv('../data/data.csv')
