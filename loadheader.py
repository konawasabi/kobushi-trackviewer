import pathlib
import re

def loadheader(path,HEAD_STR,HEAD_VER):
    '''ファイルヘッダー・バージョン・エンコードを確認して、問題なければオープンする
    path: ファイルフルパス
    HEAD_STR: ヘッダー文字列
    HEAD_VER: 許容するバージョン下限値
    '''
    #input = pathlib.Path(re.sub(r'\\','/',path))
    input = pathlib.Path(path)
    rootpath = input.resolve().parent
    try:
        f = open(input,'rb') #文字コードが不明なのでバイナリで読み込む
        header = f.readline().decode('utf-8') #一行目をutf-8でデコード。
        f.close()
    except Exception as e:
        raise OSError()

    if(HEAD_STR.casefold() not in header.casefold()):
        raise RuntimeError(str(path) + ' is not ' + HEAD_STR)

    header_version = float(re.findall(r'\d+.\d+',header)[0]) # 入力文字列からバージョン番号'xxxx.xxxxx'に最初に一致する部分を取り出す
    header_encoding = 'utf-8' if re.findall(r':[a-zA-z][a-zA-Z0-9\-_]+',header) == [] else re.findall(r':[a-zA-z][a-zA-Z0-9\-_]+',header)[0][1:] # エンコーディング指定':hoge1-huga2'と最初に一致する部分を取り出し、文頭コロンを除外。見つからない時は'utf-8'
    if(header_version < HEAD_VER):
        raise RuntimeError(str(path) + ' is under Ver.' +str(HEAD_VER))
    
    if(header_encoding.casefold() == 'shift_jis'.casefold() or header_encoding.casefold() == 'sjis'.casefold()):
        header_encoding = 'CP932'

    return input, rootpath, header_encoding
    #return open(input,'r',encoding=header_encoding), str(input), rootpath

def joinpath(rootpath, filepath):
    '''includeするファイルの相対パスを絶対パスに変換。
    rootpath: 呼び出し元ファイルの親ディレクトリ
    filepath: 呼び出すファイルの相対パス
    '''
    return rootpath.joinpath(pathlib.Path(re.sub(r'\\','/',filepath))) # パス文字列にバックスラッシュが含まれている場合置き換える
