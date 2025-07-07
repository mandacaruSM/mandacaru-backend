from django.contrib import admin
from .models import ContaFinanceira

@admin.register(ContaFinanceira)
class ContaFinanceiraAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'descricao', 'valor', 'vencimento', 'status')
    list_filter = ('tipo', 'status', 'vencimento')
    search_fields = ('descricao',)