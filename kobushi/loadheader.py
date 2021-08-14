'''
    Copyright 2021 konawasabi

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''
import pathlib
import re

def loadheader(path,HEAD_STR,HEAD_VER):
    '''ファイルヘッダー・バージョン・エンコードを確認して、問題なければオープンする
    path: ファイルフルパス
    HEAD_STR: ヘッダー文字列
    HEAD_VER: 許容するバージョン下限値
    '''
    
    input = pathlib.Path(path)
    rootpath = input.resolve().parent
    try:
        f = open(input,'rb') #文字コードが不明なのでバイナリで読み込む
        top2 = f.read(2) #ファイル先頭の2byteを読み取り、utf-16かどうか判断。
        if top2 == b'\xff\xfe':
            header_encoding = 'utf-16le'
        elif top2 == b'\xfe\xff':
            header_encoding = 'utf-16be'
        else: # utf-16でなければとりあえずutf-8と仮定する
            header_encoding = 'utf-8'
        f.seek(0)
        header = f.readline().decode(header_encoding,'ignore') #一行目をheader_encodingでデコード
        f.close()
    except Exception as e:
        raise OSError('File open error: '+str(input))

    if(HEAD_STR.casefold() not in header.casefold()):
        raise RuntimeError(str(path) + ' is not ' + HEAD_STR)

    header_version = float(re.findall(r'\d+.\d+',header)[0]) # 入力文字列からバージョン番号'xxxx.xxxxx'に最初に一致する部分を取り出す
    if(header_version < HEAD_VER):
        raise RuntimeError(str(path) + ' is under Ver.' +str(HEAD_VER))
    if(header_encoding == 'utf-8'):
        header_encoding = 'utf-8' if re.findall(r':[a-zA-z][a-zA-Z0-9\-_]+',header) == [] else re.findall(r':[a-zA-z][a-zA-Z0-9\-_]+',header)[0][1:] # エンコーディング指定':hoge1-huga2'と最初に一致する部分を取り出し、文頭コロンを除外。見つからない時は'utf-8'
    
        if(header_encoding.casefold() == 'shift_jis'.casefold() or header_encoding.casefold() == 'sjis'.casefold()):
            header_encoding = 'CP932'

    return input, rootpath, header_encoding

def joinpath(rootpath, filepath):
    '''includeするファイルの相対パスを絶対パスに変換。
    rootpath: 呼び出し元ファイルの親ディレクトリ
    filepath: 呼び出すファイルの相対パス
    '''
    return rootpath.joinpath(pathlib.Path(re.sub(r'\\','/',filepath))) # パス文字列にバックスラッシュが含まれている場合置き換える
