from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.contrib import admin
from django.urls import reverse

from wagtail.models import PreviewableMixin
from modelcluster.models import ClusterableModel # <--- Bắt buộc cho InlinePanel
from wagtail.admin.panels import (
    FieldPanel, 
    MultiFieldPanel, 
    TabbedInterface, 
    ObjectList,
    InlinePanel # <--- Bắt buộc để nhúng EquipmentValue
)
from wagtail.fields import RichTextField
from wagtail.images import get_image_model_string
from wagtail.documents import get_document_model_string


# =========================================================
# 1. PHYSICAL EQUIPMENT (Thiết bị Vật lý)
# =========================================================
class Equipment(ClusterableModel, PreviewableMixin, models.Model):
    """
    Model quản lý Thiết bị. Kế thừa ClusterableModel để hỗ trợ quan hệ 1-n (InlinePanel).
    """
    # --- Định danh ---
    name = models.CharField(max_length=255, verbose_name=_("Tên thiết bị"))
    kks_code = models.CharField(max_length=50, blank=True, null=True, db_index=True, verbose_name=_("Mã KKS"))
    
    location = models.ForeignKey(
        'area.FunctionalLocation', 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='equipments', 
        verbose_name=_("Khu vực lắp đặt")
    )

    # --- Thông tin chung ---
    manufacturer = models.CharField(max_length=255, blank=True, verbose_name=_("Hãng sản xuất"))
    model_number = models.CharField(max_length=255, blank=True, verbose_name=_("Model / Type"))
    
    # --- Media & Tài liệu ---
    image = models.ForeignKey(get_image_model_string(), null=True, blank=True, on_delete=models.SET_NULL, related_name='+', verbose_name=_("Hình ảnh"))
    operation_manual = models.ForeignKey(get_document_model_string(), null=True, blank=True, on_delete=models.SET_NULL, related_name='+', verbose_name=_("Tài liệu Vận hành"))
    maintenance_manual = models.ForeignKey(get_document_model_string(), null=True, blank=True, on_delete=models.SET_NULL, related_name='+', verbose_name=_("Tài liệu Bảo trì"))

    description = RichTextField(verbose_name=_("Mô tả / Nguyên lý"), blank=True)
    
    # --- Audio TTS ---
    audio_vi = models.FileField(upload_to='tts/equip/vi/', blank=True, null=True, verbose_name=_("Audio (VI)"))
    audio_en = models.FileField(upload_to='tts/equip/en/', blank=True, null=True, verbose_name=_("Audio (EN)"))

    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Cập nhật"))

    # --- PANELS CONFIGURATION ---
    content_panels = [
        MultiFieldPanel([
            FieldPanel('name'), 
            FieldPanel('kks_code'), 
            FieldPanel('location')
        ], heading="Định danh"),
        
        MultiFieldPanel([
            FieldPanel('image'), 
            FieldPanel('manufacturer'), 
            FieldPanel('model_number')
        ], heading="Thông tin chung"),
        
        # INLINE PANEL: Thay thế StreamField cũ
        # Cho phép thêm/sửa/xóa các dòng EquipmentValue trực tiếp tại đây
        InlinePanel('values', label="Thông số kỹ thuật", heading="Chi tiết kỹ thuật"),
        
        MultiFieldPanel([
            FieldPanel('operation_manual'), 
            FieldPanel('maintenance_manual')
        ], heading="Tài liệu"),
        
        FieldPanel('description'),
    ]
    
    ai_panels = [
        FieldPanel('audio_vi'), 
        FieldPanel('audio_en')
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Thông tin chính'),
        ObjectList(ai_panels, heading='Dữ liệu AI'),
    ])

    # --- DISPLAY METHODS (Admin) ---
    @admin.display(description="Tên thiết bị", ordering="name")
    def name_inspect_link(self):
        try:
            url = reverse('wagtailsnippets_equipment_equipment:inspect', args=[self.pk])
            return format_html('<a href="{}" style="font-weight: 600;">{}</a>', url, self.name)
        except:
            return self.name

    @admin.display(description="Mã KKS", ordering="kks_code")
    def kks_display(self):
        if self.kks_code:
            return format_html('<span class="w-status w-status--label w-bg-info-50 w-text-info-100">{}</span>', self.kks_code)
        return "-"

    @admin.display(description="Khu vực")
    def location_link(self):
        return self.location.name if self.location else "-"

    @admin.display(description="Thông số")
    def specs_count(self):
        # Đếm từ quan hệ ngược 'values'
        count = self.values.count()
        if count > 0:
            return format_html('<span class="w-status w-status--label w-bg-surface-menus w-text-text-label">{} thông số</span>', count)
        return "-"

    @admin.display(description="TTS")
    def audio_status_display(self):
        def render_dot(has_file, lang):
            color = "w-bg-positive-100" if has_file else "w-bg-grey-200"
            return f'<span class="w-w-2.5 w-h-2.5 w-rounded-full {color}" title="{lang}"></span>'
        html = f'<div class="w-flex w-gap-1">{render_dot(bool(self.audio_vi), "VI")}{render_dot(bool(self.audio_en), "EN")}</div>'
        return format_html(html)

    def __str__(self):
        return f"[{self.kks_code}] {self.name}" if self.kks_code else self.name

    class Meta:
        verbose_name = _("Thiết bị Vật lý")
        verbose_name_plural = _("Thiết bị Vật lý")


# =========================================================
# 2. DIGITAL TWIN (Thiết bị Số)
# =========================================================
class EquipmentDigital(models.Model):
    """
    Model quản lý phần Kỹ thuật số (IoT/Network).
    """
    equipment = models.OneToOneField(
        Equipment, 
        on_delete=models.CASCADE, 
        related_name='digital_profile',
        verbose_name=_("Thiết bị vật lý")
    )
    
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name=_("Địa chỉ IP"))
    mac_address = models.CharField(max_length=17, blank=True, verbose_name=_("MAC Address"))
    protocol = models.CharField(
        max_length=50, 
        choices=[('modbus', 'Modbus TCP/IP'), ('opcua', 'OPC UA'), ('mqtt', 'MQTT'), ('snmp', 'SNMP')],
        blank=True,
        verbose_name=_("Giao thức")
    )
    
    dashboard_url = models.URLField(blank=True, verbose_name=_("Link Dashboard"))
    last_connected = models.DateTimeField(null=True, blank=True, verbose_name=_("Kết nối cuối"))
    is_online = models.BooleanField(default=False, verbose_name=_("Online"))
    firmware_version = models.CharField(max_length=50, blank=True, verbose_name=_("Firmware"))

    panels = [
        FieldPanel('equipment'),
        MultiFieldPanel([
            FieldPanel('ip_address'),
            FieldPanel('mac_address'),
            FieldPanel('protocol'),
        ], heading="Kết nối mạng"),
        MultiFieldPanel([
            FieldPanel('dashboard_url'),
            FieldPanel('firmware_version'),
        ], heading="Giám sát"),
        FieldPanel('is_online'),
        FieldPanel('last_connected'),
    ]

    @admin.display(description="Thiết bị", ordering="equipment__name")
    def equipment_link(self):
        try:
            url = reverse('wagtailsnippets_equipment_equipment:inspect', args=[self.equipment.pk])
            return format_html('<a href="{}">{}</a>', url, self.equipment.name)
        except:
            return self.equipment.name

    @admin.display(description="Trạng thái")
    def status_display(self):
        if self.is_online:
            return format_html('<span class="w-status w-status--label w-bg-positive-50 w-text-positive-100">ONLINE</span>')
        return format_html('<span class="w-status w-status--label w-bg-critical-50 w-text-critical-200">OFFLINE</span>')

    def __str__(self):
        return f"Digital: {self.equipment.name}"

    class Meta:
        verbose_name = _("Thiết bị Số (Digital)")
        verbose_name_plural = _("Thiết bị Số (Digital)")