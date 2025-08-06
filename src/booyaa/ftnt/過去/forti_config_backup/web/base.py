from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from time import sleep
from pathlib import Path
from tempfile import TemporaryDirectory
import json

import requests
from urllib.parse import urljoin
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
disable_warnings(InsecureRequestWarning)


class Web:
    def __init__(self):
        self.fg_addr = ''
        self.fg_port = ''
        self.fg_user = ''
        self.fg_pass = ''
        self.fg_alias = ''
        self.fg_hostname = ''

        self.base_url = f'https://{self.fg_addr}/api/v2/'
        self.session = requests.Session()
        self.session.verify = False
        self.root_dir = Path(__file__).parent.resolve()
        config_ini = 'config.ini'
        self.config_ini_path = Path(Path(__file__).parent.parent.resolve(), config_ini)

        self.read_config_ini(config_ini)

        # node info
        self.hostname = ''
        self.serial = ''
        self.version = ''
        self.major = ''
        self.minor = ''
        self.patch = ''
        self.build = ''

        self.model = ''

        self.manage_vdom = 'root'
        self.vdom_mode = ''

        self.ha_mode = ''
        self.ha_role = ''

        self.secondary_hostname = ''
        self.secondary_serial = ''
        self.secondary_ha_mode = ''
        self.secondary_ha_role = ''
        self.result_message = ''
        self.error = None

    def set_target(self, target, user, password, alias=None):
        """ターゲットをセット
        Args:
            traget:
            user:
            password:
            alias:
        """
        let = {'code': 0, 'msg': '', 'output': ''}

        # ポート指定があったら、一応取っておく
        if ':' in target:
            _, port = target.split(':')
            port = int(port)
        else:
            port = 443

        self.fg_addr = target
        self.fg_port = port
        self.fg_user = user
        self.fg_pass = password

        # エリアス指定
        if alias is not None:
            self.fg_alias = alias

        # バックアップディレクトリ
        self.backup_directory = r'./fg_config'

        # Fortigate　APIベースURL
        self.base_url = f'https://{self.fg_addr}'

        let['msg'] = f'Set to {self.fg_addr}, user: {self.fg_user}'

        return let

    def login(self, tmp_path: TemporaryDirectory, config_dir='./tmp') -> dict:
        """
        Fortigateにログインする関数
        :param webdriver: Selenium WebDriver
        :param target: FortigateのIPアドレス
        :param user: ユーザー名
        :param password: パスワード
        """
        let = {'code': 0, 'msg': '', 'output': ''}

        # ドライバーセットアップ
        # オプション設定
        options = webdriver.ChromeOptions()

        # ダウンロード設定
        prefs = {
            "download.default_directory": tmp_path,
            "download.prompt_for_download": False,
            "directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)

        # SSL証明書エラーを無視するオプション
        options.add_argument('--ignore-certificate-errors')
        self.driver = webdriver.Chrome(options=options)

        # FGにアクセス
        # ログイン後の読み込み速度も踏まえバックアップページにアクセス
        backup_url = urljoin(self.base_url, '/ng/system/config/backup')
        try:
            self.driver.get(self.base_url)
        except Exception as e:
            let['code'] = 1
            let['msg'] = f"[Error]Login Error: {e} {target}"
            let['output'] = str(e)
            return let

        # ログイン画面表示完了待ち
        WebDriverWait(self.driver, 30).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )

        # ログインフォームの要素が読み込まれるまで待機
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.ID, 'username'))
        )


        # エラー確認
        error_div = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.ID, "err_msg_content"))
        )

        if error_div.text == '':
            let['code'] = 0
            let['msg'] = ''
            let['output'] = self.driver.page_source
        else:
            let['code'] = 1
            let['msg'] = f'[Error]Access Error: {error_div.text} {target}'
            let['output'] = error_div.text
            # 必要に応じて return や raise を入れて処理を中断

        # ログイン
        # ユーザー名とパスワードを入力
        self.driver.find_element(By.ID, 'username').send_keys(user)
        self.driver.find_element(By.ID, 'secretkey').send_keys(password)
        self.driver.find_element(By.ID, 'login_button').click()

        # ここでsleepしないとうまくいかないことがある。
        # print('ログイン中... (5秒待機)')
        # sleep(5)

        # WebDriverWaitではログイン完了を待てないので、loopで頑張ってみる。
        error_div = ''
        print('ログイン確認ループ開始')
        for i in range(30):
            current_url = self.driver.current_url

            print(current_url)
            sleep(1)

            if 'backup' in current_url:
                print(f'backup page: {current_url}')
                # バックアップページに移動できた場合は成功
                let['code'] = 0
                let['msg'] = f'[Success]Login Success: {target}'
                let['output'] = self.driver.page_source
                break
            # ログインURLだった場合はログインに失敗
            if 'login' in current_url:
            # エラー確認
                print(f'login page: {current_url}')
                try:
                    error_div = WebDriverWait(self.driver, 1).until(
                        EC.presence_of_element_located((By.ID, "err_msg_content"))
                    )
                    if error_div.text != '':
                        let['code'] = 1
                        let['msg'] = f'[Error]Login Error: {error_div.text} {target}'
                        let['output'] = error_div.text
                        print(let['msg'])
                        break
                except Exception:
                    error_div = ''
                    continue

            else:
                print(f'other page: {current_url}')
                # セットアップ、オーバービューをスキップするため、バックアップページへ移動
                self.driver.get(backup_url)
                break

            print(f"現在のURL:[{i}] {current_url}")
            print(f'error message: {error_div.text}')
            sleep(1)

        return let

    def get_node_info(self):
        """
        '/monitor/system/csf'がかなり一度に多くの情報が取れることを発見したので差し替え
        """

        let = {'code': 0, 'msg': '', 'output': ''}
        uri = f'{self.base_url}/monitor/system/csf'

        # cokkieの取得
        for cookie in self.driver.get_cookies():
            self.session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])

        res = self.session.get(uri, timeout=self.timeout)
        let['output'] = res.content.decode('utf-8').split('\n')

        if res.status_code == 200:
            res_data = json.loads(res.content.decode('utf-8'))

            # --------------------- for debug ---------------------
            with open(Path('./tmp', 'debug.json'), 'w', encoding='utf-8') as f:
                json.dump(res_data, f, indent=2, ensure_ascii=False)
            # --------------------- for debug ---------------------

            res_data = res_data['results']['devices']['fortigate'][0]

            self.hostname = res_data['host_name']
            self.serial = res_data['serial']
            self.major = res_data['firmware_version_major']
            self.minor = res_data['firmware_version_minor']
            self.patch = res_data['firmware_version_patch']
            self.build = res_data['firmware_version_build']
            self.version = f'{self.major}.{self.minor}.{self.patch}'
            self.model = res_data['model']

            self.vdom_mode = res_data['state']['vdom_mode']
            self.manage_vdom = res_data['state']['management_vdom']

            self.ha_mode = res_data['ha_mode']

            if self.ha_mode == 'active-passive' or self.ha_mode == 'a-p':
                self.ha_role = 'master' if res_data['is_ha_master'] == 1 else 'slave'
                ha_list = res_data['ha_list']
                for ha_info in ha_list:
                    if ha_info['hostname']  == self.hostname:
                        next
                    else:
                        self.secondary_hostname = ha_info['hostname']
                        self.secondary_serial = ha_info['serial_no']
                        self.secondary_ha_role = 'primary' if ha_info['is_ha_primary'] else 'secondary'
                        break

            let['msg'] = f'get node info {self.fg_addr}'

        else:
            let['code'] = 1
            let['msg'] = f'[Error] Fail get node info {self.fg_addr}'

        return let

    def backup(self, tmp_path, config_dir='./tmp', config_file_name=False) -> dict:
        """
        Fortigateの設定バックアップを取得する関数
        :param config_dir: コンフィグ保存ディレクトリ
        """
        let = {'code': 0, 'msg': '', 'output': ''}

        # バックアップページでなければ、バックアップページへ移動
        current_url = self.driver.current_url
        backup_url = urljoin(self.base_url, '/ng/system/config/backup')

        if 'backup' not in current_url:
            self.driver.get(backup_url)

        WebDriverWait(self.driver, 30).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )

        # バックアップボタンをクリック
        backup_button = WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.ID, 'submit_ok'))
        )
        backup_button.click()

        # バックアップ処理の完了を待機
        # WebDriverWait(self.driver, 30).until(
        #     EC.presence_of_element_located((By.ID, 'backup_complete'))
        # )

        # ダウンロードが完了するまで待機
        WebDriverWait(self.driver, 300).until(
            lambda d: len(list(Path(tmp_path).glob("*.conf"))) > 0
        )

        print("バックアップが完了しました。")
        self.driver.quit()

        # ダウンロードしたファイルを指定のディレクトリに移動
        backup_files = list(Path(tmp_path).glob("*.conf"))
        for backup_file in backup_files:
            backup_file.rename(Path(config_dir) / backup_file.name)

        return let


if __name__ == "__main__":
    web = Web()

    with TemporaryDirectory() as tmpdir:
        tmp_path = str(Path(tmpdir).absolute())

        res = web.login("172.16.201.202", "admin", "P@ssw0rd", tmp_path)
        if res['code'] == 0:
            print("ログイン成功")
            res = web.backup(tmp_path)
        else:
            print(f"ログイン失敗: {res['msg']}")
