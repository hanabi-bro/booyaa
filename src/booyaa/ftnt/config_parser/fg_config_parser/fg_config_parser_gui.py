import flet as ft
from fg_config_parser import FgConfigParser
import pyperclip


fcp = FgConfigParser()

def main(page: ft.page):
    def pick_files_result(e: ft.FilePickerResultEvent):
            selected_files.value = e.files[0].path if e.files[0].path else "Cancelled!"
            selected_files.update()

            for obj in export_objs:
                obj.value = ""
                obj.update()

    def export_file_result(e: ft.FilePickerResultEvent):
            export_dir.value = e.path if e.path else "Cancelled!"
            export_dir.update()

    def convert_firewall_policy():
            export_fw_policy_result.value = "config parsing  ..."
            export_fw_policy_result.update()
            res = fcp.load_config(selected_files.value)
            if "error:" in res:
                selected_files.value = res
                selected_files.update()

            result = fcp.to_csv_fw_policy(export_dir.value)
            export_fw_policy_result.value = result
            export_fw_policy_result.update()

    def convert_firewall_address():
            export_fw_address_result.value = "config parsing  ..."
            export_fw_address_result.update()
            res = fcp.load_config(selected_files.value)
            if "error:" in res:
                selected_files.value = res
                selected_files.update()

            result = fcp.to_csv_fw_address(export_dir.value)
            export_fw_address_result.value = result
            export_fw_address_result.update()

    def convert_firewall_vip():
            export_fw_vip_result.value = "config parsing  ..."
            export_fw_vip_result.update()
            res = fcp.load_config(selected_files.value)
            if "error:" in res:
                selected_files.value = res
                selected_files.update()

            result = fcp.to_csv_fw_vip(export_dir.value)
            export_fw_vip_result.value = result
            export_fw_vip_result.update()

    def copy_clipboard_export_directory(pick_file_obj):
            pyperclip.copy(str(pick_file_obj.value))

    pick_files_dialog = ft.FilePicker(on_result=pick_files_result)
    export_dir_dialog = ft.FilePicker(on_result=export_file_result)
    selected_files = ft.Text()
    export_dir = ft.Text(value='.')
    export_fw_policy_result = ft.Text()
    export_fw_address_result = ft.Text()
    export_fw_vip_result = ft.Text()

    export_objs = [
        export_fw_policy_result,
        export_fw_address_result,
        export_fw_vip_result,
    ]

    main_column = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.ElevatedButton(
                        "コンフィグファイル選択",
                        icon=ft.icons.UPLOAD_FILE,
                        on_click=lambda _: pick_files_dialog.pick_files(
                            allow_multiple=False
                        ),
                    ),
                    selected_files,
                ]
            ),
            ft.Row(
                controls=[
                    ft.ElevatedButton(
                        "CSVのExportディレクトリ選択",
                        icon=ft.icons.FILE_DOWNLOAD_OUTLINED,
                        on_click=lambda _: export_dir_dialog.get_directory_path(
                        ),
                    ),
                    export_dir,
                ]
            ),
            ft.Row(
                controls=[
                    ft.ElevatedButton(
                        "Firewall PolicyをCSVへExport",
                        icon=ft.icons.FILE_DOWNLOAD,
                        on_click=lambda _: convert_firewall_policy(
                        ),
                    ),
                    export_fw_policy_result,
                    ft.ElevatedButton(
                        "ファイルパスをコピー",
                        on_click=lambda _: copy_clipboard_export_directory(
                            export_fw_policy_result
                        ),
                    ),
                ]
            ),
            ft.Row(
                controls=[
                    ft.ElevatedButton(
                        "Firewall AddressをCSVへExport",
                        icon=ft.icons.FILE_DOWNLOAD,
                        on_click=lambda _: convert_firewall_address(
                        ),
                    ),
                    export_fw_address_result,
                    ft.ElevatedButton(
                        "ファイルパスをコピー",
                        on_click=lambda _: copy_clipboard_export_directory(
                            export_fw_address_result
                        ),
                    ),
                ]
            ),
            ft.Row(
                controls=[
                    ft.ElevatedButton(
                        "Firewall VIPをCSVへExport",
                        icon=ft.icons.FILE_DOWNLOAD,
                        on_click=lambda _: convert_firewall_vip(
                        ),
                    ),
                    export_fw_vip_result,
                    ft.ElevatedButton(
                        "ファイルパスをコピー",
                        on_click=lambda _: copy_clipboard_export_directory(
                            export_fw_vip_result
                        ),
                    ),
                ]
            ),
        ]
    )

    page.overlay.append(pick_files_dialog)
    page.overlay.append(export_dir_dialog)

    page.add(main_column)
    page.update()


if __name__ == '__main__':
    ft.app(target=main)
    # ft.app(target=main, view=ft.WEB_BROWSER)

