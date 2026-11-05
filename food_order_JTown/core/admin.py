from django.contrib import admin
from django.utils.html import format_html
from .models import Category, MenuItem, GalleryImage, ContactMessage

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'price', 'image', 'category_id', 'available')
    search_fields = ('name', 'description', 'category_id', 'available')

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_preview', 'title', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title',)
    ordering = ('order', '-created_at')

    def thumbnail_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 75px; height: 50px; object-fit: cover; border-radius: 6px; border: 1px solid #ddd;" />',
                obj.image.url
            )
        return format_html('<span style="color: #999;">No image</span>')
    thumbnail_preview.short_description = 'Preview'

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email', 'phone', 'message')
    list_filter = ('created_at',)
    readonly_fields = ('name', 'email', 'phone', 'message', 'created_at')
    ordering = ('-created_at',)

admin.site.register(MenuItem, MenuItemAdmin)
admin.site.register(Category, CategoryAdmin)