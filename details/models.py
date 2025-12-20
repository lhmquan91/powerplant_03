import logging
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language # <--- Import để lấy ngôn ngữ hiện tại
from django.utils.functional import lazy
from django.core.exceptions import ValidationError
from django.db import transaction 
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.models import Orderable
from modelcluster.fields import ParentalKey

from core.utils import get_label_text
from core.ai_services import auto_translate_model, auto_generate_description_logic

logger = logging.getLogger(__name__)

# =========================================================
# 0. LAZY WRAPPER
# =========================================================
# Tham chiếu trực tiếp đến get_label_text của app core
get_label_lazy = lazy(get_label_text, str)

# =========================================================
# 1. THƯ VIỆN TÊN THÔNG SỐ (Danh mục dùng chung)
# =========================================================
class Detail(models.Model):
    # --- NAME FIELDS (Giữ nguyên) ---
    name_vi = models.CharField(max_length=255, verbose_name=get_label_lazy('details', 'field_name_vi_label', "Tên (Tiếng Việt)"), default="", blank=True, help_text=get_label_lazy('details', 'field_name_vi_help', "Nhập tên tiếng Việt."))
    name_en = models.CharField(max_length=255, blank=True, verbose_name=get_label_lazy('details', 'field_name_en_label', "Tên (Tiếng Anh)"), help_text=get_label_lazy('details', 'field_name_en_help', "Nhập tên tiếng Anh."))
    name_zh = models.CharField(max_length=255, blank=True, verbose_name=get_label_lazy('details', 'field_name_zh_label', "Tên (Tiếng Trung)"), help_text=get_label_lazy('details', 'field_name_zh_help', "Nhập tên tiếng Trung."))
    name_zh_pinyin = models.CharField(max_length=255, blank=True, verbose_name=get_label_lazy('details', 'field_name_zh_pinyin_label'), help_text=get_label_lazy('details', 'field_name_zh_pinyin_help', "Phiên âm Latin cho tiếng Trung."))
    name_th = models.CharField(max_length=255, blank=True, verbose_name=get_label_lazy('details', 'field_name_th_label', "Tiếng Thái"), help_text=get_label_lazy('details', 'field_name_th_help', "Nhập tên tiếng Thái."))
    name_lo = models.CharField(max_length=255, blank=True, verbose_name=get_label_lazy('details', 'field_name_lo_label', "Tiếng Lào"), help_text=get_label_lazy('details', 'field_name_lo_help', "Nhập tên tiếng Lào."))
    name_km = models.CharField(max_length=255, blank=True, verbose_name=get_label_lazy('details', 'field_name_km_label', "Tiếng Khmer"), help_text=get_label_lazy('details', 'field_name_km_help', "Nhập tên tiếng Khmer."))
    name_id = models.CharField(max_length=255, blank=True, verbose_name=get_label_lazy('details', 'field_name_id_label', "Tiếng Indonesia"), help_text=get_label_lazy('details', 'field_name_id_help', "Nhập tên tiếng Indonesia."))
    name_ms = models.CharField(max_length=255, blank=True, verbose_name=get_label_lazy('details', 'field_name_ms_label', "Tiếng Malay"), help_text=get_label_lazy('details', 'field_name_ms_help', "Nhập tên tiếng Malay."))
    name_my = models.CharField(max_length=255, blank=True, verbose_name=get_label_lazy('details', 'field_name_my_label', "Tiếng Myanmar"), help_text=get_label_lazy('details', 'field_name_my_help', "Nhập tên tiếng Myanmar."))
    name_fil = models.CharField(max_length=255, blank=True, verbose_name=get_label_lazy('details', 'field_name_fil_label', "Tiếng Filipino"), help_text=get_label_lazy('details', 'field_name_fil_help', "Nhập tên tiếng Filipino."))

    # --- DESCRIPTION FIELDS (MỚI) ---
    description_vi = models.TextField(blank=True, verbose_name=get_label_lazy('details', 'field_desc_vi_label', "Mô tả (Tiếng Việt)"), help_text=get_label_lazy('details', 'field_desc_ai_vi_help', "Nhập mô tả tiếng Việt. Để trống cả Việt và Anh để AI tự động sinh."))
    description_en = models.TextField(blank=True, verbose_name=get_label_lazy('details', 'field_desc_en_label', "Mô tả (Tiếng Anh)"), help_text=get_label_lazy('details', 'field_desc_ai_en_help', "Nhập mô tả tiếng Anh."))
    description_zh = models.TextField(blank=True, verbose_name=get_label_lazy('details', 'field_desc_zh_label', "Mô tả (Tiếng Trung)"), help_text=get_label_lazy('details', 'field_desc_ai_zh_help', "Nhập mô tả tiếng Trung."))
    # SEA Descriptions
    description_th = models.TextField(blank=True, verbose_name=get_label_lazy('details', 'field_desc_th_label', "Mô tả (Thái)"), help_text=get_label_lazy('details', 'field_desc_ai_th_help', "Nhập mô tả tiếng Thái."))
    description_lo = models.TextField(blank=True, verbose_name=get_label_lazy('details', 'field_desc_lo_label', "Mô tả (Lào)"), help_text=get_label_lazy('details', 'field_desc_ai_lo_help', "Nhập mô tả tiếng Lào."))
    description_km = models.TextField(blank=True, verbose_name=get_label_lazy('details', 'field_desc_km_label', "Mô tả (Khmer)"), help_text=get_label_lazy('details', 'field_desc_ai_km_help', "Nhập mô tả tiếng Khmer."))
    description_id = models.TextField(blank=True, verbose_name=get_label_lazy('details', 'field_desc_id_label', "Mô tả (Indonesia)"), help_text=get_label_lazy('details', 'field_desc_ai_id_help', "Nhập mô tả tiếng Indonesia."))
    description_ms = models.TextField(blank=True, verbose_name=get_label_lazy('details', 'field_desc_ms_label', "Mô tả (Malay)"), help_text=get_label_lazy('details', 'field_desc_ai_ms_help', "Nhập mô tả tiếng Malay."))
    description_my = models.TextField(blank=True, verbose_name=get_label_lazy('details', 'field_desc_my_label', "Mô tả (Myanmar)"), help_text=get_label_lazy('details', 'field_desc_ai_my_help', "Nhập mô tả tiếng Myanmar."))
    description_fil = models.TextField(blank=True, verbose_name=get_label_lazy('details', 'field_desc_fil_label', "Mô tả (Filipino)"), help_text=get_label_lazy('details', 'field_desc_ai_fil_help', "Nhập mô tả tiếng Filipino."))

    default_unit = models.CharField(max_length=50, blank=True, null=True, verbose_name=get_label_lazy('details', 'field_default_unit_label', "Đơn vị"), help_text=get_label_lazy('details', 'field_default_unit_help', "Đơn vị mặc định cho thông số này."))

    panels = [
        MultiFieldPanel([
            FieldPanel('name_vi'), FieldPanel('name_en'), FieldPanel('default_unit'),
            FieldPanel('description_vi'), FieldPanel('description_en') # Thêm vào panel chính
        ], heading=get_label_lazy('details', 'panel_core_info', "Thông tin chung")),
        
        MultiFieldPanel([
            FieldPanel('name_zh'), FieldPanel('name_zh_pinyin'), FieldPanel('description_zh')
        ], heading=_("Tiếng Trung")),

        MultiFieldPanel([
            FieldPanel('name_th'), FieldPanel('description_th'),
            FieldPanel('name_lo'), FieldPanel('description_lo'),
            FieldPanel('name_km'), FieldPanel('description_km'),
            FieldPanel('name_id'), FieldPanel('description_id'),
            FieldPanel('name_ms'), FieldPanel('description_ms'),
            FieldPanel('name_my'), FieldPanel('description_my'),
            FieldPanel('name_fil'), FieldPanel('description_fil'),
        ], heading=_("Khu vực Đông Nam Á"), classname="collapsed"),
    ]

    def __str__(self):
        current_lang = get_language() or 'vi'
        lang_key = current_lang.split('-')[0] if '-' in current_lang else current_lang
        field_name = f"name_{lang_key}"
        name_val = getattr(self, field_name, '') if hasattr(self, field_name) else ''
        if not name_val: name_val = self.name_vi or self.name_en or self.name_zh or f"Detail #{self.pk}"
        return f"{name_val} ({self.default_unit})" if self.default_unit else str(name_val)

    def clean(self):
        if not self.name_vi and not self.name_zh:
            raise ValidationError(_("Vui lòng nhập tên thông số bằng Tiếng Việt hoặc Tiếng Trung."))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Sử dụng on_commit để tránh lock DB khi gọi API
        transaction.on_commit(lambda: self.trigger_auto_translate())

    def trigger_auto_translate(self):
        """
        Hàm xử lý AI toàn diện: Dịch tên -> Sinh mô tả -> Dịch mô tả -> Lưu.
        """
        try:
            # Refresh để đảm bảo dữ liệu mới nhất
            self.refresh_from_db()
            
            # 1. Dịch Tên (Name)
            # (Đảm bảo các tên ngôn ngữ khác được điền từ nguồn VI/ZH)
            auto_translate_model(self, fields=['name'])
            
            # 2. Sinh Mô tả (Description Generator)
            # (Chỉ chạy nếu cả description_vi và description_en đều trống)
            auto_generate_description_logic(self, source_field='name', target_field='description')

            # 3. Dịch Mô tả (Description Translator) - MỚI BỔ SUNG
            # (Chạy để lấp đầy các ngôn ngữ còn lại nếu user nhập tay description hoặc AI vừa sinh ra ở bước 2)
            # Hàm này thông minh: nếu field đã có dữ liệu (do bước 2 sinh ra hoặc user nhập), nó sẽ bỏ qua, không ghi đè.
            auto_translate_model(self, fields=['description'])
            
            # 4. Gom dữ liệu để update một lần (Atomic Update)
            update_data = {}
            
            # Danh sách tất cả các hậu tố ngôn ngữ
            suffixes = ['vi', 'en', 'zh', 'zh_pinyin', 'th', 'lo', 'km', 'id', 'ms', 'my', 'fil']
            
            # Lấy dữ liệu Name mới
            for s in suffixes:
                f = f"name_{s}"
                if hasattr(self, f) and getattr(self, f): update_data[f] = getattr(self, f)
            
            # Lấy dữ liệu Description mới
            for s in [x for x in suffixes if x != 'zh_pinyin']:
                f = f"description_{s}"
                if hasattr(self, f) and getattr(self, f): update_data[f] = getattr(self, f)

            # Thực hiện update trực tiếp (Tránh gọi save() lần nữa gây loop)
            if update_data:
                Detail.objects.filter(pk=self.pk).update(**update_data)
                
        except Exception as e:
            logger.error(f"Auto translate error for Detail {self.pk}: {e}")

    class Meta:
        verbose_name = get_label_lazy('details', 'model_detail_name', "Danh mục Thông số")
        verbose_name_plural = get_label_lazy('details', 'model_detail_plural', "Danh mục Thông số")


# =========================================================
# 2. GIÁ TRỊ THÔNG SỐ TRÊN THIẾT BỊ
# =========================================================
class EquipmentValue(Orderable):
    equipment = ParentalKey(
        'equipment.Equipment', 
        on_delete=models.CASCADE, 
        related_name='values',
        verbose_name=get_label_lazy('details', 'field_equipment_label', "Thiết bị")
    )
    
    detail = models.ForeignKey(
        Detail, 
        on_delete=models.CASCADE, 
        related_name='+',
        verbose_name=get_label_lazy('details', 'field_detail_label', "Tên thông số")
    )
    
    value = models.CharField(
        max_length=255, 
        verbose_name=get_label_lazy('details', 'field_value_label', "Giá trị")
    )
    
    unit = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        verbose_name=get_label_lazy('details', 'field_unit_label', "Đơn vị (nếu khác)")
    )

    panels = [
        FieldPanel('detail'), 
        FieldPanel('value'),
        FieldPanel('unit', help_text=get_label_lazy('details', 'field_unit_help', "Để trống sẽ dùng đơn vị mặc định")),
    ]

    class Meta:
        verbose_name = get_label_lazy('details', 'model_equipmentvalue_name', "Thông số kỹ thuật")
        verbose_name_plural = get_label_lazy('details', 'model_equipmentvalue_plural', "Thông số kỹ thuật")
        unique_together = ('equipment', 'detail')