# 漢字プリント作成ツール
## 使い方
### プリント作成方法
![image](https://github.com/Masaya-Yamamoto-53/KanjiWorkSheet/assets/47249430/f19ecd03-d84c-4f97-9619-f50fecf568b6)
1. 初回は、生徒登録エントリーで生徒を登録する。  
   名前を入力して、登録ボタンを押すと登録できる。  
![image](https://user-images.githubusercontent.com/47249430/221411531-b247cb70-2b7f-45fa-acb3-f28b030a2742.png) 
2. 生徒登録後は、生徒を選択する。  
![image](https://user-images.githubusercontent.com/47249430/221411569-aa3cb55b-ca67-4152-ac86-069d23d5544b.png)  
3. 問題集を選択する。問題集の作成方法は後述する。  
![image](https://user-images.githubusercontent.com/47249430/221411695-56ce88e5-47eb-49ec-8a2e-aaa82b5e3e43.png)  
4. 出題範囲の選択をする（複数選択可）。  
![image](https://user-images.githubusercontent.com/47249430/221411729-b68db2c3-01f4-4dff-84a3-03f96788279b.png) 
5. 出題モードを選択する。  
![image](https://github.com/Masaya-Yamamoto-53/KanjiWorkSheet/assets/47249430/aed697b4-c1b1-4655-920e-b5545ed71e94)  
復習: 正解している問題の中で、出題日が最も古い問題を優先して出題する。  
練習: 「学習の進め方」の優先順位に従って出題する。  
苦手: 正解している問題の中で、過去10回で間違った回数が多いものを優先して出題する。  
6. 出題数を決定する。最大20問。  
![image](https://user-images.githubusercontent.com/47249430/221411748-a84af35f-46a6-4a49-9f5a-1ad7491fc05f.png)  
7. プリント作成ボタンを押すと、PDF形式で漢字プリントを作成する。  
![image](https://user-images.githubusercontent.com/47249430/221411825-52621f04-be6f-47cc-a5fe-7429aa579ed8.png) 
8. 印刷ボタンを押すと、作成した漢字プリントを開くことができる。  
![image](https://user-images.githubusercontent.com/47249430/221411848-1e1a0728-0be8-4caa-ab81-3b33dc437477.png)  

### 学習の進め方
以下、1、2を繰り返す（出題モードが"練習"の場合）。
1. 漢字プリント作成ツールで漢字プリントを作成する。
2. 問題を解いて、答え合わせをする。
下図の部分に作成した漢字プリントの答えが表示される。  
![image](https://user-images.githubusercontent.com/47249430/221412427-d293c50c-d02e-4392-8a67-b03de5ca7810.png)  

答えの下にあるボタンの記号の意味は以下の通り、  

| 記号 | 意味 |
|-----|-----|
| ― | 初めて出題する問題 |
| ✕ | 以前のテストで間違えた問題 |
| D | 一日後に出題する問題 |
| W | 一週間後に出題する問題 |
| M | 一ヶ月後に出題する問題 |
  
最終的に、○か×をボタンを押して選択する。  
全て選択し終えたら、採点完了ボタンを押す。  
そうすると、問題集に採点結果が反映される。
  
漢字プリント作成ツールは以下の優先順位で出題する。  
![image](https://user-images.githubusercontent.com/47249430/218885114-df749b97-58d1-4dad-938f-85b68aedfc27.png)

【出題の優先順位】  
次の日に出題 ＞ 一週間後に出題 ＞　一か月後に出題 ＞ 不正解 ＞ 未出題 ＞ 正解

### 準備するもの
#### 1. 問題集
CSV形式で以下のフォーマットに従って、問題文を作成する。  
セパレータはカンマ 「,」 をつかうこと。

入力例

| 学年 | 問題文 | 答え | 番号 | 管理番号 | 最終更新日 | 結果 | 履歴 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [あめ]の 日<ひ>が つづく。 | 雨 |自由記入|自由記入|自動入力|自動入力|自動入力|

---
##### 学年:
問題の対象の学年を記入する。  
1: 小学校1年生  
2: 小学校2年生  
3: 小学校3年生  
4: 小学校4年生  
5: 小学校5年生  
6: 小学校6年生  

---
##### 問題文:
以下のルールを守って記入する。  

|  ルール  |  意味  |
| ---- | ---- |
|   <>  | ルビ |
|   []  | 問題 |

また、問題文が長いとはみ出してしまう。
10文字程度が限界。
  
例)  
[あめ]の 日<ひ>が つづく。  
  
出力結果  
![image](https://user-images.githubusercontent.com/47249430/218754651-8966d618-82c1-4e64-bef1-1b51fe439df7.png)

---
##### 答え:
問題の答えを記入する。

---
##### 番号:
問題の番号を記入。  
問題文の管理に使用するためのもので、自由に使って良い。  

---
##### 管理番号:
管理用の番号。  
問題文の管理に使用するためのもので、自由に使って良い。

---
##### 最終更新日
ツールが自動で記入するため、何も入力してはならない。  
問題を出題した日時がツールによって記入される。  

---
##### 結果
ツールが自動で記入するため、何も入力してはいけない。  
各記号は以下の意味を持つ。

|  記号  |  意味  |
| ---- | ---- |
|   o  | 正解した問題 |
|   x  | 不正解した問題 |
|   d  | 一日後に再び出題する予定の問題 |
|   w  | 一週間後に再び出題する予定の問題 |
|   m  | 一ヶ月後に再び出題する予定の問題 |

---
##### 履歴
その問題の正解/不正解の履歴を記録する。  
ツールが自動で記入するため、何も入力してはならない。  
（将来、漢字プリントの出題方法で使用するため用意している。）
