import importlib.metadata
from dataclasses import dataclass
from typing import Optional

import requests

from showmereqs.utils import get_mapping

# pypi_api = "https://pypi.org/pypi"


@dataclass
class PackageInfo:
    """a class to get package info, including package name, version, etc."""

    import_name: str
    pypi_server: str = "https://pypi.org/pypi"
    version: Optional[str] = None
    package_name: Optional[str] = None

    def __post_init__(self):
        self.package_name = self._get_package_name_from_mapping()

        self.version = self._get_local_version()

        if self.package_name is None:
            json_info = self._get_pypi_json(self.import_name, self.pypi_server)
            if json_info is not None:
                self.package_name = json_info["info"]["name"]

    def __str__(self):
        return f"<PackageInfo> {{\nimport_name: {self.import_name}\nversion: {self.version}\npackage_name: {self.package_name}\n}}"

    def format_row(self):
        """format the package info into a row"""
        return (
            self.version is not None,
            self.package_name is not None,
            self.format_version_info(),
            self.format_import_info(),
        )

    def format_version_info(
        self,
        eq_sign: str = "==",
    ):
        if self.version is None:
            return f"{self.package_name}"
        version_txt = f"{self.package_name}{eq_sign}{self.version}"
        return f"{version_txt}"

    def format_import_info(self):
        if self.package_name == self.import_name:
            return ""
        return f"# {self.import_name}"

    def _get_local_version(self):
        try:
            version = importlib.metadata.version(self.import_name)
            return version
        except importlib.metadata.PackageNotFoundError:
            if self.package_name is not None:
                version = importlib.metadata.version(self.package_name)
                return version
            return None

    def _get_package_name_from_mapping(self, special_mapping: dict[str, str] = None):
        if special_mapping is None:
            special_mapping = get_mapping()
        if self.import_name in special_mapping:
            return special_mapping[self.import_name]
        return None

    def _get_pypi_json(self, package_name: str, pypi_api: str):
        api = f"{pypi_api}/{package_name}/json"
        try:
            response = requests.get(api, timeout=2)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            print(f"Warning: Error checking {package_name} on {pypi_api}: {e}")
