from booyaa.ftnt.fgt import Fgt
from booyaa.ftnt.fgt.model.fgt_info import FgtInfo
from booyaa.ftnt.fgt.model.progress import Progress

from booyaa.common.export.save_file import save_config, save_debug_report
from booyaa.common.fire_and_forget import fire_and_forget

from concurrent.futures import ThreadPoolExecutor
from time import sleep
from pathlib import Path


class FgtObj(Fgt):
    def __init__(self):
        super().__init__()
        self.progress = Progress()

    def setup(self, primary=True, secondary=False, config=True, debug=False, cli_only=False, **kwargs):
        super().setup(**kwargs)
        self.target_priamry=primary
        self.target_secondary=secondary
        self.target_config=config
        self.target_debug=debug
        self.target_cli_only = cli_only

    def primary_export(self, config=None, debug_report=None, cli=None):
        if cli:
            obj = self.cli
        else:
            obj = self.api

        config = self.target_config if config is None else config
        debug_report = self.target_debug if debug_report is None else debug_report
        cli = self.target_cli_only if cli is None else cli

        let = obj.login()
        self.progress.login.code = let['code']
        self.progress.login.msg = let['msg']
        self.progress.login.output = let['output']
        if let['code'] == 0:
            self.progress.login.result = '[green]OK[/]'
        elif let['code'] > 0:
            self.progress.login.result = '[red]NG[/]'
            self.progress.msg = let['msg']
            return let

        #
        # config backup
        #
        if config:
            let = obj.export_backup()
            self.progress.backup.code = let['code']
            self.progress.backup.msg = let['msg']
            self.progress.backup.output = let['output']
            if let['code'] == 0:
                self.progress.backup.result = '[green]OK[/]'
            elif let['code'] > 0:
                self.progress.backup.result = '[red]NG[/]'
                self.progress.msg = let['msg']
                return let

        #
        # debug report
        #
        if debug_report:
            let = obj.export_debug_report()
            self.progress.debugreport.code = let['code']
            self.progress.debugreport.msg = let['msg']
            self.progress.debugreport.output = let['output']
            if let['code'] == 0:
                self.progress.debugreport.result = '[green]OK[/]'
            elif let['code'] > 0:
                self.progress.debugreport.result = '[red]NG[/]'
                self.progress.msg = let['msg']
                return let

        #
        # logout
        #
        let = obj.logout()
        self.progress.logout.code = let['code']
        self.progress.logout.msg = let['msg']
        self.progress.logout.output = let['output']
        if let['code'] == 0:
            self.progress.logout.result = '[green]OK[/]'
        elif let['code'] > 0:
            self.progress.logout.result = '[red]NG[/]'
            return let

    def secondary_export(self, config=None, debug_report=None, cli=True):
        if cli:
            obj = self.cli
        # else:
        #     obj = self.api

        config = self.target_config if config is None else config
        debug_report = self.target_debug if debug_report is None else debug_report
        # secondaryは今のところCLIのみ
        cli = True

        let = obj.login()
        self.progress.login.code = let['code']
        self.progress.login.msg = let['msg']
        self.progress.login.output = let['output']
        # primary login check
        if let['code'] == 0:
            self.progress.msg = let['msg']
        elif let['code'] > 0:
            self.progress.login.result += '[red]NG[/]'
            self.progress.msg = let['msg']
            return let

        # secondary login check
        let = obj.login_secondary()
        if let['code'] == 0:
            self.progress.login.result += '[green]OK[/]'
            self.progress.msg = let['msg']
        elif let['code'] > 0:
            self.progress.login.result += '[red]NG[/]'
            self.progress.msg = let['msg']
            return let

        #
        # config backup
        #
        if config:
            let = obj.export_backup(secondary=True)
            self.progress.backup.code = let['code']
            self.progress.backup.msg = let['msg']
            self.progress.backup.output = let['output']
            if let['code'] == 0:
                self.progress.backup.result += '\n[green]OK[/]'
            elif let['code'] > 0:
                self.progress.backup.result += '\n[red]NG[/]'
                self.progress.msg = let['msg']
                return let

        #
        # debug report
        #
        if debug_report:
            let = obj.export_debug_report(secondary=True)
            self.progress.debugreport.code = let['code']
            self.progress.debugreport.msg = let['msg']
            self.progress.debugreport.output = let['output']
            if let['code'] == 0:
                self.progress.debugreport.result += '\n[green]OK[/]'
            elif let['code'] > 0:
                self.progress.debugreport.result += '\n[red]NG[/]'
                self.progress.msg = let['msg']
                return let

        #
        # logout
        #
        obj.logout_secondary()
        let = obj.logout()
        self.progress.logout.code = let['code']
        self.progress.logout.msg = let['msg']
        self.progress.logout.output = let['output']
        if let['code'] == 0:
            self.progress.logout.result += '[green]OK[/]'
        elif let['code'] > 0:
            self.progress.logout.result += '[red]NG[/]'
            return let


if __name__ == '__main__':
    tmp = {
        'addr': '172.16.201.201',
        'user': 'admin',
        'password': 'P@ssw0rd',
    }

    fgtobj = FgtObj()
    fgtobj.setup(**tmp)
    fgtobj.cli.display=True

    let = fgtobj.secondary_export(config=True, debug_report=True)

