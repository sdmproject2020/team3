import io
import os
from google.protobuf.json_format import MessageToJson
import json
import pandas as pd
import numpy as np
import cv2
import matplotlib.pyplot as plt
#%matplotlib inline
#Google.cloudをimport
from google.cloud import vision
from google.cloud import translate_v2 as translate
from google.cloud.vision import types

def main():
    base_dir = r"/Users/tahara_so70/Desktop/Sample" #今回の作業用ディレクトリ
    pic=r"/sake.jpg" #対象となる画像
    tag_language = 'ja' #翻訳先言語

    #認証用に発行されたJSONキーの絶対パス
    credential_path = base_dir + r'/amplified-cache-277509-4b71fdd784b2.json'

    #サービスアカウントキーへのパスを通す
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

    en_label = get_label(base_dir, pic) #画像から要素検出 in English

    ja_label_unique = label_transaction(en_label, tag_language) #日本語に変換し、食材以外と重複を取り除く

    year = []
    for i in range(1998,2005):
        year.append(i)

    for text in ja_label_unique:
        print("・" + text + "を使う料理")
        for i in year:
            print(year[i-1998])
            ingredient = pd.read_csv(f"/Users/tahara_so70/Desktop/Sample/MDA/ingredient/ingredient{i}.csv", names=["ID", "ingredient"], usecols=[0,1])
            #ingredientから指定した素材の行だけ抽出する
            ingredient_in = ingredient[ingredient["ingredient"].isin([text])]
            recipe = pd.read_csv(f"/Users/tahara_so70/Desktop/Sample/MDA/recipe/recipe{i}.csv",names=["ID","title"],usecols=[0,2])
            df = pd.merge(ingredient_in, recipe, on = "ID", how = "left")
            #欠損地を補完
            df["title"] = df["title"].fillna("no-data")
            sug = df.drop('ID', axis=1)
            sug = sug.drop('ingredient', axis=1)
            if sug.empty:
                print("該当レシピは存在しません")
            else:
                print(sug.head(3))
            print("\n")

#画像からラベルを検出する関数
def get_label(base_dir, pic):
    #対象となる画像の絶対パス
    file_name = base_dir + pic

    #画像を読み込み
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()
        image = types.Image(content=content)

    #画像を表示
    img = cv2.imread(file_name)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    plt.imshow(img)

    #visionクライアントの初期化
    client = vision.ImageAnnotatorClient()

    #ラベル検出
    response = client.label_detection(image=image)
    labels = response.label_annotations

    #検出したラベルを格納するリスト
    en_label = []

    #リストに結果を格納
    for label in labels:
        en_label.append(label.description)

    #結果を表示
    print("検出した要素(in English)は以下")
    print(en_label)
    print( "\n")

    return en_label

#翻訳関数
def translate_lan(text, tag_language):
    #翻訳先が英語ならそのまま返す
    if tag_language == 'en':
        return text
    translate_client = translate.Client()
    result = translate_client.translate(text, target_language=tag_language)
    return result['translatedText']

#ラベルを取り扱いやすくする関数
def label_transaction(en_label, tag_language):
    ja_label = []
    for text in en_label:
        transtext = translate_lan(text, tag_language)
        ja_label.append(transtext)
    print("ラベルの日本語標記は以下")
    print(ja_label)
    print("\n")

    #よく検出される食材名以外のものを削除する
    exception = ['皿', '調理済み', '食物', '成分', 'ボトル']
    for text in exception:
        #NaNのときのエラー回避
        try:
            ja_label.remove(text)
        except ValueError:
            pass

    ja_label_unique = list(set(ja_label))  #重複を削除
    print("処理後は以下")
    print(ja_label_unique)
    print("\n")

    return ja_label_unique

#なぜか回らないので一旦main()を直で呼び出す
'''
if "__name__" == "__main__":
    main()
'''

main()
