"""empty message

Revision ID: aade508315bf
Revises: 
Create Date: 2023-02-14 12:37:33.536098

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aade508315bf'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('diet',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_diet'))
    )
    op.create_table('location',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_location'))
    )
    op.create_table('period',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_period'))
    )
    op.create_table('species',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_species'))
    )
    op.create_table('taxon',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=200), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['taxon.id'], name=op.f('fk_taxon_parent_id_taxon')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_taxon'))
    )
    op.create_table('dinosaur',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=True),
    sa.Column('period_id', sa.Integer(), nullable=True),
    sa.Column('period_start', sa.Integer(), nullable=True),
    sa.Column('period_end', sa.Integer(), nullable=True),
    sa.Column('lived_in_id', sa.Integer(), nullable=True),
    sa.Column('length_in_cms', sa.Integer(), nullable=True),
    sa.Column('taxonomy_id', sa.Integer(), nullable=True),
    sa.Column('species_id', sa.Integer(), nullable=True),
    sa.Column('ranking', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['lived_in_id'], ['location.id'], name=op.f('fk_dinosaur_lived_in_id_location')),
    sa.ForeignKeyConstraint(['period_id'], ['period.id'], name=op.f('fk_dinosaur_period_id_period')),
    sa.ForeignKeyConstraint(['species_id'], ['species.id'], name=op.f('fk_dinosaur_species_id_species')),
    sa.ForeignKeyConstraint(['taxonomy_id'], ['taxon.id'], name=op.f('fk_dinosaur_taxonomy_id_taxon')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_dinosaur'))
    )
    op.create_table('dinosaur_diet',
    sa.Column('dinosaur_id', sa.Integer(), nullable=True),
    sa.Column('diet_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['diet_id'], ['diet.id'], name=op.f('fk_dinosaur_diet_diet_id_diet')),
    sa.ForeignKeyConstraint(['dinosaur_id'], ['dinosaur.id'], name=op.f('fk_dinosaur_diet_dinosaur_id_dinosaur'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('dinosaur_diet')
    op.drop_table('dinosaur')
    op.drop_table('taxon')
    op.drop_table('species')
    op.drop_table('period')
    op.drop_table('location')
    op.drop_table('diet')
    # ### end Alembic commands ###