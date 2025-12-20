from django import template
from django.utils.safestring import mark_safe
from core.utils import get_label_text

register = template.Library()

@register.simple_tag(takes_context=False)
def get_label(app, key, default_text=None):
    """
    Template tag để lấy nhãn dịch thuật từ DB.
    Sử dụng: {% get_label 'details' 'ui_create_help' 'Default text...' %}
    """
    # Gọi hàm logic từ utils
    label_content = get_label_text(app, key, default_text)
    
    # Sử dụng mark_safe để cho phép render HTML trong nhãn 
    # (VD: "Nhập <b>Tên</b>" sẽ in đậm chữ Tên thay vì hiện thẻ <b>)
    if label_content:
        return mark_safe(label_content)
    
    return ""