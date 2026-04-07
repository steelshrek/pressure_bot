import pandas as pd
import matplotlib.pyplot as plt

def create_excel_report(records, filename="report.xlsx"):
    data = []
    for r in records:
        data.append({
            "Дата и время": r.timestamp.strftime("%Y-%m-%d %H:%M"),
            "Сис": r.sys,
            "Диа": r.dia,
            "Пульс": r.pul
        })

    df = pd.DataFrame(data)
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Замеры')
    return filename





def create_pressure_chart(records, filename="chart.png"):
    dates = [r.timestamp for r in records]
    sys_vals = [r.sys for r in records]
    dia_vals = [r.dia for r in records]

    plt.figure(figsize=(10, 6))
    plt.plot(dates, sys_vals, label="Систолическое", marker='o', color='red')
    plt.plot(dates, dia_vals, label="Диастолическое", marker='o', color='blue')

    # Линии нормы
    plt.axhline(y=120, color='red', linestyle='--', alpha=0.3, label="Норма СИС")
    plt.axhline(y=80, color='blue', linestyle='--', alpha=0.3, label="Норма ДИА")

    plt.title("Динамика артериального давления")
    plt.xlabel("Дата")
    plt.ylabel("мм рт. ст.")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(filename)
    plt.close()
    return filename