import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


def create_excel_report(records, filename="report.xlsx"):
    ordered_records = sorted(records, key=lambda record: record.timestamp)
    data = []

    for record in ordered_records:
        data.append({
            "Дата і час": record.timestamp.strftime("%Y-%m-%d %H:%M"),
            "Систолічний тиск": record.sys,
            "Діастолічний тиск": record.dia,
            "Пульс": record.pul
        })

    df = pd.DataFrame(data)
    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Вимірювання")
    return filename


def create_pressure_chart(records, filename="chart.png"):
    ordered_records = sorted(records, key=lambda record: record.timestamp)
    dates = [record.timestamp for record in ordered_records]
    sys_vals = [record.sys for record in ordered_records]
    dia_vals = [record.dia for record in ordered_records]

    plt.figure(figsize=(10, 6))
    plt.plot(dates, sys_vals, label="Систолічний тиск", marker="o", color="#c2410c")
    plt.plot(dates, dia_vals, label="Діастолічний тиск", marker="o", color="#2563eb")

    plt.axhline(y=120, color="#c2410c", linestyle="--", alpha=0.3, label="Орієнтир 120")
    plt.axhline(y=80, color="#2563eb", linestyle="--", alpha=0.3, label="Орієнтир 80")

    plt.title("Динаміка тиску")
    plt.xlabel("Дата")
    plt.ylabel("мм рт. ст.")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(filename)
    plt.close()
    return filename
