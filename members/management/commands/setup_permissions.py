from django.core.management.base import BaseCommand, CommandError
from ...models import Instructor
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):

    help = "Setup user groups and permissions"

    def handle(self, *args, **options):

        groups_permissions = {
            "Instructors": [
                ("course", "course", ["add", "change", "delete", "view"]),
                ("course", "module", ["add", "change", "delete", "view"]),
                ("course", "lesson", ["add", "change", "delete", "view"]),
                ("course", "learningoutcomes", ["add", "change", "delete", "view"]),
                ("members", "sociallinks", ["add", "change", "delete", "view"]),
            ],
        }

        for group_name, permission_list in groups_permissions.items():
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(f"Created Group: {group_name}")
            else:
                self.stdout.write(f"Group Exists: {group_name}")

            group.permissions.clear()

            for app_label, model_name, actions in permission_list:
                # try to catch contenttype
                try:
                    content_type = ContentType.objects.get(
                        app_label=app_label, model=model_name
                    )
                    for action in actions:
                        codename = f"{action}_{model_name}"
                        permission = Permission.objects.get(
                            content_type=content_type, codename=codename
                        )
                        group.permissions.add(permission)
                        self.stdout.write(
                            self.style.SUCCESS(f"Added {codename} to {group_name}'")
                        )

                except ContentType.DoesNotExist as er:

                    raise CommandError(f"There's No Contenttype With This Name {er}")
        self.stdout.write(self.style.SUCCESS("Stupe Is Complete!"))
