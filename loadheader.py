import pathlib

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
        header = f.readline().decode('utf-8') #一行目をutf-8でデコード。日本語コメントが一行目にあると詰む
        f.close()
    except Exception as e:
        raise

    if(HEAD_STR not in header):
        raise
    ix = header.find(HEAD_STR)
    header_directive = header[ix+len(HEAD_STR):-1]
    if(':' in header_directive):
        header_version = float(header_directive.split(':')[0])
        header_encoding = header_directive.split(':')[1]
    else:
        header_version = float(header_directive)
        header_encoding = 'utf-8'
    if(header_version < HEAD_VER):
        raise

    return open(input,'r',encoding=header_encoding), str(input), rootpath

def joinpath(rootpath, filepath):
    '''includeするファイルの相対パスを絶対パスに変換。
    rootpath: 呼び出し元ファイルの親ディレクトリ
    filepath: 呼び出すファイルの相対パス
    '''
    return rootpath.joinpath(pathlib.Path(filepath))
