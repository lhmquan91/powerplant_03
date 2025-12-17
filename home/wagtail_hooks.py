from wagtail import hooks

@hooks.register('construct_main_menu')
def hide_explorer_menu_item(request, menu_items):
    # Lọc bỏ item có tên là 'explorer' (đây là tên nội bộ của menu Pages)
    menu_items[:] = [item for item in menu_items if item.name != 'explorer']