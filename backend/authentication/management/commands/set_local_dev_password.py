from django.conf import settings
from backend.security_policy import local_fallback_allowed
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils.crypto import get_random_string


class Command(BaseCommand):
    help = (
        'Set or generate a local-only development password for an existing ISO Smart user. '
        'This does not update AdminApps.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True, help='User email to update.')
        parser.add_argument('--password', help='Explicit local password to set.')
        parser.add_argument(
            '--generate',
            action='store_true',
            help='Generate a strong temporary local password and print it once.',
        )
        parser.add_argument(
            '--confirm-local',
            action='store_true',
            help='Required when settings look production-like.',
        )
        parser.add_argument(
            '--must-change-password',
            action='store_true',
            help='Mark the local password as temporary so the user must change it after login.',
        )

    def handle(self, *args, **options):
        password = options.get('password')
        generate = options.get('generate')

        if bool(password) == bool(generate):
            raise CommandError('Use exactly one option: --password or --generate.')

        if not local_fallback_allowed(settings, True):
            raise CommandError('Local password fixtures are restricted to explicit test/demo environments.')

        user_model = get_user_model()
        email = options['email'].strip().lower()
        try:
            user = user_model.objects.get(email=email)
        except user_model.DoesNotExist as exc:
            raise CommandError(f'User not found: {email}') from exc

        if generate:
            password = get_random_string(
                24,
                allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789!@$%',
            )

        user.set_password(password)
        user.failed_login_attempts = 0
        user.account_locked_until = None
        if options.get('must_change_password'):
            user.mark_temporary_password()
        else:
            user.clear_temporary_password_flag()
        user.save(
            update_fields=[
                'password',
                'failed_login_attempts',
                'account_locked_until',
                'must_change_password',
                'temporary_password_set_at',
            ]
        )

        self.stdout.write(self.style.SUCCESS(f'Local password enabled for {email}.'))
        self.stdout.write('AdminApps password was not changed.')
        if generate:
            self.stdout.write(f'Generated local password: {password}')
