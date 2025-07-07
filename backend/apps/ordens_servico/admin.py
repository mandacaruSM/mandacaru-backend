from django.contrib import admin
from .models import OrdemServico

class OrdemServicoAdmin(admin.ModelAdmin):
    filter_horizontal = ('equipamentos',)

admin.site.register(OrdemServico, OrdemServicoAdmin)