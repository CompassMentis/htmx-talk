from django.db import models


class Diet(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Period(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


def full_taxonomy(taxon):
    taxons = []
    while taxon:
        taxons.append(taxon)
        taxon = taxon.parent
    return reversed(taxons)


class Taxon(models.Model):
    name = models.CharField(max_length=200)
    parent = models.ForeignKey('dinosaurs.Taxon', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def full_taxonomy(self):
        return full_taxonomy(self)


class Species(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Dinosaur(models.Model):
    name = models.CharField(max_length=200)
    diet = models.ManyToManyField(Diet)
    period = models.ForeignKey(Period, on_delete=models.PROTECT)
    period_start = models.IntegerField(null=True)
    period_end = models.IntegerField(null=True)
    lived_in = models.ForeignKey(Location, on_delete=models.PROTECT)
    length_in_cms = models.IntegerField(null=True)
    taxonomy = models.ForeignKey(Taxon, null=True, on_delete=models.PROTECT)
    species = models.ForeignKey(Species, null=True, on_delete=models.PROTECT)
    ranking = models.IntegerField(null=True, blank=True)

    def __str__(self):
        taxonomy = ' -> '.join(taxon.name for taxon in self.full_taxonomy())
        return f'{self.name} ({self.period_start}-{self.period_end}), {taxonomy}'

    def full_taxonomy(self):
        return full_taxonomy(self.taxonomy)

    def diet_description(self):
        return '/'.join(diet.name for diet in self.diet.all())

    def period_description(self):
        parts = [self.period.name]
        if self.period_start is not None:
            if self.period_end is not None:
                parts.append(f'{self.period_start} - {self.period_end} million years ago')
            else:
                parts.append(f'{self.period_start} million years ago')
        return ' '.join(parts)
