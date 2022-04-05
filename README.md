# Kobushi trackviewer

Bve trainsim 5/6向けのマップファイルから、線路平面図・縦断面図を生成するPythonスクリプトです。

動作にはPython 3が必要です。

## インストール

Powershellで次のコマンドを実行してください。
```
pip install kobushi-trackviewer
```
Kobushi本体と、動作に必要な下記パッケージが自動でインストールされます。

* [numpy](https://numpy.org)
* [matplotlib](https://matplotlib.org)
* [scipy](https://www.scipy.org)
* [lark](https://lark-parser.readthedocs.io/en/latest/)
* [ttkwidgets](https://ttkwidgets.readthedocs.io/en/latest/)

### アップデート

すでに旧バージョンのkobushiをインストール済みの方は、次のコマンドで最新版へアップデートできます。
```
pip install -U kobushi-trackviewer
```

## 起動
Powershellで以下のコマンドを実行します。
```
python -m kobushi
```

`python -m kobushi hoge.txt`として、読み込みたいマップファイルを指定して起動することも可能です。

## リファレンス

[こちら](reference.md)を参照

## おことわり

バージョン1.10以前のマップファイルには対応していません。[マップコンバーター](https://bvets.net/jp/download/mapconv.html)でMap 2.00への変換が必要です。

多バイト文字を変数名に使用しているマップには対応していません。変数名に利用できる文字は英字(A-Z, a-z), 数字(0-9), アンダーバー(_)です。

その他、BVE本体では読み込み可能なマップファイルがKobushiでは正しく読み込めない場合があります。ご了承ください。

## License

[Apache License, Version 2.0](LICENSE)

## 重要事項

本プログラムの著作権は[konawasabi](#Contact) (以下、作者)が有します。

本プログラムについて作者はいかなる保証もせず、またプログラムを実行して生じた結果についての責任を負いません。

Apache Licence, Version 2.0に従う限り、本ソフトウェアの改変、再配布を自由に行うことができます。

## Contact

Author: Konawasabi

Mail: webmaster@konawasabi.riceball.jp

Website: https://konawasabi.riceball.jp/
