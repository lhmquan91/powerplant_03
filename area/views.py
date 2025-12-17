# area/views.py
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

from .models import FunctionalLocation

# === 1. INDEX VIEW (Danh sách) ===
class FunctionalLocationIndexView(IndexView):
    """
    Custom Index View: Xử lý chuyển đổi giao diện List/Grid.
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Lấy chế độ xem từ URL, mặc định là 'grid' (theo code cũ của bạn)
        context['view_mode'] = self.request.GET.get('view', 'grid')
        
        # Giữ lại query string (search/filter) khi chuyển đổi view
        req_copy = self.request.GET.copy()
        if 'view' in req_copy: del req_copy['view']
        context['current_query_string'] = req_copy.urlencode()
        
        return context


# === 2. INSPECT VIEW (Chi tiết) ===
class FunctionalLocationInspectView(InspectView):
    """
    Custom Inspect View: Hiển thị chi tiết Area + Danh sách Equipment con (có phân trang).
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Lấy danh sách thiết bị con, sắp xếp theo KKS
        # Lưu ý: Model Equipment cần có related_name='equipments' khi ForeignKey tới Area
        equipments_qs = self.object.equipments.all().order_by('kks_code')
        
        # 2. Xử lý View Mode cho danh sách thiết bị con (Grid/List)
        view_mode = self.request.GET.get('view', 'list') 
        context['view_mode'] = view_mode
        
        # 3. Xử lý Phân trang (Pagination) cho thiết bị
        paginator = Paginator(equipments_qs, 10) # 10 thiết bị mỗi trang
        page_number = self.request.GET.get('p')
        page_obj = paginator.get_page(page_number)
        context['equipments'] = page_obj
        
        # 4. Giữ lại query string
        req_copy = self.request.GET.copy()
        if 'p' in req_copy: del req_copy['p']
        context['current_query_string'] = req_copy.urlencode()
        
        return context


# === 3. CRUD VIEWS (Tạo, Sửa, Xóa) ===
class FunctionalLocationCreateView(CreateView):
    """
    Custom Create View để xử lý logic tạo Node cho Treebeard.
    """
    def form_valid(self, form):
        # 1. Ngừng lưu vào DB ngay lập tức (commit=False)
        # Để tránh lỗi IntegrityError do thiếu depth/path
        instance = form.save(commit=False)
        
        # 2. Lấy thông tin cha từ trường parent_selection chúng ta vừa tạo
        parent = form.cleaned_data.get('parent_selection')

        # 3. Sử dụng API của Treebeard để tạo Node
        try:
            if parent:
                # Nếu có chọn cha -> Tạo node con
                # add_child() sẽ tự động tính toán depth/path và lưu vào DB
                parent.add_child(instance=instance)
            else:
                # Nếu không chọn cha -> Tạo node gốc (Root)
                FunctionalLocation.add_root(instance=instance)
                
            # 4. Thông báo thành công
            messages.success(
                self.request, 
                _("Khu vực '%(name)s' đã được tạo thành công.") % {'name': instance.name}
            )
            
            # 5. Redirect về trang danh sách (hoặc trang Inspect vừa tạo)
            return redirect('wagtailsnippets_area_functionallocation:list')
            
        except Exception as e:
            # Xử lý lỗi nếu có
            messages.error(self.request, f"Đã xảy ra lỗi khi tạo cây: {e}")
            return super().form_invalid(form)

class FunctionalLocationEditView(EditView):
    pass

class FunctionalLocationDeleteView(DeleteView):
    pass


# === 4. ADMIN & UTILITY VIEWS ===
class FunctionalLocationUsageView(UsageView):
    pass

class FunctionalLocationHistoryView(HistoryView):
    pass

class FunctionalLocationRevisionsCompareView(RevisionsCompareView):
    pass

class FunctionalLocationUnpublishView(UnpublishView):
    pass

class FunctionalLocationLockView(LockView):
    pass

class FunctionalLocationUnlockView(UnlockView):
    pass

class FunctionalLocationPreviewOnCreate(PreviewOnCreate):
    pass

class FunctionalLocationPreviewOnEdit(PreviewOnEdit):
    pass