from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("reports", "0001_initial"),
        ("applications", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="purchase",
            name="request",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="purchase",
                to="applications.request",
            ),
        ),
        migrations.AddField(
            model_name="purchase",
            name="actual_cost",
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AddField(
            model_name="purchase",
            name="purchase_date",
            field=models.DateField(),
        ),
        migrations.AddField(
            model_name="purchase",
            name="funding_source",
            field=models.CharField(max_length=255),
        ),
        migrations.AddField(
            model_name="purchase",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="purchases",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RemoveField(
            model_name="purchase",
            name="amount",
        ),
        migrations.RemoveField(
            model_name="purchase",
            name="source",
        ),
        migrations.RemoveField(
            model_name="purchase",
            name="title",
        ),
    ]
