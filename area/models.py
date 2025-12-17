from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.contrib import admin
from django.urls import reverse

from treebeard.mp_tree import MP_Node
from wagtail.models import PreviewableMixin
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, TabbedInterface, ObjectList
from wagtail.fields import RichTextField
from wagtail.images import get_image_model_string
from wagtail.documents import get_document_model_string

class FunctionalLocation(MP_Node, PreviewableMixin):
    """
    Model quản lý Khu vực / Hệ thống chức năng (Functional Location).
    Sử dụng cấu trúc cây (Tree) để phân cấp (Nhà máy -> Khối -> Hệ thống -> Cụm).
    """
    name = models.CharField(max_length=255, verbose_name=_("Tên khu vực/Hệ thống"))
    kks_code = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        db_index=True, 
        verbose_name=_("Mã KKS"),
        help_text="Mã định danh hệ thống (VD: 10LAC10)."
    )
    
    # --- Media & Tài liệu ---
    image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_("Hình ảnh đại diện")
    )
    
    schematic_file = models.ForeignKey(
        get_document_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_("Sơ đồ P&ID / Bản vẽ (PDF)")
    )

    # --- Nội dung & AI ---
    description = RichTextField(verbose_name=_("Mô tả chức năng"), blank=True)
    
    # Audio TTS (Vietnamese / English / Chinese)
    audio_vi = models.FileField(upload_to='tts/area/vi/', blank=True, null=True, verbose_name=_("Audio (VI)"))
    audio_en = models.FileField(upload_to='tts/area/en/', blank=True, null=True, verbose_name=_("Audio (EN)"))
    audio_cn = models.FileField(upload_to='tts/area/cn/', blank=True, null=True, verbose_name=_("Audio (CN)"))

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name=_("Ngày tạo"))
    updated_at = models.DateTimeField(auto_now=True, null=True, verbose_name=_("Cập nhật cuối"))

    # Trường này dùng để chọn cha trên giao diện. 
    # Logic Treebeard sẽ đọc trường này để biết cần add_child vào đâu.
    parent_selection = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='children_ref',
        verbose_name=_("Trực thuộc (Khu vực cha)"),
        help_text=_("Để trống nếu đây là Khu vực gốc (Root).")
    )

    # --- PANELS CONFIGURATION ---
    content_panels = [
        MultiFieldPanel([
            FieldPanel('parent_selection'),
            FieldPanel('name'),
            FieldPanel('kks_code'),
        ], heading="Định danh"),
        
        MultiFieldPanel([
            FieldPanel('image'),
            FieldPanel('schematic_file'),
        ], heading="Media & Tài liệu"),
        
        FieldPanel('description'),
    ]

    ai_panels = [
        FieldPanel('audio_vi', heading="Vietnamese Audio"),
        FieldPanel('audio_en', heading="English Audio"),
        FieldPanel('audio_cn', heading="Chinese Audio"),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Thông tin chính'),
        ObjectList(ai_panels, heading='Dữ liệu AI/TTS'),
    ])

    # --- CUSTOM ADMIN DISPLAY METHODS ---

    @admin.display(description="Tên khu vực", ordering="name")
    def name_inspect_link(self):
        """Tạo link trỏ đến trang Inspect thay vì Edit."""
        try:
            url = reverse('wagtailsnippets_area_functionallocation:inspect', args=[self.pk])
            return format_html('<a href="{}" style="font-weight: 600;">{}</a>', url, self.name)
        except:
            return self.name

    @admin.display(description="Mã KKS", ordering="kks_code")
    def kks_display(self):
        if self.kks_code:
            return format_html('<span class="w-status w-status--label w-bg-info-50 w-text-info-100">{}</span>', self.kks_code)
        return "-"

    @admin.display(description="Trực thuộc")
    def parent_display(self):
        parent = self.get_parent()
        if parent:
            return parent.name
        return format_html('<span class="w-text-critical-200 w-font-bold">ROOT</span>')

    @admin.display(description="TTS")
    def audio_status_display(self):
        def render_dot(has_file, lang):
            color = "w-bg-positive-100" if has_file else "w-bg-grey-200"
            return f'<span class="w-w-2.5 w-h-2.5 w-rounded-full {color}" title="{lang}"></span>'
        
        html = f'<div class="w-flex w-gap-1">{render_dot(bool(self.audio_vi), "VI")}{render_dot(bool(self.audio_en), "EN")}</div>'
        return format_html(html)

    def __str__(self):
        return f"{self.name} ({self.kks_code})" if self.kks_code else self.name

    class Meta:
        verbose_name = _("Khu vực")
        verbose_name_plural = _("Khu vực")