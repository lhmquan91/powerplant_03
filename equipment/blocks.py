from wagtail import blocks

class TechnicalSpecBlock(blocks.StructBlock):
    """
    Block đại diện cho một dòng thông số kỹ thuật.
    """
    param = blocks.CharBlock(label="Tên thông số", help_text="VD: Lưu lượng, Áp suất, Dòng định mức...")
    value = blocks.CharBlock(label="Giá trị", help_text="VD: 120, 6.6, 3000")
    unit = blocks.CharBlock(label="Đơn vị", required=False, help_text="VD: m3/h, bar, kV, rpm")
    
    is_critical = blocks.BooleanBlock(
        label="Thông số quan trọng?", 
        required=False, 
        help_text="Tích chọn để làm nổi bật thông số này trong bảng hiển thị."
    )

    class Meta:
        icon = 'cogs'
        label = "Thông số"
        # Bạn có thể tạo template riêng để render block này nếu muốn
        # template = 'equipment/blocks/technical_spec_block.html'