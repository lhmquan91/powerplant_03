import os
import re
from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import models
from django.utils.functional import Promise 
from core.models import SystemLabel

class Command(BaseCommand):
    help = "Quét Model, Template và Code Python để tự động tạo và dọn dẹp SystemLabel."

    def add_arguments(self, parser):
        parser.add_argument(
            '--apps', 
            nargs='+', 
            type=str, 
            default=['details', 'equipment', 'core'], 
            help='Danh sách các App cần quét'
        )
        parser.add_argument(
            '--update', 
            action='store_true', 
            help='Cập nhật lại text gốc từ code/template kể cả khi nhãn đã tồn tại'
        )
        parser.add_argument(
            '--clean', 
            action='store_true', 
            help='Xóa các nhãn trong DB không còn tồn tại trong code (Dọn dẹp rác)'
        )

    def handle(self, *args, **options):
        target_apps = options['apps']
        force_update = options['update']
        do_clean = options['clean']
        
        self.stdout.write(self.style.WARNING(f"🚀 BẮT ĐẦU QUÉT SYSTEM LABELS CHO APPS: {', '.join(target_apps)}\n"))

        valid_apps = []
        # scanned_keys: Lưu trữ tất cả các cặp (app, key) hợp lệ tìm thấy trong code
        scanned_keys = set() 
        
        # Thống kê
        stats = {'found': 0, 'created': 0, 'updated': 0, 'deleted': 0}

        for app_name in target_apps:
            try:
                app_config = apps.get_app_config(app_name)
                valid_apps.append(app_name)
            except LookupError:
                self.stdout.write(self.style.ERROR(f"❌ Không tìm thấy app: {app_name}"))
                continue

            app_path = app_config.path
            self.stdout.write(self.style.MIGRATE_HEADING(f"📦 Đang xử lý App: {app_name}"))

            # =========================================================
            # PHẦN 1: QUÉT MODEL (Introspection)
            # =========================================================
            # self.stdout.write(f"  > Quét Models...")
            for model in app_config.get_models():
                model_name = model.__name__.lower()
                
                # A. Meta (Tên Model)
                self._process_text_object(app_name, model._meta.verbose_name, f"model_{model_name}_name", f"Model: {model.__name__}", force_update, scanned_keys, stats)
                self._process_text_object(app_name, model._meta.verbose_name_plural, f"model_{model_name}_plural", f"Model Plural: {model.__name__}", force_update, scanned_keys, stats)

                # B. Fields (Label & Help Text)
                for field in model._meta.get_fields():
                    if not isinstance(field, (models.Field, models.ForeignKey, models.ManyToManyField)) or field.auto_created:
                        continue
                    
                    self._process_text_object(app_name, field.verbose_name, f"field_{field.name}_label", f"Field Label: {model.__name__}.{field.name}", force_update, scanned_keys, stats)
                    if field.help_text:
                        self._process_text_object(app_name, field.help_text, f"field_{field.name}_help", f"Field Help: {model.__name__}.{field.name}", force_update, scanned_keys, stats)

                # C. Standard View Titles
                # Chỉ tạo title cho model thuộc chính app đang quét để tránh trùng lặp
                if model._meta.app_label == app_name:
                    model_verbose = self._extract_lazy_text(model._meta.verbose_name) or model.__name__
                    view_patterns = [
                        ('index', 'Danh sách {name}'), ('create', 'Thêm mới {name}'),
                        ('edit', 'Cập nhật {name}'), ('delete', 'Xóa {name}'),
                        ('inspect', 'Chi tiết {name}'), ('usage', 'Sử dụng {name}'),
                        ('history', 'Lịch sử {name}'),
                    ]
                    for suffix, tmpl in view_patterns:
                        self._create_or_update_label(
                            app_name, 
                            f"view_{model_name}{suffix}_title", 
                            tmpl.format(name=model_verbose), 
                            f"View Title: {model.__name__} {suffix}", 
                            force_update, scanned_keys, stats
                        )

            # =========================================================
            # PHẦN 2: QUÉT FILE (Templates & Python)
            # =========================================================
            # self.stdout.write(f"  > Quét Files (HTML/Python)...")
            self._scan_directory(app_path, force_update, scanned_keys, stats)

        # =========================================================
        # PHẦN 3: DỌN DẸP (CLEANUP)
        # =========================================================
        if valid_apps and do_clean:
            self.stdout.write(self.style.WARNING(f"\n🧹 ĐANG DỌN DẸP LABEL THỪA..."))
            
            # Lấy tất cả label trong DB thuộc các app ĐANG QUÉT
            # Lưu ý: Nếu label thuộc app 'common' nhưng được dùng trong 'details', 
            # nó chỉ được giữ lại nếu ta quét cả 'common' hoặc nếu code 'details' có gọi nó.
            existing_labels = SystemLabel.objects.filter(app__in=valid_apps)
            
            for label in existing_labels:
                # Kiểm tra: (app, key) có nằm trong danh sách vừa quét được không?
                if (label.app, label.key) not in scanned_keys:
                    self.stdout.write(self.style.ERROR(f"   - [DELETE] [{label.app}] {label.key} (Không còn tìm thấy trong code)"))
                    label.delete()
                    stats['deleted'] += 1
            
            if stats['deleted'] == 0:
                self.stdout.write(self.style.SUCCESS("   ✓ Database sạch sẽ, không có label thừa."))

        # =========================================================
        # TỔNG KẾT
        # =========================================================
        self.stdout.write(self.style.SUCCESS(f"\n✅ HOÀN TẤT!"))
        self.stdout.write(f"   - Tìm thấy (Total Scanned): {stats['found']}")
        self.stdout.write(f"   - Tạo mới (Created): {stats['created']}")
        self.stdout.write(f"   - Cập nhật (Updated): {stats['updated']}")
        if do_clean:
            self.stdout.write(f"   - Đã xóa (Deleted): {stats['deleted']}")

    def _scan_directory(self, root_path, force_update, scanned_keys, stats):
        """
        Duyệt đệ quy thư mục để tìm Regex trong các file HTML và Python.
        """
        if not os.path.exists(root_path): return

        # Regex HTML: {% get_label 'app' 'key' 'default' %}
        regex_html = re.compile(r"\{%\s*get_label\s+(['\"])(.+?)\1\s+(['\"])(.+?)\3(?:\s+(['\"])(.*?)\5)?\s*%\}")
        
        # Regex Python: get_label_text('app', 'key', 'default') hoặc get_label_lazy
        regex_py = re.compile(r"get_label_(?:text|lazy)\s*\(\s*(['\"])(.+?)\1\s*,\s*(['\"])(.+?)\3\s*(?:,\s*(['\"])(.*?)\5)?")

        for root, _, files in os.walk(root_path):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Bỏ qua migrations và __init__
                if 'migrations' in root or file == '__init__.py': continue
                
                # Xác định loại file
                if file.endswith('.html'):
                    target_regex = regex_html
                elif file.endswith('.py'):
                    target_regex = regex_py
                else:
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        matches = target_regex.findall(content)
                        
                        for match in matches:
                            # 0: Quote App, 1: App, 2: Quote Key, 3: Key, 4: Quote Default, 5: Default
                            found_app = match[1]
                            found_key = match[3]
                            found_default = match[5] if len(match) > 5 else ""
                            
                            # Ghi chú nguồn gốc để dễ debug
                            relative_path = os.path.relpath(file_path, os.getcwd())
                            desc = f"Source: {relative_path}"
                            
                            self._create_or_update_label(found_app, found_key, found_default, desc, force_update, scanned_keys, stats)
                except Exception as e:
                    # self.stdout.write(self.style.ERROR(f"Lỗi đọc file {file}: {e}"))
                    pass

    def _process_text_object(self, default_app, text_obj, generated_key, description, force_update, scanned_keys, stats):
        """Xử lý object text từ Model"""
        target_app, target_key, target_text = default_app, generated_key, ""
        
        if isinstance(text_obj, Promise) and hasattr(text_obj, '_args') and len(text_obj._args) >= 3:
            target_app = text_obj._args[0]
            target_key = text_obj._args[1]
            target_text = text_obj._args[2]
        else:
            target_text = str(text_obj) if text_obj else ""

        if target_text:
            self._create_or_update_label(target_app, target_key, target_text, description, force_update, scanned_keys, stats)

    def _extract_lazy_text(self, text_obj):
        if isinstance(text_obj, Promise) and hasattr(text_obj, '_args') and len(text_obj._args) >= 3:
            return text_obj._args[2]
        return str(text_obj) if text_obj else ""

    def _create_or_update_label(self, app, key, text_vi, desc, force_update, scanned_keys, stats):
        # 1. Quan trọng: Ghi nhận key vào danh sách đã quét
        scanned_keys.add((app, key))
        stats['found'] += 1
        
        if not text_vi: return

        # 2. Tương tác DB
        obj, created = SystemLabel.objects.get_or_create(
            app=app, key=key,
            defaults={'text_vi': text_vi, 'description': desc}
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f"   + [NEW] {key}"))
            stats['created'] += 1
        elif force_update:
            if obj.text_vi != text_vi:
                obj.text_vi = text_vi
                obj.description = desc
                obj.save(update_fields=['text_vi', 'description'])
                self.stdout.write(self.style.WARNING(f"   ~ [UPD] {key}"))
                stats['updated'] += 1