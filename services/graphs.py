import plotext as plt
from services import data_base
import re


def get_users_graph(start, end, not_include: list = None):
    users_data = data_base.get_users_by_date_range(start, end)
    dates = [str(row[0]) for row in users_data]
    values = [int(row[1]) for row in users_data]

    plt.plotsize(40, 20)
    plt.bar(dates, values)
    plt.title("Пользователи")

    output = plt.build()
    output = re.sub(r"\x1b\[[0-9;]*m", "", output)
    plt.clear_data()

    return output


def get_gens_graph(start, end, not_include: list = None):
    gens_data = data_base.get_gens_by_date_range(start, end)
    dates = [str(row[0]) for row in gens_data]
    values = [int(row[1]) for row in gens_data]

    plt.plotsize(40, 20)
    plt.bar(dates, values)
    plt.title("Генерации")

    output = plt.build()
    output = re.sub(r"\x1b\[[0-9;]*m", "", output)
    plt.clear_data()

    return output
