import logging
from django.utils.translation import get_language
from django.core.cache import cache
from core.models import SystemLabel

# Cấu hình Logger
logger = logging.getLogger(__name__)

MISSING_KEY_SENTINEL = "__MISSING__"

def get_label_text(app, key, default_text=None):
    """
    Hàm helper lấy nhãn (Hỗ trợ các trường ngôn ngữ cụ thể).
    """
    current_lang = get_language() or 'vi'
    lang_code = current_lang

    cache_key = f"sys_label_v6_{app}_{key}_{lang_code}"
    
    cached_value = cache.get(cache_key)
    if cached_value is not None:
        if cached_value == MISSING_KEY_SENTINEL:
            return default_text or key
        return cached_value

    try:
        label = SystemLabel.objects.filter(app=app, key=key).first()
        
        if label:
            result_text = ""
            
            field_name = f"text_{lang_code}"
            if '-' in lang_code:
                prefix = lang_code.split('-')[0]
                field_name = f"text_{prefix}"

            if hasattr(label, field_name):
                result_text = getattr(label, field_name)
            
            if not result_text:
                result_text = label.text_en
            if not result_text:
                result_text = label.text_vi

            final_val = result_text if result_text else MISSING_KEY_SENTINEL
            result = result_text if result_text else (default_text or key)
        else:
            final_val = MISSING_KEY_SENTINEL
            result = default_text or key
        
        cache.set(cache_key, final_val, 3600)
        return result
        
    except Exception:
        return default_text or key

class DynamicLabelMixin:
    app_name = 'common'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field_name, field in form.fields.items():
            label_key = f"field_{field_name}_label"
            field.label = get_label_text(self.app_name, label_key, default_text=field.label)
            help_key = f"field_{field_name}_help"
            field.help_text = get_label_text(self.app_name, help_key, default_text=field.help_text)
        return form

    def get_page_title(self):
        view_name = self.__class__.__name__.replace('View', '').lower()
        key = f"view_{view_name}_title"
        default_title = super().get_page_title()
        return get_label_text(self.app_name, key, default_title)

    def get_success_message(self, instance=None):
        """
        Log chi tiết để debug lỗi TypeError.
        """
        # DEBUG LOG START
        logger.info(f"🔍 [DEBUG] get_success_message called in View: {self.__class__.__name__}")
        logger.info(f"   - Input instance: {instance}")
        
        # 1. Tự động lấy instance nếu không được truyền vào (Trường hợp EditView/CreateView)
        if instance is None:
            instance = getattr(self, 'object', None)
            logger.info(f"   - Instance retrieved from self.object: {instance}")
        
        # 2. Lấy nội dung message từ SystemLabel
        view_name = self.__class__.__name__.replace('View', '').lower()
        key = f"msg_{view_name}_success"
        
        msg_template = get_label_text(self.app_name, key, default_text=None)
        logger.info(f"   - Message Template found: {msg_template}")
        
        if msg_template and instance:
            formatted_msg = msg_template.format(object=instance)
            logger.info(f"   - Returning formatted message: {formatted_msg}")
            return formatted_msg
            
        # 3. Fallback về mặc định của Wagtail (Gọi super)
        logger.info("   - No custom message found, calling super()...")
        
        try:
            # Thử gọi với tham số (cho DeleteView cũ)
            return super().get_success_message(instance)
        except TypeError as e:
            logger.warning(f"   - super(instance) failed ({e}), trying no-arg call...")
            # Nếu lỗi, thử gọi không tham số (cho EditView/CreateView mới)
            return super().get_success_message()