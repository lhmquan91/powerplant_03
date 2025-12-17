from django import template
from wagtail.admin.widgets.button import ButtonWithDropdown # Import class này

register = template.Library()

@register.simple_tag(takes_context=True)
def get_snippet_buttons(context, view, instance):
    """
    Lấy danh sách nút và tự động 'làm phẳng' (unwrap) nếu nút đó là một Dropdown.
    Mục đích: Để Grid View có thể render tất cả các nút thành một list dọc duy nhất.
    """
    # 1. Lấy danh sách gốc từ Wagtail (thường chứa: Edit + 1 cái Dropdown to)
    original_buttons = view.get_list_buttons(instance)
    
    flat_buttons = []
    
    for btn in original_buttons:
        # 2. Kiểm tra xem nút này có phải là một cái Dropdown bọc ngoài không?
        if isinstance(btn, ButtonWithDropdown):
            # Nếu phải -> Bóc tách lấy danh sách con (buttons) bên trong
            flat_buttons.extend(btn.dropdown_buttons)
        else:
            # Nếu là nút thường (Edit...) -> Giữ nguyên
            flat_buttons.append(btn)
            
    return flat_buttons