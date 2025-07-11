from openpyxl import Workbook
import locale
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
def change_numeric_format(wb: Workbook, sheet_name: str):
    """
    Добавляет титульный лист в существующий Excel файл
    """
    
    ws = wb[sheet_name]    
    # Настройка ширины столбцов
    for col in ws['C:I']:
        for cell in col:
            # Убедитесь, что значение — число (если оно строка, конвертируем)
            if isinstance(cell.value, str):
                try:
                    cell.value = float(cell.value.replace(',', '.').replace(' ', ''))  # Преобразуем строку в число
                except (ValueError, TypeError):
                    pass  # Пропускаем, если не удаётся преобразовать
            cell.number_format = '#,##0.00'  # Русский формат: 21 000,12