from django.utils.translation import gettext as _
from wagtail.snippets.views.snippets import (
    IndexView,
    CreateView,
    EditView,
    DeleteView,
    InspectView,
    UsageView,
    HistoryView,
)

from .models import Detail, EquipmentValue
from core.utils import get_label_text, DynamicLabelMixin
from core.models import SystemLanguage

# =========================================================
# 1. DETAIL VIEWS (Sử dụng Global Mixin từ Core)
# =========================================================

class DetailIndexView(DynamicLabelMixin, IndexView):
    app_name = 'details'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Truyền danh sách mã ngôn ngữ đang active vào context (VD: ['vi', 'en', 'zh'])
        context['active_codes'] = list(SystemLanguage.objects.filter(is_active=True).values_list('code', flat=True))
        return context

class DetailCreateView(DynamicLabelMixin, CreateView):
    app_name = 'details'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Lấy danh sách ngôn ngữ KHÔNG kích hoạt
        inactive_codes = list(SystemLanguage.objects.filter(is_active=False).values_list('code', flat=True))
        
        # Danh sách tất cả các suffix ngôn ngữ có thể có trong model Detail
        # (Không bao gồm vi/en vì là core)
        all_suffixes = ['zh', 'th', 'lo', 'km', 'id', 'ms', 'my', 'fil']
        
        for code in all_suffixes:
            # Nếu ngôn ngữ này nằm trong danh sách Inactive hoặc không tồn tại trong DB
            # (Logic: code nằm trong inactive_codes HOẶC code không nằm trong active_codes thực tế)
            # Cách đơn giản: Nếu code thuộc inactive_codes thì ẩn
            if code in inactive_codes:
                # Xây dựng tên trường
                fields_to_hide = [f'name_{code}']
                if code == 'zh':
                    fields_to_hide.append('name_zh_pinyin')
                
                # Xóa khỏi form
                for field_name in fields_to_hide:
                    if field_name in form.fields:
                        del form.fields[field_name]
        return form

class DetailEditView(DynamicLabelMixin, EditView):
    app_name = 'details'
    
    # Áp dụng logic ẩn field tương tự CreateView
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        inactive_codes = list(SystemLanguage.objects.filter(is_active=False).values_list('code', flat=True))
        all_suffixes = ['zh', 'th', 'lo', 'km', 'id', 'ms', 'my', 'fil']
        
        for code in all_suffixes:
            if code in inactive_codes:
                fields_to_hide = [f'name_{code}']
                if code == 'zh':
                    fields_to_hide.append('name_zh_pinyin')
                for field_name in fields_to_hide:
                    if field_name in form.fields:
                        del form.fields[field_name]
        return form

class DetailDeleteView(DeleteView):
    def get_page_title(self):
        return get_label_text('details', 'view_delete_title', 'Xóa thông số')

    def get_success_message(self, instance):
        msg = get_label_text('details', 'msg_delete_success', "Đã xóa thành công '{object}'")
        return msg.format(object=instance)

class DetailInspectView(InspectView):
    def get_page_title(self):
        return get_label_text('details', 'view_inspect_title', 'Chi tiết thông số')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Truyền active_codes để template Inspect ẩn/hiện các block
        context['active_codes'] = list(SystemLanguage.objects.filter(is_active=True).values_list('code', flat=True))
        return context

class DetailUsageView(UsageView):
    def get_page_title(self):
        return get_label_text('details', 'view_usage_title', 'Trạng thái sử dụng')

class DetailHistoryView(HistoryView):
    def get_page_title(self):
        return get_label_text('details', 'view_history_title', 'Lịch sử thay đổi')


# =========================================================
# 2. EQUIPMENT VALUE VIEWS (Read-only)
# =========================================================

class EquipmentValueIndexView(IndexView):
    def get_page_title(self):
        return get_label_text('details', 'view_eq_value_index_title', 'Dữ liệu đo đạc toàn hệ thống')

class EquipmentValueInspectView(InspectView):
    pass

class EquipmentValueCreateView(CreateView): pass
class EquipmentValueEditView(EditView): pass
class EquipmentValueDeleteView(DeleteView): pass