# area/wagtail_hooks.py
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.admin.ui.tables import UpdatedAtColumn
from wagtail.admin.widgets.button import BaseButton
from django.urls import reverse
from wagtail import hooks
from django.utils.translation import gettext_lazy as _

from .models import FunctionalLocation
# Import toàn bộ các Views từ file views.py vừa tạo
from .views import (
    FunctionalLocationIndexView,
    FunctionalLocationInspectView,
    FunctionalLocationCreateView,
    FunctionalLocationEditView,
    FunctionalLocationDeleteView,
    FunctionalLocationUsageView,
    FunctionalLocationHistoryView,
    FunctionalLocationRevisionsCompareView,
    FunctionalLocationUnpublishView,
    FunctionalLocationLockView,
    FunctionalLocationUnlockView,
    FunctionalLocationPreviewOnCreate,
    FunctionalLocationPreviewOnEdit
)

class FunctionalLocationViewSet(SnippetViewSet):
    model = FunctionalLocation
    icon = 'site'
    menu_label = 'Khu vực'
    menu_name = 'functional_location'
    menu_order = 200
    add_to_admin_menu = True
    
    # --- A. GẮN KẾT CUSTOM VIEW CLASS ---
    index_view_class = FunctionalLocationIndexView
    add_view_class = FunctionalLocationCreateView
    edit_view_class = FunctionalLocationEditView
    delete_view_class = FunctionalLocationDeleteView
    inspect_view_class = FunctionalLocationInspectView
    inspect_view_enabled = True # Bắt buộc để kích hoạt trang Inspect

    usage_view_class = FunctionalLocationUsageView
    history_view_class = FunctionalLocationHistoryView
    revisions_compare_view_class = FunctionalLocationRevisionsCompareView
    unpublish_view_class = FunctionalLocationUnpublishView
    lock_view_class = FunctionalLocationLockView
    unlock_view_class = FunctionalLocationUnlockView
    preview_on_add_view_class = FunctionalLocationPreviewOnCreate
    preview_on_edit_view_class = FunctionalLocationPreviewOnEdit

    # --- B. ĐỊNH NGHĨA TEMPLATE PATHS (Tường minh) ---
    # Các file này nằm trong thư mục: area/templates/area/admin/
    index_template_name = 'area/admin/index.html'
    inspect_template_name = 'area/admin/inspect.html'
    
    # Các template này hiện tại sẽ fallback về mặc định của Wagtail nếu bạn chưa tạo file.
    # Khi cần custom, chỉ cần tạo file tại đúng đường dẫn này:
    create_template_name = 'area/admin/create.html'
    edit_template_name = 'area/admin/edit.html'
    delete_template_name = 'area/admin/delete.html'
    history_template_name = 'area/admin/history.html'
    usage_template_name = 'area/admin/usage.html'

    # --- C. CẤU HÌNH HIỂN THỊ DANH SÁCH ---
    list_display = [
        'kks_display', 
        'name_inspect_link', 
        'parent_display',
        'audio_status_display', 
        UpdatedAtColumn(label="Cập nhật"),
    ]
    
    list_filter = ['kks_code']
    search_fields = ('name', 'kks_code')
    list_per_page = 20

    copy_view_enabled = True

register_snippet(FunctionalLocationViewSet)

# 2. GOM NHÓM (Construct)
@hooks.register('construct_snippet_listing_buttons')
def construct_custom_snippet_buttons(buttons, snippet, user, context=None):
    if isinstance(snippet, FunctionalLocation):
        for button in buttons:
            # 1. Ép tất cả vào Dropdown
            button.allow_in_dropdown = True
            
            # 2. Xóa sạch class mặc định (để giống trang List: class="")
            button.classname = "" 
            
            # 3. Sắp xếp
            if button.label == 'Edit': button.priority = 10
            elif button.label == 'Copy': button.priority = 20
            elif button.label == 'Inspect': button.priority = 30
            elif button.label == 'Delete': button.priority = 100