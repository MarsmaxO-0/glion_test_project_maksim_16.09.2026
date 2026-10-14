from django.contrib import admin

from .models import (
    Case, ChatLog, ContactMessage, IpArea, Lawyer, Practice, PracticeGroup, PracticeHighlight, PressItem, Publication,
    ResearchItem,
)


@admin.register(PracticeGroup)
class PracticeGroupAdmin(admin.ModelAdmin):
    list_display = ('number', 'title_ru', 'title_en', 'order')
    list_editable = ('order',)


@admin.register(Practice)
class PracticeAdmin(admin.ModelAdmin):
    list_display = ('title_ru', 'title_en', 'group', 'order', 'links_to_ip_centre')
    list_filter = ('group',)
    list_editable = ('order',)
    search_fields = ('title_ru', 'title_en')


@admin.register(Lawyer)
class LawyerAdmin(admin.ModelAdmin):
    list_display = ('name_ru', 'name_en', 'group', 'position_ru', 'order', 'on_home')
    list_filter = ('group', 'on_home')
    list_editable = ('order', 'on_home')
    search_fields = ('name_ru', 'name_en')
    prepopulated_fields = {'slug': ('name_en',)}
    filter_horizontal = ('practices',)
    fieldsets = (
        (None, {'fields': ('slug', 'group', 'order', 'on_home', 'photo_url', 'silhouette', 'practices')}),
        ('Русский', {'fields': (
            'name_ru', 'position_ru', 'short_role_ru', 'kicker_ru', 'role_ru', 'registry_ru', 'bio_ru',
            'extra_title_ru', 'extra_ru', 'specialisation_ru', 'awards_title_ru', 'awards_ru', 'news_ru',
        )}),
        ('English', {'fields': (
            'name_en', 'position_en', 'short_role_en', 'kicker_en', 'role_en', 'registry_en', 'bio_en',
            'extra_title_en', 'extra_en', 'specialisation_en', 'awards_title_en', 'awards_en', 'news_en',
        )}),
    )


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('order', 'title_ru', 'title_en', 'on_home')
    list_editable = ('on_home',)


@admin.register(PracticeHighlight)
class PracticeHighlightAdmin(admin.ModelAdmin):
    list_display = ('order', 'label_ru', 'title_ru', 'title_en')


@admin.register(PressItem)
class PressItemAdmin(admin.ModelAdmin):
    list_display = ('date', 'title_ru', 'source_ru', 'on_home')
    list_filter = ('on_home',)
    list_editable = ('on_home',)
    search_fields = ('title_ru', 'title_en')


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ('order', 'author_ru', 'title_ru')


@admin.register(ResearchItem)
class ResearchItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'title_ru', 'title_en')


@admin.register(IpArea)
class IpAreaAdmin(admin.ModelAdmin):
    list_display = ('order', 'short_ru', 'full_ru', 'on_home')
    list_editable = ('on_home',)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('created', 'name', 'contact', 'language', 'handled')
    list_filter = ('handled', 'language')
    list_editable = ('handled',)
    readonly_fields = ('created', 'language', 'name', 'contact', 'message')


@admin.register(ChatLog)
class ChatLogAdmin(admin.ModelAdmin):
    list_display = ('created', 'language', 'question_short', 'session_key')
    list_filter = ('language',)
    search_fields = ('question', 'answer')
    readonly_fields = ('created', 'session_key', 'language', 'question', 'answer')

    @admin.display(description='Question')
    def question_short(self, obj):
        return obj.question[:80]
