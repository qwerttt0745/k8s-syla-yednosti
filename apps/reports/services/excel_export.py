from openpyxl import Workbook


def build_workbook(purchases):
    wb = Workbook()
    ws = wb.active
    ws.title = "Report"

    ws.append(["Назва", "Сума", "Джерело", "Дата"])
    for purchase in purchases:
        ws.append(
            [
                purchase.title,
                float(purchase.amount),
                purchase.source,
                purchase.created_at.strftime("%Y-%m-%d %H:%M"),
            ]
        )

    return wb
