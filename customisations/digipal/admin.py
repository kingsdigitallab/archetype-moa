from digipal.admin_filters import SimpleListFilter

class ImageFilterSeals(SimpleListFilter):
    title = 'Seals'

    parameter_name = ('seals')

    def lookups(self, request, model_admin):
        return (
            ('0', ('Hide seals')),
        )

    def queryset(self, request, queryset):
        if self.value() == '0':
            return queryset.exclude(locus__icontains = 'seal').distinct()

from django.contrib import admin
from digipal import admin as digipal_admin
from digipal.models import Image

class ImageAdmin(digipal_admin.ImageAdmin):
    list_filter = digipal_admin.ImageAdmin.list_filter
    list_filter.append(ImageFilterSeals)

admin.site.unregister(Image)
admin.site.register(Image, ImageAdmin)

digipal_admin.ImageAdmin = ImageAdmin
