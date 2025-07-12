import zipfile
from xml.etree import ElementTree as ET
from pathlib import Path
from tempfile import TemporaryDirectory
from shutil import make_archive


def base_font_change(book_path, font='Yu Gothic UI') -> None:
    with TemporaryDirectory() as td:
        # 解凍
        with zipfile.ZipFile(book_path, 'r') as zip_ref:
            zip_ref.extractall(td)

        styles_path = Path(td, 'xl', 'theme', 'theme1.xml')
        tree = ET.parse(styles_path)
        root = tree.getroot()

        # 名前空間の登録
        ns = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}

        # フォント名の変更
        for font in root.findall(".//a:font[@script='Jpan']", ns):
            font.set('typeface', 'Yu Gothic UI')

        # 修正した内容をファイルに書き込む
        tree.write(styles_path, encoding="utf-8", xml_declaration=True)

        # 再圧縮
        output_excel = book_path
        # # os.walk
        # from os import walk
        # from os.path import relpath
        # with zipfile.ZipFile(output_excel, 'w') as zip_ref:
        #     for folder_name, subfolders, filenames in walk(td):
        #         for filename in filenames:
        #             file_path = Path(folder_name, filename)
        #             arcname = relpath(file_path, td)
        #             zip_ref.write(file_path, arcname)

        # # rglob
        # with zipfile.ZipFile(output_excel, 'w') as zip_ref:
        #     for file_path in Path(td).rglob('*'):  # 再帰的にすべてのファイル/フォルダを取得
        #         if file_path.is_file():  # ファイルのみを対象にする
        #             arcname = file_path.relative_to(td)  # 相対パスを取得
        #             zip_ref.write(file_path, arcname)

        # shutil
        make_archive(base_name=output_excel, format='zip', root_dir=td)
        Path(f'{output_excel}.zip').replace(output_excel)


if __name__ == '__main__':
    book_path = r'D:\opt\work\phy\booya_config_parser\tmp\export\fg_config.xlsx'
    base_font_change(book_path)