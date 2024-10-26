# Change Log

## to be implemented

## [1.2.2] - 2024-10-26

- 他軌道Y座標の計算方法を修正

## [1.2.1] - 2024-07-29
- scipy 1.14.0以降で、integrate.cumtrapz が実行できずエラーとなることに対応
- include文実行時に対象ファイルがオープンできなかった場合、以降の読み込みを継続するように変更

## [1.2.0] - 2024-04-14
- 線路平面図・縦断面図で使用するフォントの変更に対応
  - Optionメニュー-> Font...で表示されるリストから選択する
  - コマンドライン引数(-f)で指定することも可能
- 依存ライブラリのバージョン条件を追加

## [1.1.7] - 2024-04-08
- ASCII文字以外を変数名に用いたマップに対応
- 空文字列を軌道キーに設定したマップに対応
  - 暫定的な対応であり、十分なテストを行っていない

## [1.1.6] - 2023-07-22
- 既定変数、ユーザー定義変数を別個に扱うように修正
  - 既定変数: $記号をつけずに呼び出せる変数。BveTs Map 2.02 ではdistanceのみ
  - https://github.com/konawasabi/tsutsuji-trackcomputer/issues/1 への対応

## [1.1.5] - 2023-06-25
- 他軌道のパラメータ計算方法を修正
  - 最終制御点のデータが反映されない問題の解消

## [1.1.4] - 2022-10-15
- ライブラリ外からmap-grammer.larkを呼び出すため、マップ文法ファイルをopenするルーチンを独立。

## [1.1.3] - 2022-05-22
- mapinterpleter.load_filesで、文字列を受け取ってパースする機能を実装
  - tsutsuji-trackcomputer向け
- コマンドライン引数(-s)で軌道座標の計算間隔を指定

## [1.1.2] - 2022-04-29
- Sin半波長逓減関数に対応していないルーチンの修正
  - tsutsuji-trackcomputer向け

## [1.1.1] - 2022-04-18
- utf-8, shift-jisの全角スペースを半角スペースと同等に扱う

## [1.1.0] - 2022-04-05
- 自軌道のカント算出
- 他軌道のカント算出
- ロードするmapファイルを起動時引数で指定
- グラフファイル出力時のエラー修正
- デバッグモードでのNumpyRuntimeErrorの取り扱いを見直し

## [1.0.3] - 2021-10-23
- 緩和曲線が存在しない円軌道の算出ルーチンを修正
- Curve要素が存在しないマップファイルを読み込めない問題を修正

## [1.0.2] - 2021-10-23
- 平面緩和曲線算出ルーチンの修正
    - sin半波長逓減関数を有効化

## [1.0.1] - 2021-08-21
- グラフサイズ、余白の調整
- ウィンドウリサイズに対応
- 内部構成の変更
    - ソースファイル名の修正
    - 文法定義ファイルの読み込みタイミングを変更
- リファレンスの追記

## 1.0 - 2021-08-16
- 1st release

[1.0.1]: https://github.com/konawasabi/kobushi-trackviewer/compare/ver1.0...ver1.0.1
[1.0.2]: https://github.com/konawasabi/kobushi-trackviewer/compare/ver1.0.1...ver1.0.2
[1.0.3]: https://github.com/konawasabi/kobushi-trackviewer/compare/ver1.0.2...ver1.0.3
[1.1.0]: https://github.com/konawasabi/kobushi-trackviewer/compare/ver1.0.3...ver1.1.0
[1.1.1]: https://github.com/konawasabi/kobushi-trackviewer/compare/ver1.1.0...ver1.1.1
[1.1.2]: https://github.com/konawasabi/kobushi-trackviewer/compare/ver1.1.1...ver1.1.2
[1.1.3]: https://github.com/konawasabi/kobushi-trackviewer/compare/ver1.1.2...ver1.1.3
[1.1.4]: https://github.com/konawasabi/kobushi-trackviewer/compare/ver1.1.3...ver1.1.4
[1.1.5]: https://github.com/konawasabi/kobushi-trackviewer/compare/ver1.1.4...ver1.1.5
[1.1.6]: https://github.com/konawasabi/kobushi-trackviewer/compare/ver1.1.5...ver1.1.6
[1.1.7]: https://github.com/konawasabi/kobushi-trackviewer/compare/ver1.1.6...ver1.1.7
[1.2.0]: https://github.com/konawasabi/kobushi-trackviewer/compare/ver1.1.7...ver1.2.0
[1.2.1]: https://github.com/konawasabi/kobushi-trackviewer/compare/ver1.2.0...ver1.2.1
