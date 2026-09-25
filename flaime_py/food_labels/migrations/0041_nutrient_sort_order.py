from django.db import migrations, models

"""
Nutrient display order: the order nutrients appear in a Canadian nutrition facts table.
Ported from flaime_py branch origin/nft_order_QC (Yuyoung Kim). That branch set the
values by the old USDA-style names, which the FSDH migration renamed, so the values
here are the ones in the FSDH database as of 2026-09-25, keyed by nutrient id.
Nutrients with no place on the table (amino acids, caffeine, taurine) stay NULL and
sort last.
"""

SORT_ORDER = {
    208: 0,  # Calories
    268: 0,  # Kilojoules
    204: 1,  # Total Fat
    606: 2,  # Saturated Fat
    607: 2,  # FATTY ACIDS, SATURATED, 4:0, BUTANOIC
    608: 2,  # FATTY ACIDS, SATURATED, 6:0, HEXANOIC
    609: 2,  # FATTY ACIDS, SATURATED, 8:0, OCTANOIC
    610: 2,  # FATTY ACIDS, SATURATED, 10:0, DECANOIC
    611: 2,  # FATTY ACIDS, SATURATED, 12:0, DODECANOIC
    612: 2,  # FATTY ACIDS, SATURATED, 14:0, TETRADECANOIC
    613: 2,  # FATTY ACIDS, SATURATED, 16:0, HEXADECANOIC
    614: 2,  # FATTY ACIDS, SATURATED, 18:0, OCTADECANOIC
    615: 2,  # FATTY ACIDS, SATURATED, 20:0, EICOSANOIC
    624: 2,  # FATTY ACIDS, SATURATED, 22:0, DOCOSANOIC
    652: 2,  # FATTY ACIDS, SATURATED, 15:0, PENTADECANOIC
    653: 2,  # FATTY ACIDS, SATURATED, 17:0, HEPTADECANOIC
    654: 2,  # FATTY ACIDS, SATURATED, 24:0, TETRACOSANOIC
    830: 2,  # FATTY ACIDS, SATURATED, 13:0 TRIDECANOIC
    605: 3,  # Trans Fat
    829: 3,  # FATTY ACIDS, TOTAL TRANS-MONOENOIC
    859: 3,  # FATTY ACIDS, TOTAL TRANS-POLYENOIC
    2015: 3, # FATTY ACIDS, SATURATED + TRANS, TOTAL
    618: 4,  # FATTY ACIDS, POLYUNSATURATED, 18:2undifferentiated, LINOLEIC, OCTADECADIENOIC
    619: 4,  # FATTY ACIDS, POLYUNSATURATED, 18:3undifferentiated, LINOLENIC, OCTADECATRIENOIC
    620: 4,  # FATTY ACIDS, POLYUNSATURATED, 20:4, EICOSATETRAENOIC
    621: 4,  # FATTY ACIDS, POLYUNSATURATED, 22:6 n-3, DOCOSAHEXAENOIC (DHA)
    627: 4,  # FATTY ACIDS, POLYUNSATURATED, 18:4, OCTADECATETRAENOIC
    629: 4,  # FATTY ACIDS, POLYUNSATURATED, 20:5 n-3, EICOSAPENTAENOIC (EPA)
    631: 4,  # FATTY ACIDS, POLYUNSATURATED, 22:5 n-3, DOCOSAPENTAENOIC (DPA)
    646: 4,  # Polyunsaturated Fat
    819: 4,  # FATTY ACIDS, POLYUNSATURATED, 18:2i, LINOLEIC, OCTADECADIENOIC
    823: 4,  # FATTY ACIDS, POLYUNSATURATED, 20:2 c,c  EICOSADIENOIC
    825: 4,  # FATTY ACIDS, POLYUNSATURATED, 18:2 c,c n-6,  LINOLEIC, OCTADECADIENOIC
    827: 4,  # FATTY ACIDS, POLYUNSATURATED, 20:3, EICOSATRIENOIC
    831: 4,  # FATTY ACIDS, POLYUNSATURATED, 18:3 c,c,c n-3  LINOLENIC, OCTADECATRIENOIC
    832: 4,  # FATTY ACIDS, POLYUNSATURATED, 18:3 c,c,c n-6, g-LINOLENIC, OCTADECATRIENOIC
    838: 4,  # FATTY ACIDS, POLYUNSATURATED, CONJUGATED, 18:2 cla, LINOLEIC, OCTADECADIENOIC
    839: 4,  # FATTY ACIDS, POLYUNSATURATED, 18:2t NOT FURTHER DEFINED, LINOLEIC, OCTADECADIENOIC
    841: 4,  # FATTY ACIDS, POLYUNSATURATED, 18:3i, LINOLENIC, OCTADECATRIENOIC
    843: 4,  # FATTY ACIDS, POLYUNSATURATED, 21:5
    845: 4,  # FATTY ACIDS, POLYUNSATURATED, 22:4 n-6, DOCOSATETRAENOIC
    848: 4,  # FATTY ACIDS, POLYUNSATURATED, 22:3,
    849: 4,  # FATTY ACIDS, POLYUNSATURATED, 22:2, DOCOSADIENOIC
    853: 4,  # FATTY ACIDS, POLYUNSATURATED, 18:2t,t , OCTADECADIENENOIC
    854: 4,  # FATTY ACIDS, POLYUNSATURATED, 20:3 n-6, EICOSATRIENOIC
    855: 4,  # FATTY ACIDS, POLYUNSATURATED, 20:4 n-6, ARACHIDONIC
    861: 4,  # FATTY ACIDS, POLYUNSATURATED, 20:3 n-3 EICOSATRIENOIC
    906: 4,  # FATTY ACIDS, POLYUNSATURATED, 18:2 9c,13c
    907: 4,  # FATTY ACIDS, POLYUNSATURATED, 18:2 9c,14c
    908: 4,  # FATTY ACIDS, POLYUNSATURATED, 18:2 9c,15c
    909: 4,  # FATTY ACIDS, POLYUNSATURATED, 22:5n-6
    869: 5,  # Omega-6
    868: 6,  # Omega-3
    617: 7,  # FATTY ACIDS, MONOUNSATURATED, 18:1undifferentiated, OCTADECENOIC
    625: 7,  # FATTY ACIDS, MONOUNSATURATED, 14:1, TETRADECENOIC
    626: 7,  # FATTY ACIDS, MONOUNSATURATED, 16:1undifferentiated, HEXADECENOIC
    628: 7,  # FATTY ACIDS, MONOUNSATURATED, 20:1, EICOSENOIC
    630: 7,  # FATTY ACIDS, MONOUNSATURATED, 22:1undifferentiated, DOCOSENOIC
    645: 7,  # Monounsaturated Fat
    817: 7,  # FATTY ACIDS, MONOUNSATURATED, 16:1t, HEXADECENOIC
    818: 7,  # FATTY ACIDS, MONOUNSATURATED, 18:1t, OCTADECENOIC
    820: 7,  # FATTY ACIDS, MONOUNSATURATED, 24:1c, TETRACOSENOIC
    821: 7,  # FATTY ACIDS, MONOUNSATURATED, 16:1c, HEXADECENOIC
    824: 7,  # FATTY ACIDS, MONOUNSATURATED, 18:1c, OCTADECENOIC
    826: 7,  # FATTY ACIDS, MONOUNSATURATED, 17:1, HEPTADECENOIC
    833: 7,  # FATTY ACIDS, MONOUNSATURATED, 15:1, PENTADECENOIC
    840: 7,  # FATTY ACIDS, MONOUNSATURATED, 22:1c, DOCOSENOIC
    846: 7,  # FATTY ACIDS, MONOUNSATURATED,  24:1undifferentiated, TETRACOSENOIC
    847: 7,  # FATTY ACIDS, MONOUNSATURATED, 12:1, LAUROLEIC
    852: 7,  # FATTY ACIDS, MONOUNSATURATED, 22:1t, DOCOSENOIC
    884: 7,  # FATTY ACIDS, MONOUNSATURATED, 18:1 10c
    885: 7,  # FATTY ACIDS, MONOUNSATURATED, 18:1 11c
    886: 7,  # FATTY ACIDS, MONOUNSATURATED, 18:1 12c
    888: 7,  # FATTY ACIDS, MONOUNSATURATED, 18:1 13c
    891: 7,  # FATTY ACIDS, MONOUNSATURATED, 18:1 14c
    895: 7,  # FATTY ACIDS, MONOUNSATURATED, 18:1 15c
    896: 7,  # FATTY ACIDS, MONOUNSATURATED, 18:1 16c
    897: 7,  # FATTY ACIDS, MONOUNSATURATED, 18:1 11t
    898: 7,  # FATTY ACIDS, MONOUNSATURATED, 18:1 4t
    899: 7,  # FATTY ACIDS, MONOUNSATURATED, 18:1 5t
    900: 7,  # FATTY ACIDS, MONOUNSATURATED, 18:1 6t-8t
    901: 7,  # FATTY ACIDS, MONOUNSATURATED, 18:1 10t
    902: 7,  # FATTY ACIDS, MONOUNSATURATED, 18:1 12t
    904: 7,  # FATTY ACIDS, MONOUNSATURATED, 18:1 16t
    905: 7,  # FATTY ACIDS, MONOUNSATURATED, 20:1 5c
    205: 8,  # Total Carbohydrate
    2009: 8, # OTHERCARBOHYDRATES
    291: 9,  # Fibre
    916: 9,  # INULIN
    2010: 9, # POLYDEXTROSE
    2013: 10,# Soluble Fibre
    273: 11, # Insoluble Fibre
    210: 12, # SUCROSE
    211: 12, # GLUCOSE
    212: 12, # FRUCTOSE
    213: 12, # LACTOSE
    214: 12, # MALTOSE
    269: 12, # Sugars
    287: 12, # GALACTOSE
    917: 12, # Sugars, total including NLEA
    260: 13, # MANNITOL
    261: 13, # SORBITOL
    2003: 13,# ERYTHRITOL
    2006: 13,# ISOMALT
    2007: 13,# MALTITOL
    2011: 13,# Sugar Alcohols
    2012: 13,# XYLITOL
    810: 14, # Starch
    203: 15, # Protein
    601: 16, # Cholesterol
    307: 17, # Sodium
    306: 18, # Potassium
    301: 19, # Calcium
    303: 20, # Iron
    319: 21, # RETINOL
    321: 21, # BETA CAROTENE
    814: 21, # RETINOL ACTIVITY EQUIVALENTS
    834: 21, # ALPHA CAROTENE
    835: 21, # BETA CRYPTOXANTHIN
    2016: 21,# Vitamin A
    401: 22, # Vitamin C
    339: 23, # Vitamin D
    323: 24, # ALPHA-TOCOPHEROL
    340: 24, # Vitamin E
    875: 24, # ALPHA-TOCOPHEROL, ADDED
    2014: 25,# Vitamin K
    404: 26, # Thiamine
    405: 27, # Riboflavin
    406: 28, # Niacin
    409: 28, # TOTAL NIACIN EQUIVALENT
    415: 29, # Vitamin B6
    417: 30, # TOTAL FOLACIN
    431: 30, # FOLIC ACID
    815: 30, # Folate
    418: 31, # Vitamin B12
    416: 32, # Biotin
    410: 33, # Pantothenic Acid
    862: 34, # Choline
    305: 35, # Phosphorus
    2005: 36,# Iodide
    304: 37, # Magnesium
    309: 38, # Zinc
    317: 39, # Selenium
    312: 40, # Copper
    315: 41, # Manganese
    2002: 42,# Chromium
    2008: 43,# Molybdenum
    2001: 44,# Chloride
}


def populate(apps, schema_editor):
    Nutrient = apps.get_model('food_labels', 'Nutrient')
    for nutrient_id, order in SORT_ORDER.items():
        Nutrient.objects.filter(id=nutrient_id).update(sort_order=order)


def unpopulate(apps, schema_editor):
    apps.get_model('food_labels', 'Nutrient').objects.update(sort_order=None)


class Migration(migrations.Migration):

    dependencies = [
        ('food_labels', '0040_category_unique_together_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='nutrient',
            name='sort_order',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterModelOptions(
            name='nutrient',
            options={'managed': True, 'ordering': ['sort_order', 'name'], 'verbose_name': 'Nutrient', 'verbose_name_plural': 'Nutrients'},
        ),
        migrations.RunPython(populate, unpopulate),
    ]
