# Generated by Django 3.2.3 on 2024-11-20 21:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_alter_favoriterecipe_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipeingredient',
            options={},
        ),
        migrations.RemoveConstraint(
            model_name='recipeingredient',
            name='unique ingredient',
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='recipes.ingredient', verbose_name='Ингредиент'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe'),
        ),
    ]
