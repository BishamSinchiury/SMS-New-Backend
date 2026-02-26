from Org.models import OrganizationAdmin

class TenantSafeQuerySetMixin:
    """
    Mixin for ViewSets to ensure querysets are always filtered by the user's
    assigned organization(s), avoiding cross-tenant data leaks.
    """
    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        if user.is_superuser:
            return queryset

        # Get list of organization IDs where the user is an active admin
        admin_org_ids = OrganizationAdmin.objects.filter(
            user=user,
            is_active=True
        ).values_list('organization_id', flat=True)

        # Filter the queryset by these organizations
        # Assumes the model has an 'organization' field (TenantModel)
        return queryset.filter(organization_id__in=admin_org_ids)
