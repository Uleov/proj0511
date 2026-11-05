import json
import os
import sys

def load_data(file_name):
    if not os.path.exists(file_name):
        print("Ошибка: файл не найден")
        return None
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        print("Ошибка: файл поврежден или не является JSON")
        return None

    if "stock" not in data or "recipes" not in data:
        print("Ошибка: в файле нет stock или recipes")
        return None

    stock = data["stock"]
    recipes = data["recipes"]

    if not isinstance(stock, dict) or not isinstance(recipes, list):
        print("Ошибка: неверный формат данных")
        return None

    if len(recipes) > 20:
        print("Ошибка: рецептов больше 20")
        return None

    for item, amount in stock.items():
        if not isinstance(amount, (int, float)) or amount < 0:
            print("Ошибка: количество на складе должно быть >= 0")
            return None

    for r in recipes:
        if not isinstance(r, dict):
            print("Ошибка: рецепт должен быть словарем")
            return None
        if "id" not in r or "name" not in r or "ingredients" not in r:
            print("Ошибка: у рецепта должны быть id, name и ingredients")
            return None
        if not isinstance(r["name"], str) or len(r["name"].strip()) == 0:
            print("Ошибка: пустое название рецепта")
            return None
        if not isinstance(r["ingredients"], dict):
            print("Ошибка: ингредиенты должны быть словарем")
            return None
        for ing, amount in r["ingredients"].items():
            if not isinstance(amount, (int, float)) or amount <= 0:
                print("Ошибка: количество ингредиента должно быть больше нуля")
                return None

    return data

def process_recipes(stock, recipes):
    result = []
    for r in recipes:
        missing = {}
        for ing, needed in r["ingredients"].items():
            have = stock.get(ing, 0)
            if needed > have:
                missing[ing] = needed - have
        item = {
            "id": r["id"],
            "name": r["name"],
            "missing": missing,
            "missing_count": len(missing)
        }
        result.append(item)

    def sort_key(x):
        return (x["missing_count"], x["name"])

    result.sort(key=sort_key)
    return result

def print_results(recipes, chosen):
    print("Доступные блюда:")
    available_found = False
    for r in recipes:
        if r["missing_count"] == 0:
            print(f"- {r['name']} (id {r['id']})")
            available_found = True
    if not available_found:
        print("Нет блюд, которые можно приготовить.")

    print()
    print("Все рецепты:")
    for r in recipes:
        if r["missing_count"] == 0:
            print(f"{r['name']} (id {r['id']}): можно готовить")
        else:
            print(f"{r['name']} (id {r['id']}): не хватает {r['missing_count']} продуктов")

    if chosen is not None:
        print()
        print(f"Список покупок для блюда {chosen['name']}:")
        if chosen["missing_count"] == 0:
            print("Все продукты есть, покупать ничего не надо.")
        else:
            for ing, count in chosen["missing"].items():
                print(f"{ing}: докупить {count}")

def save_results(recipes, chosen, output_file):
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("Доступные блюда:\n")
            available_found = False
            for r in recipes:
                if r["missing_count"] == 0:
                    f.write(f"- {r['name']} (id {r['id']})\n")
                    available_found = True
            if not available_found:
                f.write("Нет блюд, которые можно приготовить.\n")

            f.write("\nВсе рецепты:\n")
            for r in recipes:
                if r["missing_count"] == 0:
                    f.write(f"{r['name']} (id {r['id']}): можно готовить\n")
                else:
                    f.write(f"{r['name']} (id {r['id']}): не хватает {r['missing_count']} продуктов\n")

            if chosen is not None:
                f.write(f"\nСписок покупок для блюда {chosen['name']}:\n")
                if chosen["missing_count"] == 0:
                    f.write("Все продукты есть, покупать ничего не надо.\n")
                else:
                    for ing, count in chosen["missing"].items():
                        f.write(f"{ing}: докупить {count}\n")
        return True
    except:
        print("Ошибка: не удалось сохранить файл")
        return False

def main():
    file_name = "data.json"
    if len(sys.argv) > 1:
        file_name = sys.argv[1]

    data = load_data(file_name)
    if data is None:
        return

    stock = data["stock"]
    recipes = data["recipes"]

    processed = process_recipes(stock, recipes)

    chosen = None
    if len(processed) > 0:
        chosen_param = None
        if len(sys.argv) > 2:
            chosen_param = sys.argv[2]
        else:
            try:
                chosen_param = input("Введите ID или название рецепта для покупок (Enter для первого): ")
            except:
                chosen_param = ""

        if chosen_param and chosen_param.strip() != "":
            val = chosen_param.strip()
            for r in processed:
                if str(r["id"]) == val or r["name"].lower() == val.lower():
                    chosen = r
                    break
            if chosen is None:
                print("Рецепт не найден, выбран первый из списка.")
                chosen = processed[0]
        else:
            chosen = processed[0]

    print_results(processed, chosen)

    output_file = "result.txt"
    if save_results(processed, chosen, output_file):
        print()
        print(f"Результат сохранен в файл {output_file}")

if __name__ == "__main__":
    main()
