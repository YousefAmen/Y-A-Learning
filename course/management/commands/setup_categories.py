from django.core.management.base import BaseCommand, CommandError
from course.models import Category, CHOICES_CATEGORIES


class Command(BaseCommand):
    help = "setup / adding main categories"

    def handle(self, *args, **options):

        try:
            for category_value, category_lable in CHOICES_CATEGORIES:
                obj, created = Category.objects.get_or_create(name=category_value)
                if created:
                    self.stdout.write(f"Added {category_lable} successfully.")
                else:
                    self.stdout.write(f"Allready Exists {category_lable}")

            self.stdout.write("setup categories is compleated successfully.")
        except Exception as ex:
            raise CommandError(f"error {ex}")
