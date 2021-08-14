# Kobushi trackviewer

Bve trainsim 5/6向けのマップファイルから、線路平面図・縦断面図を生成するPythonスクリプトです。

動作にはPython 3が必要です。

## インストール

次のコマンドを実行してください。
```
pip install kobushi-trackviewer
```

動作に必要な下記パッケージを同時にインストールします。

* numpy
* scipy
* matplotlib
* lark
* ttkwidgets
## 使い方

[こちら](manual.md)を参照

## おことわり

バージョン1.10以前のマップファイルには対応していません。[マップコンバーター](https://bvets.net/jp/download/conv.html)でMap 2.00への変換をお願いします。

多バイト文字を変数名に使用しているマップは読み込めません。変数名に利用できる文字は英字(A-Z, a-z), 数字(0-9), アンダーバー(_)です。

その他、BVE本体では読み込み可能なマップファイルがKobushiでは正しく読み込めない場合があります。ご了承ください。

## LICENSE

Apache License, Version 2.0 