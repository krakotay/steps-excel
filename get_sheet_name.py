import zipfile
from lxml import etree

xlsx_path = "Шаблон53. РД Выборка_out (48).xlsx"
sheet_files = ["sheet135.xml", "sheet167.xml"]

with zipfile.ZipFile(xlsx_path) as zf:
    rels = etree.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    workbook = etree.fromstring(zf.read("xl/workbook.xml"))
    ns = {"r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}

    # target -> id
    target2id = {}
    print("Содержимое workbook.xml.rels:")
    for rel in rels.findall(".//{http://schemas.openxmlformats.org/package/2006/relationships}Relationship"):
        print(rel.attrib)
        target2id[rel.attrib['Target']] = rel.attrib['Id']

    print("\nСодержимое workbook.xml (sheets):")
    for sheet in workbook.findall(".//sheet", namespaces=ns):
        print(sheet.attrib)

    # теперь ищем соответствие
    for sf in sheet_files:
        # ищем прямое совпадение target
        rid = target2id.get(f"worksheets/{sf}") or target2id.get(sf)
        if not rid:
            print(f"{sf}: Не найдено в workbook.xml.rels")
            continue
        sheet = workbook.find(f".//sheet[@r:id='{rid}']", namespaces=ns)
        if sheet is not None:
            print(f"{sf}: {sheet.attrib['name']}")
        else:
            print(f"{sf}: rId {rid} не найден в workbook.xml")
