# Generated manually - Rename tables to clear names using SQL
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0003_classe_groupe_customuser_groupe_schedule_groupe'),
    ]

    operations = [
        # Rename tables using raw SQL - this actually renames in MySQL
        migrations.RunSQL(
            sql="""
                RENAME TABLE accounts_customuser TO users;
                RENAME TABLE accounts_schedule TO emplois_du_temps;
                RENAME TABLE accounts_classe TO classes;
                RENAME TABLE accounts_groupe TO groupes;
            """,
            reverse_sql="""
                RENAME TABLE users TO accounts_customuser;
                RENAME TABLE emplois_du_temps TO accounts_schedule;
                RENAME TABLE classes TO accounts_classe;
                RENAME TABLE groupes TO accounts_groupe;
            """
        ),
        # Also update Django's table config
        migrations.AlterModelTable(
            name='customuser',
            table='users',
        ),
        migrations.AlterModelTable(
            name='schedule',
            table='emplois_du_temps',
        ),
        migrations.AlterModelTable(
            name='classe',
            table='classes',
        ),
        migrations.AlterModelTable(
            name='groupe',
            table='groupes',
        ),
    ]
