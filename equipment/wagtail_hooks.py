from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.admin.ui.tables import UpdatedAtColumn

from .models import Equipment

from .views import (
    EquipmentIndexView,
    EquipmentInspectView,
    EquipmentCreateView,
    EquipmentEditView,
    EquipmentDeleteView,
    EquipmentUsageView,
    EquipmentHistoryView,
    EquipmentRevisionsCompareView,
    EquipmentUnpublishView,
    EquipmentLockView,
    EquipmentUnlockView,
    EquipmentPreviewOnCreate,
    EquipmentPreviewOnEdit
)

class EquipmentViewSet(SnippetViewSet):
    model = Equipment
    icon = 'cogs'
    menu_label = 'Thiết bị'
    menu_name = 'equipment'
    menu_order = 201 # Ngay sau Area
    add_to_admin_menu = True

    #-- A. GẮN KẾT CUSTOM VIEW CLASS ---
    index_view_class = EquipmentIndexView
    add_view_class = EquipmentCreateView
    edit_view_class = EquipmentEditView
    delete_view_class = EquipmentDeleteView
    inspect_view_class = EquipmentInspectView
    inspect_view_enabled = True # Bắt buộc để kích hoạt trang Inspect

    usage_view_class = EquipmentUsageView
    history_view_class = EquipmentHistoryView
    revisions_compare_view_class = EquipmentRevisionsCompareView
    unpublish_view_class = EquipmentUnpublishView
    lock_view_class = EquipmentLockView
    unlock_view_class = EquipmentUnlockView
    preview_on_add_view_class = EquipmentPreviewOnCreate
    preview_on_edit_view_class = EquipmentPreviewOnEdit

    # -- B. ĐỊNH NGHĨA TEMPLATE PATHS (Tường minh) ---
    # Các file này nằm trong thư mục: equipment/templates/equipment/admin/
    index_template_name = 'equipment/admin/index.html'
    inspect_template_name = 'equipment/admin/inspect.html'

    # Các template này hiện tại sẽ fallback về mặc định của Wagtail nếu bạn chưa tạo file.
    # Khi cần custom, chỉ cần tạo file tại đúng đường dẫn này:
    create_template_name = 'equipment/admin/create.html'
    edit_template_name = 'equipment/admin/edit.html'
    delete_template_name = 'equipment/admin/delete.html'
    history_template_name = 'equipment/admin/history.html'
    usage_template_name = 'equipment/admin/usage.html'

    # -- C. CẤU HÌNH BẢNG DANH SÁCH (INDEX TABLE) ---
    list_display = [
        'kks_display',          # <-- Đã di chuyển
        'name_inspect_link',
        'location_link',        # <-- Đã di chuyển
        'manufacturer',
        'specs_count',          # <-- Đã di chuyển
        'audio_status_display', # <-- Đã di chuyển
        UpdatedAtColumn(label="Cập nhật"),
    ]
    
    list_filter = ['location', 'manufacturer']
    search_fields = ('name', 'kks_code', 'model_number')
    list_per_page = 20

register_snippet(EquipmentViewSet)