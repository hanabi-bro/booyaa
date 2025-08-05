from pathlib import Path
from datetime import datetime
from pygit2 import GitError, init_repository, Repository


class MyGit:
    def setup(self, repo_path=None):
        if repo_path is None:
            self.repo_path = Path('config_backup')
        else:
            self.repo_path = Path(repo_path)

        self.repo = self.init_git_repo()

    def init_git_repo(self):
        try:
            repo = init_repository(self.repo_path, False)
        except GitError:
            repo = Repository(self.repo_path, False)
        return repo

    def add(self, path=''):
        index = self.repo.index
        if path == '':
            index.add_all()
        else:
            index.add(path)
        self.repo.index.write()

    def commit(self, message=None, author=None, committer=None):
        index = self.repo.index
        if message is None:
            message = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        if author is None:
            author = self.repo.default_signature
        if committer is None:
            committer = author
        tree = index.write_tree()

        try:
            ref = self.repo.head.name
            parents = [self.repo.head.target]
        except GitError:
            ref = "HEAD"
            parents = []

        self.repo.create_commit(ref, author, committer, message, tree, parents)

    def add_commit(self, path='', message=None, author=None, committer=None):
        self.add(path)
        self.commit(message, author, committer)

if __name__ == "__main__":
    root_path = Path('.')
    repo_path = Path(root_path, 'config_backup')
    mygit = MyGit()

    # リポジトリを初期化する
    mygit.setup(repo_path)

    # ファイルを追加する
    file_path = "test.txt"
    Path(repo_path, file_path).write_text("Hello, World!")

    # git add and commit
    mygit.add_commit(file_path)

    # gita add . テスト用にファイルを追加
    test2_file_path = "test2.txt"
    Path(repo_path / test2_file_path).write_text("Add All test!")

    # git add and commit
    mygit.add_commit()



