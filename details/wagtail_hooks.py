from django.utils.functional import lazy
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup
from .models import Detail, EquipmentValue
from core.utils import get_label_text # Import hàm lấy nhãn từ core

from .views import (
    DetailIndexView, DetailCreateView, DetailEditView, DetailDeleteView,
    DetailInspectView, DetailUsageView, DetailHistoryView,
    EquipmentValueIndexView, EquipmentValueInspectView,
    EquipmentValueCreateView, EquipmentValueEditView, EquipmentValueDeleteView
)

# =========================================================
# 0. LAZY WRAPPER (Để dùng cho Menu Label)
# =========================================================
def _get_label_lazy_func(app, key, default):
    return get_label_text(app, key, default)

get_label_lazy = lazy(_get_label_lazy_func, str)


# =========================================================
# 1. DETAIL VIEWSET
# =========================================================
class DetailViewSet(SnippetViewSet):
    """
    Quản lý danh mục Tên thông số (Thư viện dùng chung).
    """
    model = Detail
    icon = 'list-ul'
    # Sử dụng get_label_lazy cho menu với chuẩn đặt tên mới: menu_{model}_{context}
    menu_label = get_label_lazy('details', 'menu_detail_library', 'Danh mục Thông số')
    menu_name = 'detail_library'
    
    # Hiển thị tên Tiếng Việt trong bảng
    list_display = ['name_vi', 'default_unit']
    search_fields = ['name_vi', 'name_en', 'name_zh'] # Tìm kiếm trên nhiều ngôn ngữ
    
    # --- A. GẮN KẾT CUSTOM VIEW CLASS ---
    index_view_class = DetailIndexView
    add_view_class = DetailCreateView
    edit_view_class = DetailEditView
    delete_view_class = DetailDeleteView
    inspect_view_class = DetailInspectView
    inspect_view_enabled = True
    usage_view_class = DetailUsageView
    history_view_class = DetailHistoryView

    # --- B. ĐỊNH NGHĨA TEMPLATE PATHS ---
    index_template_name = 'details/detail/index.html'
    results_template_name = 'details/detail/index_results.html'
    create_template_name = 'details/detail/create.html'
    edit_template_name = 'details/detail/edit.html'
    delete_template_name = 'details/detail/delete.html'
    inspect_template_name = 'details/detail/inspect.html'
    usage_template_name = 'details/detail/usage.html'
    history_template_name = 'details/detail/history.html'


# =========================================================
# 2. EQUIPMENT VALUE VIEWSET
# =========================================================
class EquipmentValueViewSet(SnippetViewSet):
    model = EquipmentValue
    icon = 'table'
    # Chuẩn hóa key: menu_equipmentvalue_list
    menu_label = get_label_lazy('details', 'menu_equipmentvalue_list', 'Dữ liệu đo đạc')
    menu_name = 'equipment_values'
    
    index_view_class = EquipmentValueIndexView
    inspect_view_class = EquipmentValueInspectView
    inspect_view_enabled = True
    add_view_class = EquipmentValueCreateView
    edit_view_class = EquipmentValueEditView
    delete_view_class = EquipmentValueDeleteView
    
    list_display = ['equipment', 'detail', 'value', 'unit']
    list_filter = ['detail', 'equipment__location']
    search_fields = ('value', 'equipment__name', 'detail__name_vi')

    def get_admin_urls_for_registration(self):
        urls = super().get_admin_urls_for_registration()
        return [url for url in urls if url.name in (
            self.get_url_name('index'), self.get_url_name('inspect'), self.get_url_name('history'),
        )]

# =========================================================
# 3. GOM NHÓM MENU (GROUP)
# =========================================================
class DetailsAppGroup(SnippetViewSetGroup):
    # Chuẩn hóa key: menu_details_group
    menu_label = get_label_lazy('details', 'menu_details_group', 'Quản lý Thông số')
    menu_icon = 'cogs'
    menu_order = 300
    items = (DetailViewSet, EquipmentValueViewSet)

register_snippet(DetailsAppGroup)