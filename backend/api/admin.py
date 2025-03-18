from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import (Character, StoryOrEvent, SceneOrIncident, PlaceOrLocation,
                    ObjectOrArtifact, ThemeOrMoral, MythologySystem, MythologyEra,
                    CreatureOrSpecies, ProphecyOrFate, Comparison, CulturalOrHistorical,
                    RiddleOrPuzzle)

# Create a mixin for common image handling
class ImagePreviewMixin:
    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="150" height="150" style="object-fit: cover;" />')
        return "No Image"
    
    image_preview.short_description = 'Image Preview'

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin, ImagePreviewMixin):
    list_display = ('name', 'manual_entry', 'image_preview')
    search_fields = ('name',)
    fields = ('name', 'queries', 'answers', 'image', 'image_preview', 'manual_entry')
    readonly_fields = ('image_preview',)

@admin.register(StoryOrEvent)
class StoryOrEventAdmin(admin.ModelAdmin, ImagePreviewMixin):
    list_display = ('title', 'manual_entry', 'image_preview')
    search_fields = ('title',)
    fields = ('title', 'queries', 'answers', 'source', 'image', 'image_preview', 'manual_entry')
    readonly_fields = ('image_preview',)

@admin.register(SceneOrIncident)
class SceneOrIncidentAdmin(admin.ModelAdmin, ImagePreviewMixin):
    list_display = ('scene_title', 'manual_entry', 'image_preview')
    search_fields = ('scene_title',)
    fields = ('scene_title', 'queries', 'answers', 'image', 'image_preview', 'manual_entry')
    readonly_fields = ('image_preview',)

@admin.register(PlaceOrLocation)
class PlaceOrLocationAdmin(admin.ModelAdmin, ImagePreviewMixin):
    list_display = ('place_name', 'manual_entry', 'image_preview')
    search_fields = ('place_name',)
    fields = ('place_name', 'queries', 'answers', 'image', 'image_preview', 'manual_entry')
    readonly_fields = ('image_preview',)

@admin.register(ObjectOrArtifact)
class ObjectOrArtifactAdmin(admin.ModelAdmin, ImagePreviewMixin):
    list_display = ('object_name', 'manual_entry', 'image_preview')
    search_fields = ('object_name',)
    fields = ('object_name', 'queries', 'answers', 'image', 'image_preview', 'manual_entry')
    readonly_fields = ('image_preview',)

@admin.register(ThemeOrMoral)
class ThemeOrMoralAdmin(admin.ModelAdmin, ImagePreviewMixin):
    list_display = ('theme', 'manual_entry', 'image_preview')
    search_fields = ('theme',)
    fields = ('theme', 'queries', 'answers', 'image', 'image_preview', 'manual_entry')
    readonly_fields = ('image_preview',)

@admin.register(MythologySystem)
class MythologySystemAdmin(admin.ModelAdmin, ImagePreviewMixin):
    list_display = ('system_name', 'manual_entry', 'image_preview')
    search_fields = ('system_name',)
    fields = ('system_name', 'queries', 'answers', 'image', 'image_preview', 'manual_entry')
    readonly_fields = ('image_preview',)

@admin.register(MythologyEra)
class MythologyEraAdmin(admin.ModelAdmin, ImagePreviewMixin):
    list_display = ('era_name', 'manual_entry', 'image_preview')
    search_fields = ('era_name',)
    fields = ('era_name', 'queries', 'answers', 'image', 'image_preview', 'manual_entry')
    readonly_fields = ('image_preview',)

@admin.register(CreatureOrSpecies)
class CreatureOrSpeciesAdmin(admin.ModelAdmin, ImagePreviewMixin):
    list_display = ('species_name', 'manual_entry', 'image_preview')
    search_fields = ('species_name',)
    fields = ('species_name', 'queries', 'answers', 'image', 'image_preview', 'manual_entry')
    readonly_fields = ('image_preview',)

@admin.register(ProphecyOrFate)
class ProphecyOrFateAdmin(admin.ModelAdmin, ImagePreviewMixin):
    list_display = ('prophecy_title', 'manual_entry', 'image_preview')
    search_fields = ('prophecy_title',)
    fields = ('prophecy_title', 'queries', 'answers', 'image', 'image_preview', 'manual_entry')
    readonly_fields = ('image_preview',)

@admin.register(Comparison)
class ComparisonAdmin(admin.ModelAdmin, ImagePreviewMixin):
    list_display = ('comparison_title', 'manual_entry', 'image_preview')
    search_fields = ('comparison_title',)
    fields = ('comparison_title', 'queries', 'answers', 'image', 'image_preview', 'manual_entry')
    readonly_fields = ('image_preview',)

@admin.register(CulturalOrHistorical)
class CulturalOrHistoricalAdmin(admin.ModelAdmin, ImagePreviewMixin):
    list_display = ('culture_event', 'manual_entry', 'image_preview')
    search_fields = ('culture_event',)
    fields = ('culture_event', 'queries', 'answers', 'image', 'image_preview', 'manual_entry')
    readonly_fields = ('image_preview',)

@admin.register(RiddleOrPuzzle)
class RiddleOrPuzzleAdmin(admin.ModelAdmin, ImagePreviewMixin):
    list_display = ('riddle', 'manual_entry', 'image_preview')
    search_fields = ('riddle',)
    fields = ('riddle', 'queries', 'answers', 'image', 'image_preview', 'manual_entry')
    readonly_fields = ('image_preview',)
from .models import AppUser, UserQuery

# Register AppUser model
@admin.register(AppUser)
class AppUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'created_at')  # Display fields in admin panel
    search_fields = ('username',)  # Enable search by username
    ordering = ('-created_at',)  # Order by creation date (latest first)

# Register UserQuery model
class UserQueryAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_username', 'query', 'created_at')  # Show username

    def get_username(self, obj):
        return obj.user.username  # Fetch username instead of showing ID
    get_username.admin_order_field = 'user'  # Allow sorting by user
    get_username.short_description = 'Username'  # Rename column in admin panel

    search_fields = ('user__username', 'query')  
    list_filter = ('created_at',)  
    ordering = ('-created_at',)  
