import json
import requests
from django.conf import settings
from django.utils.translation import gettext_lazy as _

def get_best_prompt(prompt_type, app_name=None):
    from core.models import AIPrompt
    if app_name:
        prompt = AIPrompt.objects.filter(prompt_type=prompt_type, scope='app', target_app=app_name, is_active=True).first()
        if prompt: return prompt.content
    prompt = AIPrompt.objects.filter(prompt_type=prompt_type, scope='system', is_active=True).first()
    if prompt: return prompt.content
    
    # CẬP NHẬT PROMPT: Thêm ràng buộc Output chặt chẽ hơn cho SEA languages
    default_prompts = {
        'translate_to_en': (
            "Role: Technical Translator specializing in Thermal Power Plants.\n"
            "Task: Translate the term '{text}' from {source_lang} to English.\n"
            "Constraint: Return ONLY the translated term. No explanations. No labels like 'Translation:'.\n"
            "Example Input: 'Lò hơi'\n"
            "Example Output: Boiler"
        ),
        'translate_from_en': (
            "Role: Technical Translator specializing in Thermal Power Plants.\n"
            "Task: Translate the term '{text}' from English to {target_lang}.\n"
            "Context: Power plant equipment, SCADA, industrial automation.\n"
            "Constraint: Return ONLY the translated term in the target language script. No English text. No explanations.\n"
            "Example Input (to Filipino): 'Boiler'\n"
            "Example Output: Pakuluan"
        ),
        'pinyin_converter': (
            "Role: Linguist.\n"
            "Task: Convert the Chinese term '{text}' to Pinyin with tone marks.\n"
            "Constraint: Return ONLY the Pinyin. No original text.\n"
            "Example Input: '超临界锅炉'\n"
            "Example Output: Chāolínjiè guōlú"
        ),
        'generate_desc': (
            "Role: Technical Writer for Industrial Automation.\n"
            "Task: Write a concise technical description (1-2 sentences) for the parameter: '{text}'.\n"
            "Constraint: Return ONLY the English description. Be professional and precise."
        ),
    }
    return default_prompts.get(prompt_type, "")

def call_gemini_api(prompt_text):
    api_key = getattr(settings, 'GEMINI_API_KEY', '')
    if not api_key: return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            text = response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
            
            # --- POST-PROCESSING (Hậu xử lý để làm sạch kết quả) ---
            # 1. Loại bỏ các tiền tố phổ biến
            prefixes_to_remove = [
                "Translation:", "Translated text:", "Output:", "Result:", 
                "Chinese:", "Vietnamese:", "English:", "Pinyin:", "Filipino:", "Tagalog:"
            ]
            for prefix in prefixes_to_remove:
                if text.lower().startswith(prefix.lower()):
                    text = text[len(prefix):].strip()
            
            # 2. Loại bỏ dấu ngoặc kép
            if text.startswith('"') and text.endswith('"'):
                text = text[1:-1].strip()
                
            # 3. Loại bỏ tiếng Anh còn sót lại (chỉ lấy phần sau dấu hai chấm nếu có)
            if ':' in text:
                parts = text.split(':')
                text = parts[-1].strip()

            return text
    except Exception: pass
    return None

def _translate_field_logic(instance, field_prefix, app_label, check_active_only=True):
    from core.models import SystemLanguage
    
    f_vi = f"{field_prefix}_vi"
    f_zh = f"{field_prefix}_zh"
    f_en = f"{field_prefix}_en"
    
    val_vi = getattr(instance, f_vi, '') if hasattr(instance, f_vi) else ''
    val_zh = getattr(instance, f_zh, '') if hasattr(instance, f_zh) else ''
    val_en = getattr(instance, f_en, '') if hasattr(instance, f_en) else ''

    # --- BƯỚC 1: CHUẨN HÓA SANG TIẾNG ANH ---
    if not val_en and hasattr(instance, f_en):
        source_text = val_vi or val_zh
        source_lang = "Vietnamese" if val_vi else "Chinese"
        if source_text:
            tmpl = get_best_prompt('translate_to_en', app_label)
            prompt = tmpl.format(source_lang=source_lang, text=source_text)
            res = call_gemini_api(prompt)
            if res:
                setattr(instance, f_en, res)
                val_en = res

    # --- BƯỚC 2: DỊCH TỪ ANH SANG NGÔN NGỮ KHÁC ---
    if val_en:
        # A. Dịch ngược về VI
        if not val_vi and hasattr(instance, f_vi):
            tmpl = get_best_prompt('translate_from_en', app_label)
            prompt = tmpl.format(target_lang="Vietnamese", text=val_en)
            res = call_gemini_api(prompt)
            if res: setattr(instance, f_vi, res)

        # B. Dịch sang ngôn ngữ khác
        lang_query = SystemLanguage.objects.exclude(code__in=['vi', 'en'])
        if check_active_only:
            lang_query = lang_query.filter(is_active=True)
        langs = list(lang_query.values('code', 'name'))

        for lang in langs:
            code = lang['code']
            lang_name = lang['name']
            target_field = f"{field_prefix}_{code}"
            
            if hasattr(instance, target_field) and not getattr(instance, target_field):
                # Mapping tên ngôn ngữ rõ ràng hơn cho AI
                prompt_lang_name = lang_name
                if code == 'zh': prompt_lang_name = 'Simplified Chinese (Hanzi only)'
                if code == 'fil': prompt_lang_name = 'Filipino (Tagalog)' # Cụ thể hóa cho Filipino
                
                tmpl = get_best_prompt('translate_from_en', app_label)
                prompt = tmpl.format(target_lang=prompt_lang_name, text=val_en)
                translated_text = call_gemini_api(prompt)
                
                if translated_text:
                    setattr(instance, target_field, translated_text)

                    # C. Pinyin cho Tiếng Trung
                    if code == 'zh':
                        pinyin_field = f"{field_prefix}_zh_pinyin"
                        if hasattr(instance, pinyin_field) and not getattr(instance, pinyin_field):
                            pinyin_tmpl = get_best_prompt('pinyin_converter', app_label)
                            if not pinyin_tmpl: 
                                pinyin_tmpl = "Role: Linguist. Task: Convert '{text}' to Pinyin. Constraint: Return ONLY Pinyin."
                            
                            pinyin_res = call_gemini_api(pinyin_tmpl.format(text=translated_text))
                            if pinyin_res:
                                setattr(instance, pinyin_field, pinyin_res)


def auto_generate_description_logic(instance, source_field='name', target_field='description'):
    """
    Tự động sinh mô tả nếu cả VI và EN đều trống.
    Logic: Dùng Tên (EN hoặc VI) -> Sinh Mô tả (EN) -> Dịch Mô tả (EN) sang các tiếng khác.
    """
    f_desc_vi = f"{target_field}_vi"
    f_desc_en = f"{target_field}_en"
    
    val_desc_vi = getattr(instance, f_desc_vi, '')
    val_desc_en = getattr(instance, f_desc_en, '')
    
    # CHỈ CHẠY KHI CẢ VI VÀ EN ĐỀU TRỐNG
    if not val_desc_vi and not val_desc_en:
        # Lấy nguồn từ tên (đã được dịch chuẩn hóa ở bước trước đó)
        f_name_en = f"{source_field}_en"
        f_name_vi = f"{source_field}_vi"
        
        name_source = getattr(instance, f_name_en, '') or getattr(instance, f_name_vi, '')
        
        if name_source:
            app_label = instance._meta.app_label
            # 1. Sinh mô tả tiếng Anh
            tmpl = get_best_prompt('generate_desc', app_label)
            prompt = tmpl.format(text=name_source)
            
            generated_desc = call_gemini_api(prompt)
            
            if generated_desc:
                # Gán vào field tiếng Anh
                setattr(instance, f_desc_en, generated_desc)
                
                # Sau khi sinh xong tiếng Anh, gọi hàm dịch để lan ra các ngôn ngữ khác (bao gồm cả VI)
                _translate_field_logic(instance, target_field, app_label, check_active_only=True)

def auto_translate_label(label_instance):
    # SystemLabel luôn dịch hết để sẵn sàng
    _translate_field_logic(label_instance, 'text', label_instance.app, check_active_only=False)
    return label_instance

def auto_translate_model(instance, fields=[]):
    # App khác chỉ dịch ngôn ngữ active
    app_label = instance._meta.app_label
    for field_prefix in fields:
        _translate_field_logic(instance, field_prefix, app_label, check_active_only=True)
    return instance