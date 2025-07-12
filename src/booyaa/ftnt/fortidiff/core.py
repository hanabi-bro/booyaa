import re
import textwrap
import difflib
import subprocess
import tempfile
import os

class Core():
    def __init__(self):
        self.parser = FtntConfigParse()

    def load_config_from_file(self, file_path):
        with open(file_path, 'r', encoding='UTF-8_sig') as f:
            config_text = f.read()
        
        configs = config_text.splitlines()
        
        return configs
    
    def parse_configs(self, config_file_path, empty_line=True, config_version=True, encryption=True, cert=True, uuid=True, ifindex=True):
        configs = self.load_config_from_file(config_file_path)
        if empty_line:
            configs = self.parser.remove_empty_line(configs)
        if config_version:
            configs = self.parser.remove_config_version(configs)
        if encryption:
            configs = self.parser.remove_encryption(configs)
        if cert:
            configs = self.parser.remove_cert(configs)
        if uuid:
            configs = self.parser.remove_uuid(configs)
        if ifindex:
            configs = self.parser.remove_ifindex(configs)
        
        return configs

    def diff_print(self, orig_file, new_file):
        orig_parsed_configs = self.parse_configs(orig_file)
        new_parsed_configs = self.parse_configs(new_file)
        
        self.open_diff_tool(orig_parsed_configs, new_parsed_configs)
        
    def open_diff_tool(self, orig_configs, new_configs):
        """
        winmergeu.exe
            -or "出力パス"
            -e # ESCキーでClose可能"
            -noninteractive # ファイル出力のみ
            -noprefs # レジストリを使わずデフォルト設定
            -wl # 左を読み込み専用
            -wr # 右を読み込み専用
            -u # 履歴に残さない
            -cp # コードページ指定
            -ignorews # 空白無視
            -ignoreblanklines # 空白無視
            -ignoreeol # 改行無視
            -ignorecodepage # コードページ無視
            -cfg "設定情報" # 設定パラメータを渡す
        """
        fds = []
        tmps = []
        
        for i in [orig_configs, new_configs]:
            fd, tmp = tempfile.mkstemp(text=True)
            fds.append(fd), tmps.append(tmp)
            with open(tmp, 'w') as f:
                f.write('\n'.join(i))

        cmd = [
            'WinMergeU.exe',
            tmps[0],
            tmps[1],
            '-wl',
            '-wr',
            '-u',
            '-e',
            '-cp', '65001',
            '-noprefs',
            '-ignorews',
            '-ignoreblanklines',
            '-ignoreeol',
            '-ignorecodepage',
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # print(f'returncode: {res.returncode},stdout: {res.stdout},stderr: {res.stderr}')

        for i in range(2):
            os.close(fds[i])
            os.unlink(tmps[i])


class FtntConfigParse():    
    def remove_empty_line(self, configs):
        skip_word = re.compile(r'^"$')
        removed_configs = self.remove_line_with_word_re(configs, skip_word)
        return removed_configs

    def remove_config_version(self, configs):
        skip_word = re.compile(r'conf_file_ver')
        removed_configs = self.remove_line_with_word_re(configs, skip_word)
        return removed_configs

    def remove_encryption(self, configs):
        skip_word = re.compile(r'set password ENC|set passwd ENC|set wifi-passphrase ENC|set .*key ENC|set public-key')
        removed_configs = self.remove_line_with_word_re(configs, skip_word)
        return removed_configs

    def remove_uuid(self, configs):
        skip_word = re.compile(r'set uuid ')
        removed_configs = self.remove_line_with_word_re(configs, skip_word)
        return removed_configs

    def remove_ifindex(self, configs):
        skip_word = re.compile(r'set snmp-index')
        removed_configs = self.remove_line_with_word_re(configs, skip_word)
        return removed_configs

    def remove_line_with_word_re(self, configs, skip_word):
        removed_configs = []

        for l in configs:
            if skip_word.search(l):
                continue
            removed_configs.append(l)
        
        return removed_configs

    def remove_cert(self, configs):
        b64start = re.compile('-----BEGIN')
        b64end = re.compile('-----END')
        skip = False
        removed_configs = []
        for l in configs:
            ## BEGIN から END まで読み飛ばす
            if b64start.search(l):
                skip = True

            if skip is True:
                if b64end.search(l):
                    skip = False

                continue
            
            removed_configs.append(l)
        
        return removed_configs

if __name__ == '__main__':
    orig = 'NEPNWFW01_20221128_0119.conf'
    new = 'NEPNWFW01_20230531_1246.conf'
    
    tc = Core()
    tc.diff_print(orig, new)
