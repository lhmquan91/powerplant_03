from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.core.management import call_command
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from django.db import transaction

# =========================================================
# 1. QUẢN LÝ NGÔN NGỮ (SYSTEM LANGUAGE)
# =========================================================
# @register_snippet
class SystemLanguage(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name=_("Mã ngôn ngữ"))
    name = models.CharField(max_length=100, verbose_name=_("Tên hiển thị"))
    flag = models.CharField(max_length=10, default="🏳️", verbose_name=_("Quốc kỳ (Emoji)"))
    is_active = models.BooleanField(default=True, verbose_name=_("Kích hoạt"))
    is_core = models.BooleanField(default=False, editable=False, verbose_name=_("Là ngôn ngữ gốc"))

    panels = [FieldPanel('code'), FieldPanel('name'), FieldPanel('flag'), FieldPanel('is_active')]
    
    def __str__(self): return f"{self.flag} {self.name}"
    
    def delete(self, *args, **kwargs):
        if self.is_core: raise ValidationError(_("Không thể xóa ngôn ngữ mặc định."))
        self.is_active = False
        self.save()
    
    class Meta:
        verbose_name = _("Cấu hình Ngôn ngữ")
        verbose_name_plural = _("Cấu hình Ngôn ngữ")
        ordering = ['-is_core', 'code']

# =========================================================
# 2. QUẢN LÝ PROMPT
# =========================================================
# @register_snippet
class AIPrompt(models.Model):
    PROMPT_TYPES = [
        ('translate_to_en', _('Dịch sang Tiếng Anh (Chuẩn hóa)')),
        ('translate_from_en', _('Dịch từ Tiếng Anh sang ngôn ngữ khác')),
        ('pinyin_converter', _('Chuyển đổi Pinyin (Tiếng Trung)')),
        ('generate_desc', _('Tự động tạo mô tả (Từ tên)')), # <--- MỚI
    ]
    SCOPE_CHOICES = [('system', 'Toàn hệ thống'), ('app', 'Theo Phân hệ'), ('specific', 'Cụ thể')]

    name = models.CharField(max_length=255, verbose_name=_("Tên Prompt"))
    prompt_type = models.CharField(max_length=50, choices=PROMPT_TYPES, verbose_name=_("Loại tác vụ"))
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, default='system', verbose_name=_("Phạm vi"))
    target_app = models.CharField(max_length=50, blank=True, verbose_name=_("Áp dụng cho App"))
    content = models.TextField(verbose_name=_("Nội dung Prompt"))
    is_active = models.BooleanField(default=True, verbose_name=_("Sử dụng"))

    panels = [
        MultiFieldPanel([FieldPanel('name'), FieldPanel('prompt_type'), FieldPanel('is_active')], heading="Cấu hình"),
        MultiFieldPanel([FieldPanel('scope'), FieldPanel('target_app')], heading="Phạm vi áp dụng"),
        FieldPanel('content', classname="full"),
    ]
    def __str__(self): return self.name
    class Meta: verbose_name = _("Cấu hình AI Prompt"); verbose_name_plural = _("Cấu hình AI Prompt")

# =========================================================
# 3. SYSTEM LABEL (CẬP NHẬT CÁC TRƯỜNG CỤ THỂ)
# =========================================================
# @register_snippet
class SystemLabel(models.Model):
    # ... (Các field giữ nguyên) ...
    APP_CHOICES = [
        ('common', _('Dùng chung (Common)')),
        ('equipment', _('Thiết bị (Equipment)')),
        ('details', _('Thông số (Details)')),
        ('auth', _('Tài khoản (Auth)')),
        ('report', _('Báo cáo (Report)')),
        ('core', _('Hệ thống (Core)')),
    ]
    app = models.CharField(max_length=50, choices=APP_CHOICES, default='common', verbose_name=_("Phân hệ"))
    key = models.SlugField(max_length=100, verbose_name=_("Mã định danh (Key)"))
    description = models.CharField(max_length=255, blank=True, verbose_name=_("Mô tả ngữ cảnh"))
    
    # ... (Các field ngôn ngữ giữ nguyên) ...
    text_vi = models.TextField(verbose_name=_("Tiếng Việt"), default="", blank=True)
    text_en = models.TextField(verbose_name=_("Tiếng Anh"), blank=True)
    text_zh = models.TextField(verbose_name=_("Tiếng Trung (Giản thể)"), blank=True)
    text_zh_pinyin = models.TextField(verbose_name=_("Pinyin (Trung)"), blank=True, help_text="Phiên âm Latin cho tiếng Trung")
    # ... (Các field SEA giữ nguyên) ...
    text_th = models.TextField(verbose_name=_("Tiếng Thái"), blank=True)
    text_lo = models.TextField(verbose_name=_("Tiếng Lào"), blank=True)
    text_km = models.TextField(verbose_name=_("Tiếng Khmer"), blank=True)
    text_id = models.TextField(verbose_name=_("Tiếng Indonesia"), blank=True)
    text_ms = models.TextField(verbose_name=_("Tiếng Malay"), blank=True)
    text_my = models.TextField(verbose_name=_("Tiếng Myanmar"), blank=True)
    text_fil = models.TextField(verbose_name=_("Tiếng Filipino"), blank=True)

    panels = [
        MultiFieldPanel([FieldPanel('app'), FieldPanel('key'), FieldPanel('description')], heading=_("Thông tin chung")),
        MultiFieldPanel([FieldPanel('text_vi'), FieldPanel('text_en')], heading=_("Ngôn ngữ Gốc (Core)")),
        MultiFieldPanel([FieldPanel('text_zh'), FieldPanel('text_zh_pinyin')], heading=_("Tiếng Trung & Pinyin")),
        MultiFieldPanel([
            FieldPanel('text_th'), FieldPanel('text_lo'), FieldPanel('text_km'),
            FieldPanel('text_id'), FieldPanel('text_ms'), FieldPanel('text_my'), FieldPanel('text_fil'),
        ], heading=_("Đông Nam Á (SEA)")),
    ]

    def clean(self):
        """
        Validate: Bắt buộc có Tiếng Việt HOẶC Tiếng Trung làm nguồn.
        """
        if not self.text_vi and not self.text_zh:
            raise ValidationError(_("Bạn phải nhập ít nhất nội dung Tiếng Việt hoặc Tiếng Trung để hệ thống có thể dịch tự động."))

    def save(self, *args, **kwargs):
        # 1. Lưu dữ liệu hiện tại vào DB trước (để nhả khóa nhanh nhất có thể)
        super().save(*args, **kwargs)

        # 2. Sử dụng on_commit để gọi AI dịch thuật SAU KHI giao dịch save hoàn tất
        # Điều này tránh việc API call (chậm) giữ khóa DB quá lâu
        if self.text_vi or self.text_zh:
            transaction.on_commit(lambda: self.trigger_auto_translate())

    def trigger_auto_translate(self):
        """
        Hàm helper để gọi AI service và lưu lại kết quả.
        Hàm này sẽ chạy trong một transaction riêng biệt sau khi save() gốc xong.
        """
        from core.ai_services import auto_translate_label
        
        # Refresh object từ DB để đảm bảo dữ liệu mới nhất
        self.refresh_from_db()
        
        # Gọi AI dịch thuật (Hàm này sẽ gọi API và update field)
        updated_instance = auto_translate_label(self)
        
        # Lưu lại các thay đổi do AI tạo ra (dịch bổ sung)
        # Sử dụng update_fields để chỉ update các trường ngôn ngữ, tránh conflict
        # Tuy nhiên, auto_translate_label trả về instance đã set attribute, ta cần save lại.
        # Để an toàn với SQLite, ta dùng super().save() một lần nữa ở đây.
        # Vì nó nằm trong on_commit nên sẽ là một transaction mới, ít gây lock hơn.
        super(SystemLabel, self).save()

    def __str__(self): return f"[{self.get_app_display()}] {self.key}"
    class Meta: verbose_name = _("Nhãn giao diện"); unique_together = ('app', 'key')

# =========================================================
# 4. SIGNALS & DATA SEEDING
# =========================================================
@receiver(post_save, sender=SystemLanguage)
def trigger_scan_on_new_language(sender, instance, created, **kwargs):
    if created:
        try: call_command('scan_system_labels')
        except: pass

@receiver(post_migrate)
def create_default_languages(sender, **kwargs):
    if sender.name == 'core':
        # 1. Core
        SystemLanguage.objects.get_or_create(code='vi', defaults={'name': 'Tiếng Việt', 'flag': '🇻🇳', 'is_core': True})
        SystemLanguage.objects.get_or_create(code='en', defaults={'name': 'English', 'flag': '🇺🇸', 'is_core': True})
        
        # 2. Chinese
        SystemLanguage.objects.get_or_create(code='zh', defaults={'name': 'Tiếng Trung', 'flag': '🇨🇳', 'is_core': False})

        # 3. SEA Languages (Trùng khớp với các field trong model)
        sea_langs = [
            ('th', 'Tiếng Thái', '🇹🇭'),
            ('lo', 'Tiếng Lào', '🇱🇦'),
            ('km', 'Tiếng Khmer', '🇰🇭'),
            ('id', 'Tiếng Indo', '🇮🇩'),
            ('ms', 'Tiếng Malay', '🇲🇾'),
            ('my', 'Tiếng Myanmar', '🇲🇲'),
            ('fil', 'Tiếng Filipino', '🇵🇭'),
        ]
        for code, name, flag in sea_langs:
            SystemLanguage.objects.get_or_create(code=code, defaults={'name': name, 'flag': flag, 'is_core': False})