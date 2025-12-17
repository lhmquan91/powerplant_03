from django.shortcuts import redirect
from wagtail.admin import messages

# Import các View cơ sở từ Wagtail Snippets
#
from wagtail.snippets.views.snippets import (
    IndexView,
    CreateView,
    EditView,
    DeleteView,
    InspectView,
    HistoryView,
    UsageView,
    RevisionsCompareView,
    RevisionsUnscheduleView,
    UnpublishView,
    LockView,
    UnlockView,
    PreviewOnCreate,
    PreviewOnEdit
)

from .models import DetailGroup

# =======================
# === 1. DETAIL VIEWS ===
# =======================

# --- 1. LOGIC BẢO VỆ (MIXIN) ---

class DetailGroupRequiredMixin:
    """
    Mixin cho Detail.
    """
    def dispatch(self, request, *args, **kwargs):
        """
        Chặn truy cập nếu chưa có DetailGroup.
        Áp dụng cho các trang thao tác dữ liệu (List, Add, Edit).
        Nếu chưa có DetailGroup, chuyển hướng về trang danh sách DetailGroup
        """
        if not DetailGroup.objects.exists():
            messages.warning(
                request, 
                "Bạn cần tạo ít nhất một 'Nhóm Thông số' (Group) trước khi định nghĩa Chi tiết."
            )
            return redirect('wagtailsnippets_details_detailgroup:list')
        return super().dispatch(request, *args, **kwargs)


# --- 2. CÁC VIEW CHÍNH (CRUD) ---

class DetailIndexView(DetailGroupRequiredMixin, IndexView):
    """
    Trang danh sách (List View).
    Mặc định: Hiển thị bảng dữ liệu, bộ lọc, tìm kiếm.
    """
    pass

class DetailCreateView(DetailGroupRequiredMixin, CreateView):
    """
    Trang thêm mới (Add View).
    Mặc định: Hiển thị Form tạo mới.
    """
    pass

class DetailEditView(DetailGroupRequiredMixin, EditView):
    """
    Trang chỉnh sửa (Edit View).
    Mặc định: Hiển thị Form chỉnh sửa.
    """
    pass

class DetailDeleteView(DetailGroupRequiredMixin, DeleteView):
    """
    Trang xóa (Delete View).
    Mặc định: Hiển thị trang xác nhận xóa.
    """
    pass

class DetailInspectView(DetailGroupRequiredMixin, InspectView):
    """
    Trang xem chi tiết (Inspect View).
    Mặc định: Hiển thị thông tin readonly của object (key-value).
    """
    pass


# --- 3. CÁC VIEW QUẢN TRỊ & TIỆN ÍCH ---

class DetailUsageView(DetailGroupRequiredMixin, UsageView):
    """
    Trang Usage.
    Mặc định: Hiển thị nơi snippet này đang được sử dụng (liên kết với Page nào).
    """
    pass

class DetailHistoryView(DetailGroupRequiredMixin, HistoryView):
    """
    Trang lịch sử (History).
    Mặc định: Hiển thị log các lần thay đổi, ai sửa, sửa lúc nào.
    """
    pass


# --- 4. CÁC VIEW LIÊN QUAN ĐẾN REVISION & PUBLISH ---
# (Chỉ hoạt động nếu Model kế thừa RevisionMixin / DraftStateMixin)

class DetailRevisionsCompareView(DetailGroupRequiredMixin, RevisionsCompareView):
    """So sánh sự khác biệt giữa 2 phiên bản."""
    pass

class DetailRevisionsUnscheduleView(DetailGroupRequiredMixin, RevisionsUnscheduleView):
    """Hủy lịch xuất bản."""
    pass

class DetailUnpublishView(DetailGroupRequiredMixin, UnpublishView):
    """Gỡ bỏ xuất bản (Unpublish)."""
    pass


# --- 5. CÁC VIEW LIÊN QUAN ĐẾN LOCKING ---
# (Chỉ hoạt động nếu Model kế thừa LockableMixin)

class DetailLockView(DetailGroupRequiredMixin, LockView):
    """Khóa vật phẩm (không cho người khác sửa)."""
    pass

class DetailUnlockView(DetailGroupRequiredMixin, UnlockView):
    """Mở khóa vật phẩm."""
    pass

# --- 6. CÁC VIEW PREVIEW (Xem trước) ---
# (Chỉ hoạt động nếu Model kế thừa PreviewableMixin)

class DetailPreviewOnCreate(DetailGroupRequiredMixin, PreviewOnCreate):
    pass

class DetailPreviewOnEdit(DetailGroupRequiredMixin, PreviewOnEdit):
    pass


# =============================
# === 2. DETAIL GROUP VIEWS ===
# =============================

# --- 1. LOGIC BẢO VỆ (MIXIN) ---

class DetailGroupRequiredMixin:
    """
    Mixin cho DetailGroup.
    """
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    

# --- 2. CÁC VIEW CHÍNH (CRUD) ---

class DetailGroupIndexView(DetailGroupRequiredMixin, IndexView):
    """
    Trang danh sách (List View) cho DetailGroup.
    Mặc định: Hiển thị bảng dữ liệu, bộ lọc, tìm kiếm.
    """
    pass

class DetailGroupCreateView(DetailGroupRequiredMixin, CreateView):
    """
    Trang thêm mới (Add View) cho DetailGroup.
    Mặc định: Hiển thị Form tạo mới.
    """
    pass

class DetailGroupEditView(DetailGroupRequiredMixin, EditView):
    """
    Trang chỉnh sửa (Edit View) cho DetailGroup.
    Mặc định: Hiển thị Form chỉnh sửa.
    """
    pass

class DetailGroupDeleteView(DetailGroupRequiredMixin, DeleteView):
    """
    Trang xóa (Delete View) cho DetailGroup.
    Mặc định: Hiển thị trang xác nhận xóa.
    """
    pass

class DetailGroupInspectView(DetailGroupRequiredMixin, InspectView):
    """
    Trang xem chi tiết (Inspect View) cho DetailGroup.
    Mặc định: Hiển thị thông tin readonly của object (key-value).
    """
    pass

# --- 3. CÁC VIEW QUẢN TRỊ & TIỆN ÍCH ---

class DetailGroupUsageView(DetailGroupRequiredMixin, UsageView):
    """
    Trang Usage cho DetailGroup.
    Mặc định: Hiển thị nơi snippet này đang được sử dụng (liên kết với Page nào).
    """
    pass

class DetailGroupHistoryView(DetailGroupRequiredMixin, HistoryView):
    """
    Trang lịch sử (History) cho DetailGroup.
    Mặc định: Hiển thị log các lần thay đổi, ai sửa, sửa lúc nào.
    """
    pass

# --- 4. CÁC VIEW LIÊN QUAN ĐẾN REVISION & PUBLISH ---
# (Chỉ hoạt động nếu Model kế thừa RevisionMixin / DraftStateMixin)

class DetailGroupRevisionsCompareView(DetailGroupRequiredMixin, RevisionsCompareView):
    """So sánh sự khác biệt giữa 2 phiên bản cho DetailGroup."""
    pass

class DetailGroupRevisionsUnscheduleView(DetailGroupRequiredMixin, RevisionsUnscheduleView):
    """Hủy lịch xuất bản cho DetailGroup."""
    pass

class DetailGroupUnpublishView(DetailGroupRequiredMixin, UnpublishView):
    """Gỡ bỏ xuất bản (Unpublish) cho DetailGroup."""
    pass

# --- 5. CÁC VIEW LIÊN QUAN ĐẾN LOCKING ---
# (Chỉ hoạt động nếu Model kế thừa LockableMixin)

class DetailGroupLockView(DetailGroupRequiredMixin, LockView):
    """Khóa vật phẩm (không cho người khác sửa) cho DetailGroup."""
    pass

class DetailGroupUnlockView(DetailGroupRequiredMixin, UnlockView):
    """Mở khóa vật phẩm cho DetailGroup."""
    pass

# --- 6. CÁC VIEW PREVIEW (Xem trước) ---
# (Chỉ hoạt động nếu Model kế thừa PreviewableMixin)

class DetailGroupPreviewOnCreate(DetailGroupRequiredMixin, PreviewOnCreate):
    pass

class DetailGroupPreviewOnEdit(DetailGroupRequiredMixin, PreviewOnEdit):
    pass

# ================================
# === 3. EQUIPMENT VALUE VIEWS ===
# ================================

# --- 1. LOGIC BẢO VỆ (MIXIN) ---

class EquipmentValueRequiredMixin:
    """
    Mixin cho DetailGroup.
    """
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
# --- 2. CÁC VIEW CHÍNH (CRUD) ---

class EquipmentValueIndexView(EquipmentValueRequiredMixin, IndexView):
    """
    Trang danh sách (List View) cho EquipmentValue.
    Mặc định: Hiển thị bảng dữ liệu, bộ lọc, tìm kiếm.
    """
    pass