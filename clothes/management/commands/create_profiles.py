from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from clothes.models import UserProfile

class Command(BaseCommand):
    help = 'Create UserProfiles for existing users who do not have one'

    def handle(self, *args, **options):
        users_without_profile = User.objects.filter(userprofile__isnull=True)
        created_count = 0
        
        for user in users_without_profile:
            UserProfile.objects.create(
                user=user,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email
            )
            created_count += 1
            self.stdout.write(f'Created profile for user: {user.username}')
        
        if created_count == 0:
            self.stdout.write(
                self.style.SUCCESS('All users already have profiles!')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {created_count} user profiles')
            )
