import gradio as gr
from samle import sample_process, scan_excel
from comis import comiss
from inn import filter_by_inn, filter_by_inn_split
from filter import filting
import polars as pl
from datetime import datetime

# Создаем интерфейс с использованием Gradio Blocks и вкладок
with gr.Blocks() as app:
    dt_now = datetime.now()

    gr.HTML("""<h1 style="color: darkgreen;">ООО КНК</h1>""")
    bank_name = gr.Textbox(label="Название аудироемого лица", value="Авангард")
    date_value_start = gr.Textbox(
        label="Период проверки, начало",
        value=datetime(dt_now.year, 1, 1).strftime("%d-%m-%Y"),
    )
    date_value_end = gr.Textbox(
        label="Период проверки, конец", value=dt_now.strftime("%d-%m-%Y")
    )
    boss_name = gr.Textbox(
        label="Руководитель проверки", value="Ельхимова Татьяна Викторовна"
    )
    with gr.Tabs():
        with gr.TabItem("Балансовый счет"):
            gr.Markdown("## Фильтрация по балансовому счету")
            with gr.Row():
                file_input = gr.File(
                    label="Загрузите Excel файл (.xlsx)", file_types=[".xlsx"]
                )
                column_number = gr.Number(label="Цифры начала", value=706, precision=0)
                sheet_input = gr.Textbox(label="Название листа", value="Приложение_ОСВ")
                target_value = gr.Number(
                    label="Сколько процентов от суммы нужно?", value=40, precision=0
                )

            process_button = gr.Button("Запустить процесс")
            download_output = gr.File(label="Скачать обработанный файл")

            process_button.click(
                filting,
                inputs=[
                    file_input,
                    sheet_input,
                    column_number,
                    target_value,
                    bank_name,
                    date_value_start,
                    date_value_end,
                    boss_name,
                ],
                outputs=[download_output],
            )

        with gr.TabItem("Метод систематической выборки (по шагам)"):
            gr.Markdown("ОСВ")
            with gr.Row():
                file_input = gr.File(
                    label="Загрузите Excel файл (.xlsx)", file_types=[".xlsx"]
                )
                sheet_input = gr.Textbox(label="Название листа", value="706")
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
                sample_process,
                inputs=[
                    file_input,
                    sheet_input,
                    start_input,
                    green_input,
                    yellow_input,
                    bank_name,
                    date_value_start,
                    date_value_end,
                    boss_name,
                ],
                outputs=[output_text, download_output],
            )

        with gr.TabItem("706 по символам"):
            with gr.Row():
                file_input = gr.File(
                    label="Загрузите Excel файл (.xlsx)", file_types=[".xlsx"]
                )
                sheet_input = gr.Textbox(label="Название листа", value="Приложение_ОСВ")
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
                inputs=[
                    file_input,
                    sheet_input,
                    type_value,
                    target_value,
                    timevalue,
                    bank_name,
                    date_value_start,
                    date_value_end,
                    boss_name,
                ],
                outputs=[download_output, log_percentage],
            )

        with gr.TabItem("фильтрация по ИНН"):
            # gr.Markdown("## Метка 3")

            with gr.Row():
                file_input = gr.File(
                    label="Загрузите Excel файл (.xlsx)", file_types=[".xlsx"]
                )
                with gr.Column():
                    sheet_input = gr.Radio(label="Название листа", choices=['дебет', 'кредит'], value='дебет')
                    main_col_name = gr.Textbox(label="Название столбца", value="ИНН контрагента")
                    process_button = gr.Button("Запустить процесс")
                download_output = gr.File(label="Скачать обработанный файл")

            dataframe = gr.Dataframe(
                type='pandas',
                interactive=False,
                wrap=True,  # Оборачиваем текст
            )
            inn_list_show = gr.CheckboxGroup(label="Выбранные ИНН", interactive=True)

            with gr.Row():
                download_filtered = gr.File(label="Скачать выборку")
                process_filter_button = gr.Button("Выгрузить выборку по листам")

            def update_inn_list(df: pl.DataFrame, main_col_name: str):
                if df is not None and not df.is_empty():
                    # Предполагаем, что в df есть столбец с ИНН
                    inn_values = df[main_col_name].unique(maintain_order=True).to_list()
                    return gr.CheckboxGroup(choices=inn_values, value=None)
                return gr.CheckboxGroup(choices=[])

            process_button.click(
                fn=filter_by_inn,
                inputs=[
                    file_input,
                    bank_name,
                    date_value_start,
                    date_value_end,
                    boss_name,
                    sheet_input,
                    main_col_name,
                ],
                outputs=[dataframe, download_output, inn_list_show],
            ).then(fn=update_inn_list, inputs=[dataframe, main_col_name], outputs=[inn_list_show])

            # Фильтрация по шагам
            process_filter_button.click(
                filter_by_inn_split,
                inputs=[
                    file_input,
                    bank_name,
                    date_value_start,
                    date_value_end,
                    boss_name,
                    sheet_input,
                    main_col_name,
                    inn_list_show,
                ],
                outputs=[download_filtered],
            )
if __name__ == "__main__":
    app.launch(inbrowser=True)
