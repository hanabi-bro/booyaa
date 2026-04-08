from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class ProgressParams:
    code: int = -999
    msg: str = ''
    output: str | bytes | dict | dict[str, Any] | list[Any] = ''
    result: str = ''

@dataclass
class Login(ProgressParams):
    """"""

@dataclass
class Backup(ProgressParams):
    """"""

@dataclass
class Logout(ProgressParams):
    """"""

@dataclass
class Progress:
    login: Login = field(default_factory=Login)
    backup: Backup = field(default_factory=Backup)
    logout: Logout = field(default_factory=Logout)
    msg: str = ''
