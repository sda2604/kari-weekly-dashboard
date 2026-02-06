#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт проверки docstrings в проекте KARI Dashboard
Находит функции/классы без docstrings или с неполными docstrings
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple


class DocstringChecker(ast.NodeVisitor):
    """Проверяет наличие и полноту docstrings"""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.issues = []
        self.stats = {
            'functions': 0,
            'with_docstring': 0,
            'with_full_docstring': 0,
            'classes': 0,
            'class_with_docstring': 0
        }
    
    def visit_FunctionDef(self, node):
        """Проверка функций"""
        self.stats['functions'] += 1
        
        # Игнорируем приватные функции и __init__
        if node.name.startswith('_') and node.name != '__init__':
            self.generic_visit(node)
            return
        
        docstring = ast.get_docstring(node)
        
        if not docstring:
            self.issues.append({
                'type': 'MISSING',
                'name': node.name,
                'line': node.lineno,
                'kind': 'function'
            })
        else:
            self.stats['with_docstring'] += 1
            
            # Проверяем полноту (Args, Returns если есть return)
            has_args = len(node.args.args) > 0
            has_return = any(isinstance(n, ast.Return) and n.value for n in ast.walk(node))
            
            doc_lower = docstring.lower()
            has_args_section = 'args:' in doc_lower or 'parameters:' in doc_lower
            has_returns_section = 'returns:' in doc_lower or 'return:' in doc_lower
            
            is_complete = True
            missing_sections = []
            
            if has_args and not has_args_section:
                is_complete = False
                missing_sections.append('Args')
            
            if has_return and not has_returns_section:
                is_complete = False
                missing_sections.append('Returns')
            
            if is_complete:
                self.stats['with_full_docstring'] += 1
            else:
                self.issues.append({
                    'type': 'INCOMPLETE',
                    'name': node.name,
                    'line': node.lineno,
                    'kind': 'function',
                    'missing': missing_sections
                })
        
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """Проверка классов"""
        self.stats['classes'] += 1
        
        docstring = ast.get_docstring(node)
        
        if not docstring:
            self.issues.append({
                'type': 'MISSING',
                'name': node.name,
                'line': node.lineno,
                'kind': 'class'
            })
        else:
            self.stats['class_with_docstring'] += 1
        
        self.generic_visit(node)


def check_file(filepath: Path) -> Tuple[dict, List[dict]]:
    """
    Проверяет файл на наличие docstrings
    
    Args:
        filepath: Путь к Python файлу
    
    Returns:
        Tuple с статистикой и списком проблем
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(filepath))
        
        checker = DocstringChecker(str(filepath))
        checker.visit(tree)
        
        return checker.stats, checker.issues
    
    except Exception as e:
        print(f"⚠️  Ошибка при проверке {filepath.name}: {e}")
        return {}, []


def main():
    """Главная функция"""
    print("=" * 70)
    print("ПРОВЕРКА DOCSTRINGS")
    print("=" * 70)
    print()
    
    # Файлы для проверки
    project_dir = Path(__file__).parent
    files_to_check = [
        'generate_dashboard.py',
        'error_handler.py',
        'data_validator.py',
        'logging_config.py',
        'telegram_bot/send_dashboard.py',
        'telegram_bot/period_parser.py',
    ]
    
    total_stats = {
        'functions': 0,
        'with_docstring': 0,
        'with_full_docstring': 0,
        'classes': 0,
        'class_with_docstring': 0
    }
    
    all_issues = []
    
    for file_path in files_to_check:
        filepath = project_dir / file_path
        if not filepath.exists():
            print(f"⏭️  Пропускаю: {file_path} (не найден)")
            continue
        
        print(f"📄 Проверяю: {file_path}")
        stats, issues = check_file(filepath)
        
        # Обновляем общую статистику
        for key in total_stats:
            total_stats[key] += stats.get(key, 0)
        
        # Выводим результаты
        if stats.get('functions', 0) > 0:
            coverage = (stats['with_docstring'] / stats['functions']) * 100
            full_coverage = (stats['with_full_docstring'] / stats['functions']) * 100
            print(f"  Функций: {stats['functions']}")
            print(f"  С docstring: {stats['with_docstring']} ({coverage:.0f}%)")
            print(f"  Полные docstrings: {stats['with_full_docstring']} ({full_coverage:.0f}%)")
        
        if issues:
            print(f"  ⚠️  Проблемы: {len(issues)}")
            for issue in issues:
                all_issues.append((file_path, issue))
        else:
            print(f"  ✅ Все docstrings в порядке!")
        
        print()
    
    # Итоговый отчёт
    print("=" * 70)
    print("ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 70)
    print(f"Всего функций: {total_stats['functions']}")
    print(f"С docstring: {total_stats['with_docstring']} ({(total_stats['with_docstring']/total_stats['functions']*100):.0f}%)")
    print(f"Полные docstrings: {total_stats['with_full_docstring']} ({(total_stats['with_full_docstring']/total_stats['functions']*100):.0f}%)")
    print()
    print(f"Всего классов: {total_stats['classes']}")
    print(f"С docstring: {total_stats['class_with_docstring']} ({(total_stats['class_with_docstring']/max(total_stats['classes'],1)*100):.0f}%)")
    print()
    
    # Детальный список проблем
    if all_issues:
        print("=" * 70)
        print("ДЕТАЛИ ПРОБЛЕМ")
        print("=" * 70)
        
        for file_path, issue in all_issues:
            icon = "❌" if issue['type'] == 'MISSING' else "⚠️"
            kind_ru = "Функция" if issue['kind'] == 'function' else "Класс"
            
            if issue['type'] == 'MISSING':
                print(f"{icon} {file_path}:{issue['line']} - {kind_ru} '{issue['name']}' БЕЗ docstring")
            else:
                missing = ', '.join(issue['missing'])
                print(f"{icon} {file_path}:{issue['line']} - {kind_ru} '{issue['name']}' - отсутствует: {missing}")
        
        print()
        print(f"❌ Найдено проблем: {len(all_issues)}")
        return 1
    else:
        print("✅ ВСЕ DOCSTRINGS В ПОРЯДКЕ!")
        return 0


if __name__ == '__main__':
    sys.exit(main())
