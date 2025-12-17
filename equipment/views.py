# equipment/views.py
from django.shortcuts import redirect
from wagtail.admin import messages
from django.utils.translation import gettext as _
from django.core.paginator import Paginator
from wagtail.snippets.views.snippets import (
    IndexView,
    CreateView,
    EditView,
    DeleteView,
    InspectView,
    HistoryView,
    UsageView,
    RevisionsCompareView,
    UnpublishView,
    LockView,
    UnlockView,
    PreviewOnCreate,
    PreviewOnEdit
)

from .models import Equipment

# === 1. INDEX VIEW (Danh sách) ===
class EquipmentIndexView(IndexView):
    """
    Custom Index View cho Equipment: Xử lý logic chuyển đổi List/Grid và Query String.
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Xử lý View Mode
        # Lấy tham số 'view' từ URL, mặc định là 'list'
        view_mode = self.request.GET.get('view', 'list')
        context['view_mode'] = view_mode
        
        # 2. Xử lý Query String
        # Giữ lại các tham số query (search, filter) khi chuyển view
        req_copy = self.request.GET.copy()
        if 'view' in req_copy:
            del req_copy['view']
        context['current_query_string'] = req_copy.urlencode()
        
        return context

# === 2. INSPECT VIEW (Chi tiết) ===
class EquipmentInspectView(InspectView):
    """
    Custom Inspect View cho Equipment: Hiển thị chi tiết thiết bị.
    """
    pass

# === 3. CRUD VIEWS (Tạo, Sửa, Xóa) ===
class EquipmentCreateView(CreateView):
    """
    Custom Create View cho Equipment.
    """
    pass

class EquipmentEditView(EditView):
    """
    Custom Edit View cho Equipment.
    """
    pass

class EquipmentDeleteView(DeleteView):
    """
    Custom Delete View cho Equipment.
    """
    pass

# === 4. ADMIN & UTILITY VIEWS ===
class EquipmentUsageView(UsageView):
    """
    Custom Usage View cho Equipment.
    """
    pass

class EquipmentHistoryView(HistoryView):
    """
    Custom History View cho Equipment.
    """
    pass

class EquipmentRevisionsCompareView(RevisionsCompareView):
    """
    Custom Revisions Compare View cho Equipment.
    """
    pass

class EquipmentUnpublishView(UnpublishView):
    """
    Custom Unpublish View cho Equipment.
    """
    pass    

class EquipmentLockView(LockView):
    """
    Custom Lock View cho Equipment.
    """
    pass   

class EquipmentUnlockView(UnlockView):
    """
    Custom Unlock View cho Equipment.
    """
    pass

class EquipmentPreviewOnCreate(PreviewOnCreate):
    """
    Custom Preview On Create View cho Equipment.
    """
    pass    

class EquipmentPreviewOnEdit(PreviewOnEdit):
    """
    Custom Preview On Edit View cho Equipment.
    """
    pass