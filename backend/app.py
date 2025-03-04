import gradio as gr
from samle import process_file, scan_excel
from comis import comiss
from inn import filter_by_inn, filter_by_sample
from filter import filting

# Создаем интерфейс с использованием Gradio Blocks и вкладок
with gr.Blocks() as app:
    gr.Markdown("# Excel Processor")

    with gr.Tabs():
        # Первая вкладка с процессингом Excel файла
        with gr.TabItem("Метод систематической выборки (по шагам)"):
            gr.Markdown("## Метка 1")
            with gr.Row():
                file_input = gr.File(
                    label="Загрузите Excel файл (.xlsx)", file_types=[".xlsx"]
                )
                sheet_input = gr.Textbox(label="Название листа", value="455")
            with gr.Row():
                scan_button = gr.Button("Сканировать Excel файл")
                start_input = gr.Number(
                    label="Начать со строчки номер", value=1, precision=0
                )
                rows = gr.Textbox(label="Высота, строчек", interactive=False)
            with gr.Row():
                green_input = gr.Number(
                    label="Интервал в GREEN?", value=10, precision=0
                )
                yellow_input = gr.Number(
                    label="Интервал в YELLOW?", value=10, precision=0
                )
            process_button = gr.Button("Запустить процесс")
            download_output = gr.File(label="Скачать обработанный файл")
            output_text = gr.Textbox(label="Лог выполнения", interactive=False)

            scan_button.click(
                scan_excel,
                inputs=[file_input, sheet_input],
                outputs=[start_input, rows],
            )
            process_button.click(
                process_file,
                inputs=[
                    file_input,
                    sheet_input,
                    start_input,
                    green_input,
                    yellow_input,
                ],
                outputs=[download_output, output_text],
            )

        with gr.TabItem("комиссионки"):
            gr.Markdown("""
## Какие столбцы должны быть

```python
    "входящий актив" # актив - расход
    "входящий пассив" # пассив - доход
    "исходящий актив" 
    "исходящий пассив"
    "Лицевой счет" # С большой буквы, без лишних пробелов
```
Остальные не принципиальны

Не должно быть никакой шапки, никаких данных за пределами прямоугольника

Просьма избегать сумм и прочих выводов внизу.
                        """)

            with gr.Row():
                file_input = gr.File(
                    label="Загрузите Excel файл (.xlsx)", file_types=[".xlsx"]
                )
                sheet_input = gr.Textbox(label="Название листа", value="Лист1")
            with gr.Row():
                type_value = gr.Radio(
                    ["Доход", "Расход"], label="Выберите тип", value="Расход"
                )
                timevalue = gr.Radio(
                    ["Первый", "Не первый"], label="Этап", value="Первый"
                )
                target_value = gr.Number(
                    label="Сколько процентов от суммы нужно?", value=40, precision=0
                )
            process_button = gr.Button("Запустить процесс")
            download_output = gr.File(label="Скачать обработанный файл")
            log_percentage = gr.Textbox(label="Результаты", interactive=False)

            process_button.click(
                comiss,
                inputs=[file_input, sheet_input, type_value, target_value, timevalue],
                outputs=[download_output, log_percentage],
            )

        with gr.TabItem("фильтрация по ИНН"):
            gr.Markdown("## Метка 3")

            with gr.Row():
                file_input = gr.File(
                    label="Загрузите Excel файл (.xlsx)", file_types=[".xlsx"]
                )
                process_button = gr.Button("Запустить процесс")
                download_output = gr.File(label="Скачать обработанный файл")
                dataframe = gr.Dataframe(type="polars")
            with gr.Row():
                sample_number = gr.Number(
                    label="Какой интервал выборки?", value=10, precision=0
                )
                download_filtered = gr.File(label="Скачать отфильтрованный по шагам")
                process_filter_button = gr.Button("Отфильтровать")

            process_button.click(
                filter_by_inn,
                inputs=[
                    file_input,
                ],
                outputs=[dataframe, download_output],
            )
            process_filter_button.click(
                filter_by_sample,
                inputs=[file_input, sample_number],
                outputs=[download_filtered],
            )
        with gr.TabItem("фильтрация"):
            gr.Markdown("""
            ## Фильтрация по балансовому счету
            Столбец должен называться `Лицевой счет`""")
            with gr.Row():
                file_input = gr.File(
                    label="Загрузите Excel файл (.xlsx)", file_types=[".xlsx"]
                )
                column_number = gr.Number(label="Цифры начала", value=706, precision=0)
                sheet_input = gr.Textbox(label="Название листа", value="Лист1")
                target_value = gr.Number(
                    label="Сколько процентов от суммы нужно?", value=40, precision=0
                )

            process_button = gr.Button("Запустить процесс")
            download_output = gr.File(label="Скачать обработанный файл")

            process_button.click(
                filting,
                inputs=[file_input, sheet_input, column_number, target_value],
                outputs=[download_output],
            )

            pass

if __name__ == "__main__":
    app.launch(inbrowser=True)
