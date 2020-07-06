from django.contrib import admin

from .models import Player

class PlayerAdmin(admin.ModelAdmin):
    list_display = ('user', 'banned', 'score','current_level')
    list_display_links = ('user', 'score')
    list_filter = ('current_level',)
    search_fields = ('user','current_level')
    list_per_page = 25


admin.site.register(Player, PlayerAdmin)
