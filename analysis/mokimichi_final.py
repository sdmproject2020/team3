import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

def main():
    """
    メインの処理。
    mokomichi()で欲しいデータを取得。
    show()で年ごとの特定の料理ごとにオリーブオイルが使われている割合を棒グラフで、全体を折れ線グラフで出す。
    """

    year = []
    for i in range(2000, 2015):
        year.append(i)

    bar = tqdm(total=45)

    qty, ratio, se = mokomichi(year, bar)
    show(year, qty, ratio, se)


def mokomichi(year, bar):
    """
    各年のオリーブオイルを使ったレシピの特定の料理別数(qty)、割合(ratio)、標準誤差(se)を求める
    配列の順番は["サラダ", "パスタ", "ドリア", "ピザ", "カルパッチョ"]
    """

    col_names_recipe = ["recipe_id", "name"]
    col_names_ingredient = ["recipe_id", "ingredient"]

    qty = []
    ratio = []
    se = []

    for i in year:
        # recipeファイルを読み込む
        recipe = pd.read_csv(f"/Users/tamuramasayuki/Desktop/3S/基礎プロジェクトB/programming/dataset/recipe/recipe{i}.csv",
                             names=col_names_recipe, usecols=[0, 2])
        recipe.dropna(inplace=True)

        bar.update(1)

        # 特定の料理を抽出する
        salad = recipe.query('name.str.contains("サラダ|さらだ")', engine="python")
        pasta = recipe.query('name.str.contains("パスタ|スパゲッティ｜スパゲティ|ペンネ|ペペロンチーノ|カルボナーラ|ボロネーゼ")', engine="python")
        doria = recipe.query('name.str.contains("ドリア|グラタン|リゾット")', engine="python")
        pizza = recipe.query('name.str.contains("ピザ|ピッザ|ピッツァ")', engine="python")
        carpaccio = recipe.query('name.str.contains("カルパッチョ|かるぱっちょ")', engine="python")

        # ingredientファイルを読み込む
        ingredient = pd.read_csv(f"/Users/tamuramasayuki/Desktop/3S/基礎プロジェクトB/programming/dataset/ingredient/ingredient{i}.csv",
                                 names=col_names_ingredient, usecols=[0, 1])
        bar.update(1)

        # ingredientからオリーブオイルの行だけ抽出する
        ingredient_olive = ingredient[ingredient["ingredient"].isin(["オリーブオイル", "オリーブ油", "おりーぶおいる"])]

        # オリーブオイルを使ったレシピだけで料理とingredientを結合
        salad = pd.merge(salad, ingredient_olive, on="recipe_id", how="left")
        pasta = pd.merge(pasta, ingredient_olive, on="recipe_id", how="left")
        doria = pd.merge(doria, ingredient_olive, on="recipe_id", how="left")
        pizza = pd.merge(pizza, ingredient_olive, on="recipe_id", how="left")
        carpaccio = pd.merge(carpaccio, ingredient_olive, on="recipe_id", how="left")

        temp_qty = [len(salad), len(pasta), len(doria), len(pizza), len(carpaccio)]

        olive_qty = [temp_qty[0] - salad["ingredient"].isnull().sum(), temp_qty[1] - pasta["ingredient"].isnull().sum(),
                     temp_qty[2] - doria["ingredient"].isnull().sum(), temp_qty[3] - pizza["ingredient"].isnull().sum(),
                     temp_qty[4] - carpaccio["ingredient"].isnull().sum()]

        temp_ratio = []
        temp_se = []
        for j in range(5):
            n = temp_qty[j]
            if n == 0:
                temp_ratio.append(0)
                temp_se.append(0)
            else:
                count = olive_qty[j]
                p = count / n
                temp_ratio.append(p)
                x = np.sqrt(p * (1-p) / n)
                temp_se.append(x)

        qty.append(temp_qty)
        ratio.append(temp_ratio)
        se.append(temp_se)

        bar.update(1)

    # 年ごとではなく料理ごとで見るために転置する
    qty = np.array(qty).T
    ratio = np.array(ratio).T
    se = np.array(se).T

    return qty, ratio, se

def show(year, qty, ratio, se):
    """
    各年のオリーブオイルを使った特定の料理別レシピの割合とその標準誤差を視覚化する。
    料理別で棒グラフで表す。全体を折れ線グラフで表す。
    """

    dish = ["salad", "pasta", "doria", "pizza", "carpaccio"]

    qty_adjusted = [[], [], [], [], []]
    for i in range(5):
        qty_adjusted[i] = [n / (max(qty[i]) / max(ratio[i])) for n in qty[i]]

    error_bar_set = dict(lw=1, capthick=1, capsize=3)
    fig = plt.figure(figsize=(14.0, 8.0))

    # 料理別
    for i in range(5):
        ax = fig.add_subplot(2, 3, i+1)
        ax.plot(year, qty_adjusted[i])
        ax.bar(year, ratio[i], color="lightgreen", tick_label=year, yerr=se[i], ecolor="black", error_kw=error_bar_set, width=0.65)
        ax.set_xticklabels(year, fontsize=7, rotation=60)
        ax.set_title(f"{dish[i]}")

    # 全体
    ax = fig.add_subplot(2, 3, 6)
    for i in range(5):
        ax.plot(year, ratio[i], label=dish[i])
    ax.set_xticks(year)
    ax.set_xticklabels(year, fontsize=7, rotation=60)
    ax.set_title("Overall")

    ax.legend()

    plt.savefig("mokomichi_final.png")
    plt.show()

if __name__ == '__main__':
    main()