"""
Модуль валидации данных для KARI Dashboard
Проверяет структуру и корректность данных из Excel файлов
"""

import pandas as pd
from typing import List, Dict, Optional, Tuple
from logging_config import get_logger

logger = get_logger('data_validator')


class ValidationResult:
    """Результат валидации данных"""
    
    def __init__(self, is_valid: bool, errors: List[str] = None, warnings: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
    
    def __bool__(self):
        return self.is_valid
    
    def log_results(self, context: str):
        """Логирование результатов валидации"""
        if self.is_valid:
            logger.info(f"✅ Валидация пройдена: {context}")
        else:
            logger.error(f"❌ Валидация провалена: {context}")
        
        for error in self.errors:
            logger.error(f"  - {error}")
        
        for warning in self.warnings:
            logger.warning(f"  - {warning}")


class DataValidator:
    """Валидатор данных Excel файлов"""
    
    # Схемы данных для разных типов файлов
    REGIONS_SCHEMA = {
        'required_columns': ['регион', 'продаж'],  # Ключевые слова в названиях колонок
        'min_rows': 5,  # Минимум регионов
        'max_rows': 20  # Максимум регионов
    }
    
    TURNOVER_SCHEMA = {
        'required_columns': ['группа', 'оборач'],  # Ключевые слова
        'min_rows': 10,  # Минимум категорий
        'max_rows': 500  # Максимум категорий
    }
    
    ACCESSORIES_SCHEMA = {
        'required_columns': ['магазин', 'продаж'],
        'min_rows': 50,  # Минимум магазинов
        'max_rows': 200
    }
    
    @staticmethod
    def validate_dataframe(
        df: pd.DataFrame,
        schema: Dict,
        data_name: str
    ) -> ValidationResult:
        """
        Базовая валидация DataFrame
        
        Args:
            df: DataFrame для проверки
            schema: Схема валидации
            data_name: Название данных для логов
            
        Returns:
            ValidationResult: Результат валидации
        """
        errors = []
        warnings = []
        
        # Проверка что DataFrame не None
        if df is None:
            errors.append(f"{data_name}: DataFrame is None")
            return ValidationResult(False, errors, warnings)
        
        # Проверка что DataFrame не пустой
        if df.empty:
            errors.append(f"{data_name}: DataFrame пустой (0 строк)")
            return ValidationResult(False, errors, warnings)
        
        # Проверка количества строк
        row_count = len(df)
        min_rows = schema.get('min_rows', 1)
        max_rows = schema.get('max_rows', 10000)
        
        if row_count < min_rows:
            errors.append(
                f"{data_name}: недостаточно строк ({row_count} < {min_rows})"
            )
        elif row_count > max_rows:
            warnings.append(
                f"{data_name}: подозрительно много строк ({row_count} > {max_rows})"
            )
        
        # Проверка наличия обязательных колонок (по ключевым словам)
        required_keywords = schema.get('required_columns', [])
        columns_str = ' '.join([str(col).lower() for col in df.columns])
        
        missing_keywords = []
        for keyword in required_keywords:
            if keyword.lower() not in columns_str:
                missing_keywords.append(keyword)
        
        if missing_keywords:
            errors.append(
                f"{data_name}: не найдены колонки с ключевыми словами: {missing_keywords}"
            )
            errors.append(
                f"Доступные колонки: {list(df.columns)[:10]}"  # Первые 10
            )
        
        # Проверка на полностью пустые колонки
        empty_columns = []
        for col in df.columns:
            if df[col].isna().all():
                empty_columns.append(str(col))
        
        if empty_columns:
            warnings.append(
                f"{data_name}: найдены пустые колонки: {empty_columns[:5]}"
            )
        
        # Проверка на дубликаты строк
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            warnings.append(
                f"{data_name}: найдено {duplicates} дубликатов строк"
            )
        
        is_valid = len(errors) == 0
        
        logger.debug(
            f"Валидация {data_name}",
            extra={'extra_data': {
                'rows': row_count,
                'columns': len(df.columns),
                'errors': len(errors),
                'warnings': len(warnings),
                'is_valid': is_valid
            }}
        )
        
        return ValidationResult(is_valid, errors, warnings)
    
    @staticmethod
    def validate_regions_data(df: pd.DataFrame) -> ValidationResult:
        """
        Валидация данных по регионам
        
        Args:
            df: DataFrame с данными по регионам
            
        Returns:
            ValidationResult: Результат валидации
        """
        result = DataValidator.validate_dataframe(
            df,
            DataValidator.REGIONS_SCHEMA,
            "Данные по регионам"
        )
        
        # Дополнительные проверки для регионов
        if result.is_valid and df is not None:
            # Проверяем наличие региона ННВ
            nnv_found = False
            for idx, row in df.iterrows():
                row_str = ' '.join([str(v).lower() for v in row.values if pd.notna(v)])
                if 'ннв' in row_str or 'нижний' in row_str:
                    nnv_found = True
                    break
            
            if not nnv_found:
                result.warnings.append(
                    "Не найден регион ННВ в данных"
                )
        
        result.log_results("Регионы")
        return result
    
    @staticmethod
    def validate_turnover_data(df: pd.DataFrame) -> ValidationResult:
        """
        Валидация данных оборачиваемости
        
        Args:
            df: DataFrame с данными оборачиваемости
            
        Returns:
            ValidationResult: Результат валидации
        """
        result = DataValidator.validate_dataframe(
            df,
            DataValidator.TURNOVER_SCHEMA,
            "Данные оборачиваемости"
        )
        
        # Дополнительные проверки для оборачиваемости
        if result.is_valid and df is not None:
            # Ищем колонку с оборачиваемостью
            turnover_col = None
            for col in df.columns:
                col_str = str(col).lower()
                if 'оборач' in col_str or 'недел' in col_str:
                    turnover_col = col
                    break
            
            if turnover_col:
                # Проверяем что есть числовые значения
                numeric_values = pd.to_numeric(df[turnover_col], errors='coerce')
                valid_count = numeric_values.notna().sum()
                
                if valid_count == 0:
                    result.errors.append(
                        f"Колонка оборачиваемости '{turnover_col}' не содержит числовых значений"
                    )
                    result.is_valid = False
                elif valid_count < len(df) * 0.5:
                    result.warnings.append(
                        f"Только {valid_count}/{len(df)} значений в колонке оборачиваемости"
                    )
            else:
                result.warnings.append(
                    "Не найдена колонка с оборачиваемостью"
                )
        
        result.log_results("Оборачиваемость")
        return result
    
    @staticmethod
    def validate_accessories_data(df: pd.DataFrame) -> ValidationResult:
        """
        Валидация данных по аксессуарам
        
        Args:
            df: DataFrame с данными по аксессуарам
            
        Returns:
            ValidationResult: Результат валидации
        """
        result = DataValidator.validate_dataframe(
            df,
            DataValidator.ACCESSORIES_SCHEMA,
            "Данные по аксессуарам"
        )
        
        # Дополнительные проверки для аксессуаров
        if result.is_valid and df is not None:
            # Проверяем наличие магазинов ННВ
            nnv_stores = df[df.apply(
                lambda r: any('ннв' in str(v).lower() for v in r.values if pd.notna(v)),
                axis=1
            )]
            
            if len(nnv_stores) == 0:
                result.warnings.append(
                    "Не найдены магазины ННВ в данных по аксессуарам"
                )
            elif len(nnv_stores) < 50:
                result.warnings.append(
                    f"Мало магазинов ННВ: {len(nnv_stores)} (ожидается ~119)"
                )
        
        result.log_results("Аксессуары")
        return result
    
    @staticmethod
    def validate_numeric_column(
        df: pd.DataFrame,
        column_name: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        allow_negative: bool = False
    ) -> ValidationResult:
        """
        Валидация числовой колонки
        
        Args:
            df: DataFrame
            column_name: Название колонки
            min_value: Минимальное допустимое значение
            max_value: Максимальное допустимое значение
            allow_negative: Разрешены ли отрицательные значения
            
        Returns:
            ValidationResult: Результат валидации
        """
        errors = []
        warnings = []
        
        if column_name not in df.columns:
            errors.append(f"Колонка '{column_name}' не найдена")
            return ValidationResult(False, errors, warnings)
        
        # Конвертируем в числа
        numeric_values = pd.to_numeric(df[column_name], errors='coerce')
        
        # Проверка на NaN
        nan_count = numeric_values.isna().sum()
        if nan_count > 0:
            warnings.append(
                f"Колонка '{column_name}': {nan_count} нечисловых значений"
            )
        
        valid_values = numeric_values.dropna()
        
        if len(valid_values) == 0:
            errors.append(f"Колонка '{column_name}' не содержит числовых значений")
            return ValidationResult(False, errors, warnings)
        
        # Проверка диапазона
        if not allow_negative and (valid_values < 0).any():
            negative_count = (valid_values < 0).sum()
            warnings.append(
                f"Колонка '{column_name}': найдено {negative_count} отрицательных значений"
            )
        
        if min_value is not None:
            below_min = (valid_values < min_value).sum()
            if below_min > 0:
                warnings.append(
                    f"Колонка '{column_name}': {below_min} значений < {min_value}"
                )
        
        if max_value is not None:
            above_max = (valid_values > max_value).sum()
            if above_max > 0:
                warnings.append(
                    f"Колонка '{column_name}': {above_max} значений > {max_value}"
                )
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings)


# Функции для быстрой валидации
def quick_validate_regions(df: pd.DataFrame) -> bool:
    """Быстрая валидация данных регионов (только критичные ошибки)"""
    result = DataValidator.validate_regions_data(df)
    return result.is_valid


def quick_validate_turnover(df: pd.DataFrame) -> bool:
    """Быстрая валидация данных оборачиваемости"""
    result = DataValidator.validate_turnover_data(df)
    return result.is_valid


def quick_validate_accessories(df: pd.DataFrame) -> bool:
    """Быстрая валидация данных аксессуаров"""
    result = DataValidator.validate_accessories_data(df)
    return result.is_valid


# Пример использования
if __name__ == '__main__':
    print("=== Тест валидации данных ===\n")
    
    # Тест 1: Пустой DataFrame
    print("Тест 1: Пустой DataFrame")
    empty_df = pd.DataFrame()
    result = DataValidator.validate_regions_data(empty_df)
    print(f"Результат: {'✅ VALID' if result.is_valid else '❌ INVALID'}")
    print(f"Ошибки: {result.errors}\n")
    
    # Тест 2: DataFrame с правильной структурой
    print("Тест 2: Корректные данные")
    good_df = pd.DataFrame({
        'Регион': ['МСК', 'СПБ', 'ННВ'],
        'Продажи': [1000, 800, 600],
        'Рост': [-10, -5, -8]
    })
    result = DataValidator.validate_regions_data(good_df)
    print(f"Результат: {'✅ VALID' if result.is_valid else '❌ INVALID'}")
    print(f"Предупреждения: {result.warnings}\n")
    
    # Тест 3: DataFrame с отсутствующими колонками
    print("Тест 3: Отсутствуют обязательные колонки")
    bad_df = pd.DataFrame({
        'Column1': [1, 2, 3],
        'Column2': [4, 5, 6]
    })
    result = DataValidator.validate_regions_data(bad_df)
    print(f"Результат: {'✅ VALID' if result.is_valid else '❌ INVALID'}")
    print(f"Ошибки: {result.errors}\n")
    
    print("Тесты завершены!")
