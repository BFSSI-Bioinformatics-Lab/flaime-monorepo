import re
from collections import defaultdict

from django.db import migrations

"""
Drop duplicate foreign key constraints, keeping one per column.

Most FK columns carry two or three identical constraints: the original .NET ones
(FK_<table>_<target>_<column>), lowercase copies added by 0016 (its DROP/ADD did not
quote the names, so it created fk_... instead of replacing FK_...), and others with
Postgres default names (<table>_<column>_fkey). They behave identically, but each
one fires its own trigger on every insert, update and delete, and Django cannot
alter a field that has more than one.

Constraints are grouped by (table, columns, referenced table, referenced columns).
A group is only reduced when every member has the same definition; a group whose
members differ (e.g. different ON DELETE) is left alone and reported. The name
kept, in order of preference: Django's, then <table>_<column>_fkey, then fk_...,
then FK_....
"""

DJANGO_NAME = re.compile(r"_[0-9a-f]{8}_fk_")


def rank(name):
    if DJANGO_NAME.search(name):
        return 0
    if name.endswith("_fkey"):
        return 1
    if name.startswith("fk_"):
        return 2
    return 3


def drop_duplicates(apps, schema_editor):
    qn = schema_editor.quote_name
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            SELECT t.relname, c.conname, pg_get_constraintdef(c.oid),
                   c.conrelid, c.conkey, c.confrelid, c.confkey
            FROM pg_constraint c JOIN pg_class t ON t.oid = c.conrelid
            WHERE c.contype = 'f' AND c.connamespace = 'public'::regnamespace
            ORDER BY t.relname, c.conname
        """)
        groups = defaultdict(list)
        for table, name, definition, relid, key, frelid, fkey in cursor.fetchall():
            groups[(relid, tuple(key), frelid, tuple(fkey))].append((table, name, definition))

        dropped = 0
        for members in groups.values():
            if len(members) < 2:
                continue
            if len({definition for _, _, definition in members}) > 1:
                print(f"\n  Left alone (definitions differ): {members[0][0]}: "
                      + "; ".join(f"{name} = {definition}" for _, name, definition in members))
                continue
            keep = min(members, key=lambda m: (rank(m[1]), m[1]))
            for table, name, _ in members:
                if name != keep[1]:
                    cursor.execute(f"ALTER TABLE {qn(table)} DROP CONSTRAINT {qn(name)}")
                    dropped += 1
        print(f"\n  Dropped {dropped} duplicate foreign key constraint(s)")


class Migration(migrations.Migration):

    dependencies = [
        ('food_labels', '0041_nutrient_sort_order'),
    ]

    operations = [
        migrations.RunPython(drop_duplicates, migrations.RunPython.noop),
    ]
