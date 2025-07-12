import flet as ft
from booya_config_parser import config_parser


class BooyaConfigParserGui:
    def __init__(self):
        self.cp = FgConfigParser()

    def main(self, page: ft.page):
        """"""
        page.title = 'Booya Config Parser'
        page.window_width = 700
        page.window_height = 350

        ### 表示更新用にオブジェクトをまとめて更新
        view_objects = []
        def view_objects_update():
            for obj in view_objects:
                obj.update()

        ### コンフィグロード中などに操作無効化するオブジェクトをまとめて更新
        loading_objects = []

        def disable_loading_objects(disabled=True):
            for obj in loading_objects:
                obj.disabled = disabled
                obj.update()

        ## コンフィグファイルロード
        ### Path表示用テキスト
        selected_files = ft.Text('browse config file')
        view_objects.append(selected_files)
        loading_objects.append(selected_files)

        ### ファイル選択時の処理
        def pick_config_file(e: ft.FilePickerResultEvent):
            if e.files is not None:
                # 読み込み中に表示更新
                selected_files.value = f"loding {e.files[0].path}"
                disable_loading_objects(disabled=True)
                view_objects_update()

                # コンフィグフィルをロード
                self.cp.config_load(e.files[0].path)

                # ピッカーから取得したパスを表示
                selected_files.value = e.files[0].path
                disable_loading_objects(disabled=False)
                view_objects_update()
            else:
                pass
                # selected_files.value = "ファイルが選択されていません"
                # view_objects_update()

        ### ファイルピッカー
        pick_config_file_dialog = ft.FilePicker(on_result=pick_config_file)
        ### pageに追加
        page.overlay.append(pick_config_file_dialog)

        ### ボタン
        config_file_browse_btn = ft.ElevatedButton(
            "browse config file",
            icon=ft.icons.UPLOAD_FILE,
            on_click=lambda _: pick_config_file_dialog.pick_files(
                allow_multiple=False
            ),
            disabled=False,
        )
        loading_objects.append(config_file_browse_btn)

        ## exportディレクトリ選択
        ### Path表示用テキスト
        export_dir = ft.Text('select export dir')
        view_objects.append(export_dir)
        loading_objects.append(export_dir)

        ### ディレクトリ選択時の処理
        def pick_export_dir(e: ft.FilePickerResultEvent):
            if e.path is not None:
                # 読み込み中に表示更新
                export_dir.value = f"check dir {e.path}"
                disable_loading_objects(disabled=True)
                view_objects_update()

                # 存在や権限チェックなどの処理を追加するかも

                # ピッカーから取得したパスを表示
                export_dir.value = e.path
                disable_loading_objects(disabled=False)
                view_objects_update()
            else:
                pass
                # selected_files.value = "ファイルが選択されていません"
                # view_objects_update()

        ### ディレクトリピッカー
        pick_export_dir_dialog = ft.FilePicker(on_result=pick_export_dir)
        ### pageに追加
        page.overlay.append(pick_export_dir_dialog)

        ### ボタン
        export_dir_browse_btn = ft.ElevatedButton(
            "browse export dir",
            icon=ft.icons.FILE_DOWNLOAD_OUTLINED,
            on_click=lambda _: pick_export_dir_dialog.get_directory_path(
            ),
            disabled=False,
        )
        loading_objects.append(export_dir_browse_btn)

        #
        # メイン画面構成
        #
        main_column = ft.Column(
            controls=[
                # コンフィグファイル選択
                ft.Row(
                    controls=[
                        config_file_browse_btn,
                        selected_files,
                    ]
                ),
                # エクスポートディレクトリ選択
                ft.Row(
                    controls=[
                        export_dir_browse_btn,
                        export_dir,
                    ]
                ),
            ]
        )

        page.add(main_column)
        page.update()

    def run(self):
        ft.app(target=self.main)


if __name__ == '__main__':
    tfg = BooyaConfigParserGui()
    tfg.run()
