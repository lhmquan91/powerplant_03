from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup
from wagtail.admin.ui.tables import UpdatedAtColumn
from .models import DetailGroup, Detail, EquipmentValue

from .views import (
    DetailIndexView, DetailCreateView, DetailEditView, DetailDeleteView,
    DetailInspectView, DetailUsageView, DetailHistoryView,
    DetailRevisionsCompareView, DetailUnpublishView, DetailLockView, DetailUnlockView,

    DetailGroupIndexView, DetailGroupCreateView, DetailGroupEditView, DetailGroupDeleteView,
    DetailGroupInspectView, DetailGroupUsageView, DetailGroupHistoryView,
    DetailGroupRevisionsCompareView, DetailGroupUnpublishView, DetailGroupLockView, DetailGroupUnlockView,

    EquipmentValueIndexView
)

# ===============================
# === 1. DETAIL GROUP VIEWSET ===
# ===============================

class DetailGroupViewSet(SnippetViewSet):
    model = DetailGroup
    icon = 'folder-open-inverse'
    menu_label = 'Nhóm Thông số'
    menu_name = 'detail_group'

    # ------------------------------------
    # --- A. GẮN KẾT CUSTOM VIEW CLASS ---
    # ------------------------------------

    # 1. CRUD Views
    index_view_class = DetailGroupIndexView
    add_view_class = DetailGroupCreateView
    edit_view_class = DetailGroupEditView
    delete_view_class = DetailGroupDeleteView
    inspect_view_class = DetailGroupInspectView
    inspect_view_enabled = True # Phải bật lên mới dùng được

    # 2. Admin Views
    usage_view_class = DetailGroupUsageView
    history_view_class = DetailGroupHistoryView

    # 3. Revision Views (Nếu model có hỗ trợ)
    revisions_compare_view_class = DetailGroupRevisionsCompareView
    unpublish_view_class = DetailGroupUnpublishView

    # 4. Locking Views (Nếu model có hỗ trợ)
    lock_view_class = DetailGroupLockView
    unlock_view_class = DetailGroupUnlockView

    # ------------------------------------
    # --- B. ĐỊNH NGHĨA TEMPLATE PATHS ---
    # ------------------------------------

    index_template_name = 'details/detail_group/index.html'
    results_template_name = 'details/detail_group/index_results.html'
    create_template_name = 'details/detail_group/create.html'
    edit_template_name = 'details/detail_group/edit.html'
    delete_template_name = 'details/detail_group/delete.html'
    inspect_template_name = 'details/detail_group/inspect.html'
    history_template_name = 'details/detail_group/history.html'
    usage_template_name = 'details/detail_group/usage.html'

    # ----------------------------
    # --- C. CẤU HÌNH HIỂN THỊ ---
    # ----------------------------
    
    list_display = [
        'name',
        'get_details_count',  # Hàm này nằm trong Model (đã fix lỗi lookup)
        'is_active',
        UpdatedAtColumn(label="Cập nhật"),
    ]
    search_fields = ('name', 'description')

# =========================
# === 2. DETAIL VIEWSET ===
# =========================

class DetailViewSet(SnippetViewSet):
    model = Detail
    icon = 'list-ul'
    menu_label = 'Thông số'
    menu_name = 'detail'

    # ------------------------------------
    # --- A. GẮN KẾT CUSTOM VIEW CLASS ---
    # ------------------------------------
    
    # 1. CRUD Views
    index_view_class = DetailIndexView
    add_view_class = DetailCreateView
    edit_view_class = DetailEditView
    delete_view_class = DetailDeleteView
    inspect_view_class = DetailInspectView
    inspect_view_enabled = True # Phải bật lên mới dùng được
    
    # 2. Admin Views
    usage_view_class = DetailUsageView
    history_view_class = DetailHistoryView
    
    # 3. Revision Views (Nếu model có hỗ trợ)
    revisions_compare_view_class = DetailRevisionsCompareView
    unpublish_view_class = DetailUnpublishView
    
    # 4. Locking Views (Nếu model có hỗ trợ)
    lock_view_class = DetailLockView
    unlock_view_class = DetailUnlockView

    # ------------------------------------
    # --- B. ĐỊNH NGHĨA TEMPLATE PATHS ---
    # ------------------------------------

    index_template_name = 'details/detail/index.html'
    results_template_name = 'details/detail/index_results.html'
    create_template_name = 'details/detail/create.html'
    edit_template_name = 'details/detail/edit.html'
    delete_template_name = 'details/detail/delete.html'
    inspect_template_name = 'details/detail/inspect.html'
    history_template_name = 'details/detail/history.html'
    usage_template_name = 'details/detail/usage.html'
    
    # ----------------------------
    # --- C. CẤU HÌNH HIỂN THỊ ---
    # ----------------------------

    list_display = [
        'name',
        'group_name', # Hàm này nằm trong Model
        'unit',
        'data_type',
        'is_active',
    ]
    list_filter = ['group', 'data_type', 'is_active']
    search_fields = ('name', 'unit')

# ==============================================
# === 3. EQUIPMENT VALUE VIEWSET (Read-Only) ===
# ==============================================

class EquipmentValueViewSet(SnippetViewSet):
    model = EquipmentValue
    icon = 'table'
    menu_label = 'Giá trị'
    menu_name = 'equipment_value'

    # ------------------------------------
    # --- A. GẮN KẾT CUSTOM VIEW CLASS ---
    # ------------------------------------
    # 1. CRUD Views
    index_view_class = EquipmentValueIndexView
    # Chỉ cho phép xem danh sách, không cho phép tạo/sửa/xóa

    # ------------------------------------
    # --- B. ĐỊNH NGHĨA TEMPLATE PATHS ---
    # ------------------------------------
    index_template_name = 'details/equipment_value/index.html'
    results_template_name = 'details/equipment_value/index_results.html'
    # Không có create/edit/delete templates vì không cho phép thao tác
    
    ordering = ('-measured_at',)
    search_fields = ('equipment__kks_code', 'detail__name', 'value')
    
    list_display = [
        'equipment_name', # Hàm này nằm trong Model
        'detail_name',    # Hàm này nằm trong Model
        'value', 
        'measured_at'
    ]
    
    list_filter = ['detail__group', 'detail', 'measured_at']

    # Khóa nút "Add"
    def get_buttons_for_model(self, model):
        return []
    
    # Khóa link Edit/Create
    def get_admin_urls(self):
        urls = super().get_admin_urls()
        return [url for url in urls if 'create' not in url.name and 'edit' not in url.name]

# ================================
# === 4. GOM NHÓM MENU (GROUP) ===
# ================================

class DetailsAppGroup(SnippetViewSetGroup):
    """
    Tạo menu cha 'Quản lý Thông số' chứa 3 menu con ở trên.
    """
    menu_label = "Quản lý Thông số"
    menu_icon = "cogs" # Icon bánh răng tổng
    menu_order = 250
    
    # Danh sách các ViewSet con nằm trong nhóm này
    items = (DetailGroupViewSet, DetailViewSet, EquipmentValueViewSet)

# Chỉ đăng ký Group, không đăng ký lẻ từng ViewSet
register_snippet(DetailsAppGroup)