from app import db


dinosaur_diet = db.Table(
    'dinosaur_diet',
    db.Column('dinosaur_id', db.Integer, db.ForeignKey('dinosaur.id')),
    db.Column('diet_id', db.Integer, db.ForeignKey('diet.id'))
)


class Diet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))

    def __str__(self):
        return self.name


class Period(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    dinosaur = db.relationship('Dinosaur', back_populates='period')

    def __str__(self):
        return self.name


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))

    def __str__(self):
        return self.name

    def dinosaurs(self):
        return db.session.query(Dinosaur).filter(Dinosaur.lived_in_id == self.id).all()


def full_taxonomy(taxon):
    taxons = []
    while taxon:
        taxons.append(taxon)
        taxon = db.session.query(Taxon).get(taxon.parent_id) if taxon.parent_id else None
    return reversed(taxons)


class Taxon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('taxon.id'))
    parent = db.relationship('Taxon')
    name = db.Column(db.String(200))

    def __str__(self):
        return self.name

    def full_taxonomy(self):
        return full_taxonomy(self)


class Species(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    dinosaurs = db.relationship('Dinosaur')

    def __str__(self):
        return self.name


class Dinosaur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    diet = db.relationship('Diet', secondary=dinosaur_diet)
    period_id = db.Column(db.Integer, db.ForeignKey(Period.id))
    period = db.relationship('Period')
    period_start = db.Column(db.Integer)
    period_end = db.Column(db.Integer)
    lived_in_id = db.Column(db.Integer, db.ForeignKey(Location.id))
    length_in_cms = db.Column(db.Integer)
    taxonomy_id = db.Column(db.Integer, db.ForeignKey(Taxon.id))
    taxonomy = db.relationship('Taxon')
    species_id = db.Column(db.Integer, db.ForeignKey(Species.id))
    species = db.relationship('Species', overlaps="dinosaurs")
    ranking = db.Column(db.Integer)

    def __str__(self):
        taxonomy = ' -> '.join(taxon.name for taxon in self.full_taxonomy())
        return f'{self.name} ({self.period_start}-{self.period_end}), {taxonomy}'

    def full_taxonomy(self):
        return full_taxonomy(self.taxonomy)

    def diet_description(self):
        return '/'.join(diet.name for diet in self.diet)

    def period_description(self):
        parts = [self.period.name]
        if self.period_start is not None:
            if self.period_end is not None:
                parts.append(f'{self.period_start} - {self.period_end} million years ago')
            else:
                parts.append(f'{self.period_start} million years ago')
        return ' '.join(parts)
