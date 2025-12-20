from django.urls import path, reverse
from django.utils.translation import get_language
from django.shortcuts import redirect
from django.utils import translation
from wagtail.users.models import UserProfile
from wagtail import hooks
from wagtail.admin.menu import MenuItem
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup
from .models import SystemLabel, SystemLanguage, AIPrompt # Thêm AIPrompt

LANGUAGE_SESSION_KEY = '_language'

# ... (Phần switch_language và DynamicLanguageMenuItem giữ nguyên) ...
def switch_language(request, lang_code):
    db_langs = list(SystemLanguage.objects.filter(is_active=True).values_list('code', flat=True))
    valid_codes = list(set(db_langs + ['vi', 'en'])) 
    if lang_code not in valid_codes:
        found = False
        for db_code in valid_codes:
            if lang_code.startswith(db_code):
                lang_code = db_code
                found = True
                break
        if not found: lang_code = 'vi'
    translation.activate(lang_code)
    request.session[LANGUAGE_SESSION_KEY] = lang_code
    if request.user.is_authenticated:
        profile = UserProfile.get_for_user(request.user)
        profile.preferred_language = lang_code
        profile.save()
    return redirect(request.META.get('HTTP_REFERER', '/admin/'))

@hooks.register('register_admin_urls')
def register_core_urls():
    return [path('core/lang/<str:lang_code>/', switch_language, name='core_switch_language')]

class DynamicLanguageMenuItem(MenuItem):
    def __init__(self, code, label, flag, order):
        self.lang_code = code
        url = reverse('core_switch_language', args=[code])
        display_label = f"{flag} {label}"
        super().__init__(display_label, url, name=f'language_{code}', icon_name='site', order=order)
    def is_shown(self, request):
        current = get_language()
        return not current.startswith(self.lang_code)

@hooks.register('construct_main_menu')
def add_language_menu_items(request, menu_items):
    try: languages = SystemLanguage.objects.filter(is_active=True).order_by('-is_core', 'code')
    except: return
    if not languages.exists(): return
    order_counter = 99999
    for lang in languages:
        menu_items.append(DynamicLanguageMenuItem(code=lang.code, label=lang.name, flag=lang.flag, order=order_counter))
        order_counter += 1

# --- VIEWSETS ---

class SystemLanguageViewSet(SnippetViewSet):
    model = SystemLanguage
    icon = 'site'
    menu_label = 'Cấu hình Ngôn ngữ'
    menu_name = 'system_languages'
    list_display = ['flag', 'name', 'code', 'is_active', 'is_core']
    add_to_admin_menu = False

class AIPromptViewSet(SnippetViewSet): # MỚI
    model = AIPrompt
    icon = 'code'
    menu_label = 'Cấu hình AI Prompt'
    menu_name = 'ai_prompts'
    list_display = ['name', 'prompt_type', 'scope', 'target_app', 'is_active']
    list_filter = ['prompt_type', 'scope', 'target_app']
    search_fields = ['name', 'content']
    add_to_admin_menu = False

class SystemLabelViewSet(SnippetViewSet):
    model = SystemLabel
    icon = 'globe'
    menu_label = 'Nhãn giao diện'
    menu_name = 'system_labels'
    list_display = ['key', 'text_vi', 'text_en', 'app']
    list_filter = ['app']
    search_fields = ['key', 'text_vi', 'text_en']
    ordering = ['app', 'key']
    add_to_admin_menu = False

class CoreGroup(SnippetViewSetGroup):
    menu_label = 'Hệ thống (Core)'
    menu_icon = 'cogs'
    menu_order = 900
    items = (SystemLanguageViewSet, AIPromptViewSet, SystemLabelViewSet) # Thêm AIPrompt vào Group

register_snippet(CoreGroup)