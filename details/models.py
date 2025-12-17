from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.contrib import admin
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.models import DraftStateMixin, RevisionMixin, Orderable
from modelcluster.fields import ParentalKey

# =============================================
# === 1. DETAIL GROUP MODEL (Nhóm thông số) ===
# =============================================

class DetailGroup(DraftStateMixin, RevisionMixin, models.Model):
    """
    Nhóm thông số kỹ thuật (Ví dụ: Thông số Điện, Thông số Hóa học).
    """
    name = models.CharField(max_length=100, verbose_name=_("Tên nhóm thông số"))
    description = models.TextField(blank=True, verbose_name=_("Mô tả nhóm"), help_text="Mô tả các thông số thuộc nhóm này.")
    is_active = models.BooleanField(default=True, verbose_name=_("Kích hoạt"))
    
    panels = [
        FieldPanel('name'),
        FieldPanel('description'),
        FieldPanel('is_active'),
        InlinePanel('details', label=_("Danh sách Thông số chi tiết")), 
    ]

    @admin.display(description="Số lượng chi tiết")
    def get_details_count(self):
        count = self.details.count()
        if count > 0:
            return format_html(
                '<span class="w-status w-status--label w-bg-primary-50 w-text-primary-200">{}</span>', 
                count
            )
        return format_html('<span class="w-text-text-meta">0</span>')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Nhóm Thông số")
        verbose_name_plural = _("Nhóm Thông số")
        ordering = ['name']


# ===========================================
# === 2. DETAIL MODEL (Thông số chi tiết) ===
# ===========================================

class Detail(models.Model):
    """
    Chi tiết một thông số (Ví dụ: Điện áp, Cột áp).
    """
    group = models.ForeignKey(
        DetailGroup,
        on_delete=models.CASCADE,
        related_name='details', # Dùng cho InlinePanel của DetailGroup
        verbose_name=_("Nhóm thông số"),
        null=True, blank=True
    )
    
    name = models.CharField(max_length=100, verbose_name=_("Tên thông số"))
    unit = models.CharField(max_length=20, blank=True, verbose_name=_("Đơn vị"), help_text="VD: V, bar, m3/h")
    
    DATA_TYPE_CHOICES = [
        ('num', 'Số (Number)'),
        ('text', 'Chữ (Text)'),
        ('bool', 'Đúng/Sai (Boolean)'),
    ]
    data_type = models.CharField(max_length=10, choices=DATA_TYPE_CHOICES, default='num', verbose_name=_("Kiểu dữ liệu"))

    is_active = models.BooleanField(default=True, verbose_name=_("Kích hoạt"))
    
    panels = [
        FieldPanel('group'),
        FieldPanel('name'),
        FieldPanel('unit'),
        FieldPanel('data_type'),
        FieldPanel('is_active'),
    ]
    
    # Phương thức hiển thị Group cha cho bảng Index View của Detail
    @admin.display(description="Nhóm")
    def group_name(self):
        return self.group.name

    def __str__(self):
        return f"{self.name} ({self.unit})"

    class Meta:
        verbose_name = _("Thông số")
        verbose_name_plural = _("Thông số")
        ordering = ['name']


# =================================================
# === 3. EQUIPMENT VALUE MODEL (Giá trị đo đạc) ===
# =================================================

class EquipmentValue(Orderable):
    """
    Giá trị thực tế gán cho thiết bị.
    Kế thừa Orderable để hỗ trợ sắp xếp kéo thả trong InlinePanel.
    """
    # Dùng ParentalKey để liên kết chặt với Equipment (ClusterableModel)
    equipment = ParentalKey(
        'equipment.Equipment', 
        on_delete=models.CASCADE, 
        related_name='values', # Tên này dùng trong InlinePanel ở Equipment
        verbose_name=_("Thiết bị")
    )
    
    detail = models.ForeignKey(
        Detail,
        on_delete=models.PROTECT, 
        verbose_name=_("Thông số")
    )

    value = models.CharField(max_length=255, verbose_name=_("Giá trị"))
    
    # Auto timestamp (không hiển thị trên form nhập liệu)
    measured_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Thời gian đo"))

    # Panels hiển thị khi nhập liệu trong Equipment
    panels = [
        FieldPanel('detail'),
        FieldPanel('value'),
    ]

    # Các phương thức hiển thị cho trang Snippet List (Read-only)
    @admin.display(description="Thiết bị")
    def equipment_name(self):
        return self.equipment.name

    @admin.display(description="Thông số")
    def detail_name(self):
        return self.detail.name

    def __str__(self):
        return f"{self.detail.name}: {self.value}"

    class Meta:
        verbose_name = _("Giá trị")
        verbose_name_plural = _("Giá trị")
        ordering = ['sort_order']