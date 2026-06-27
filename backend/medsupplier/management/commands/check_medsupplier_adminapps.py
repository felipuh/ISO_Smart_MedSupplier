from django.core.management.base import BaseCommand, CommandError

from core.models import Organization
from integration.client import admin_apps_client
from medsupplier.models import MedSupplierUserScope


class Command(BaseCommand):
    help = 'Smoke check AdminApps entitlement and local MedSupplier scope fallback.'

    def add_arguments(self, parser):
        parser.add_argument('--organization-slug', default='medsupplier-demo-e2e')
        parser.add_argument('--organization-id', type=int, default=None)

    def handle(self, *args, **options):
        if options['organization_id']:
            organization = Organization.objects.filter(id=options['organization_id']).first()
        else:
            organization = Organization.objects.filter(slug=options['organization_slug']).first()

        if not organization:
            raise CommandError('Organization not found for AdminApps MedSupplier smoke.')

        health = admin_apps_client.health_check()
        modules_result = admin_apps_client.get_organization_modules(organization.id, use_cache=False)
        modules = modules_result.get('modules') or []
        medsupplier_module = next((module for module in modules if module.get('code') == 'MEDSUPPLIER'), None)
        active_scopes = MedSupplierUserScope.objects.filter(
            organization=organization,
            is_active=True,
        ).count()

        adminapps_available = 'error' not in health
        module_enabled = bool(medsupplier_module and medsupplier_module.get('enabled', True))
        fallback_source = modules_result.get('source') == 'local_database'

        self.stdout.write(f'organization={organization.id} slug={organization.slug}')
        self.stdout.write(f'adminapps_available={adminapps_available}')
        self.stdout.write(f'modules_source={modules_result.get("source", "adminapps")}')
        self.stdout.write(f'medsupplier_entitlement_enabled={module_enabled}')
        self.stdout.write(f'active_medsupplier_scopes={active_scopes}')

        if fallback_source:
            self.stdout.write(
                self.style.WARNING(
                    'AdminApps fallback local activo: no se abren permisos globales; '
                    'el acceso sigue limitado por MedSupplierUserScope.'
                )
            )

        if not module_enabled:
            raise CommandError('MEDSUPPLIER entitlement is not enabled for this organization.')
        if active_scopes == 0:
            raise CommandError('No active MedSupplier scopes found for this organization.')

        self.stdout.write(self.style.SUCCESS('MedSupplier AdminApps smoke passed.'))
