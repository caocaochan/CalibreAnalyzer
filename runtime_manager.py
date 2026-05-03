"""
Helpers for installing and activating the optional pkuseg runtime.

The plugin ZIP carries platform-specific runtime archives so word mode works
offline; the matching runtime is extracted into the user's Calibre config
directory on first use.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import os
import pkgutil
import platform
import shutil
import sys
import tempfile
import zipfile
from datetime import datetime, timezone

from calibre.utils.config import config_dir


PLUGIN_IMPORT_NAME = "chinese_character_analyzer"
PACKAGE_NAME = "calibre_plugins.chinese_character_analyzer"
RUNTIME_VERSION = "2026.05.03.1"

# Ready-to-import ZIP assets bundled inside the plugin package.
RUNTIME_ASSETS = {
    "windows-x86_64-py314": {
        "version": RUNTIME_VERSION,
        "filename": "pkuseg-runtime-windows-x86_64-py314.zip",
        "resource_path": "runtime_assets/pkuseg-runtime-windows-x86_64-py314.zip",
        "sha256": "f2758571603392ef14b6833d072c098ad815876442e4eb187f05b8202995d615",
        "size": 56409165,
        "packages": ["numpy==2.4.4", "pkuseg==0.0.12"],
    },
    "macos-x86_64-py314": {
        "version": RUNTIME_VERSION,
        "filename": "pkuseg-runtime-macos-x86_64-py314.zip",
        "resource_path": "runtime_assets/pkuseg-runtime-macos-x86_64-py314.zip",
        "sha256": "2fde3eae7e1a9188c9281c66a8289905b7a87c690b1613adc800361adf572f47",
        "size": 60780668,
        "packages": ["numpy==2.4.4", "pkuseg==0.0.12"],
    },
    "macos-arm64-py314": {
        "version": RUNTIME_VERSION,
        "filename": "pkuseg-runtime-macos-arm64-py314.zip",
        "resource_path": "runtime_assets/pkuseg-runtime-macos-arm64-py314.zip",
        "sha256": "ebae6d79d9cef322008dd42160195ac6447e3c9dedad8194cebf8fe64d6cd32f",
        "size": 58801229,
        "packages": ["numpy==2.4.4", "pkuseg==0.0.12"],
    },
    "linux-x86_64-py314": {
        "version": RUNTIME_VERSION,
        "filename": "pkuseg-runtime-linux-x86_64-py314.zip",
        "resource_path": "runtime_assets/pkuseg-runtime-linux-x86_64-py314.zip",
        "sha256": "98148c3095476b86f7d4429cd121327cfb4863f58d646da58f36bba28b7f62e7",
        "size": 60734021,
        "packages": ["numpy==2.4.4", "pkuseg==0.0.12"],
    },
}


class WordRuntimeError(RuntimeError):
    """Raised when the optional word-mode runtime cannot be used."""


class WordRuntimeCancelled(WordRuntimeError):
    """Raised when the user cancels runtime installation."""


class _ProgressReporter:
    """Adapter around QProgressDialog so runtime install stays responsive."""

    def __init__(self, parent=None):
        from qt.core import QApplication, QProgressDialog, Qt

        self._app = QApplication
        self._dialog = QProgressDialog(parent)
        self._dialog.setWindowTitle("Installing Word Mode")
        self._dialog.setLabelText("Preparing word segmentation runtime…")
        self._dialog.setCancelButtonText("Cancel")
        self._dialog.setAutoClose(False)
        self._dialog.setAutoReset(False)
        self._dialog.setMinimumDuration(0)
        self._dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self._dialog.setRange(0, 0)
        self._dialog.setValue(0)
        self._pump()

    def close(self):
        self._dialog.close()
        self._pump()

    def update_bytes(self, label, completed, total=None):
        self._dialog.setLabelText(label)
        if total and total > 0:
            total_kib = max(1, total // 1024)
            self._dialog.setRange(0, total_kib)
            self._dialog.setValue(min(total_kib, completed // 1024))
        else:
            self._dialog.setRange(0, 0)
        self._pump()
        self._check_cancelled()

    def update_steps(self, label, completed, total):
        self._dialog.setLabelText(label)
        self._dialog.setRange(0, max(total, 1))
        self._dialog.setValue(min(completed, total))
        self._pump()
        self._check_cancelled()

    def _check_cancelled(self):
        if self._dialog.wasCanceled():
            raise WordRuntimeCancelled("Word-mode setup was canceled.")

    def _pump(self):
        self._app.processEvents()


def current_platform_key():
    """Return the manifest key for the current Calibre runtime."""
    if sys.platform.startswith("win"):
        os_name = "windows"
    elif sys.platform == "darwin":
        os_name = "macos"
    elif sys.platform.startswith("linux"):
        os_name = "linux"
    else:
        os_name = sys.platform

    machine = platform.machine().lower()
    arch_map = {
        "amd64": "x86_64",
        "x64": "x86_64",
        "x86_64": "x86_64",
        "arm64": "arm64",
        "aarch64": "arm64",
    }
    arch = arch_map.get(machine, machine)
    py_tag = f"py{sys.version_info.major}{sys.version_info.minor}"
    return f"{os_name}-{arch}-{py_tag}"


def get_runtime_asset(platform_key=None):
    """Return the pinned asset record for a runtime key, if supported."""
    if platform_key is None:
        platform_key = current_platform_key()
    return RUNTIME_ASSETS.get(platform_key)


def get_runtime_root():
    return os.path.join(config_dir, "plugins", PLUGIN_IMPORT_NAME, "runtime")


def get_runtime_install_dir(platform_key=None):
    if platform_key is None:
        platform_key = current_platform_key()
    return os.path.join(get_runtime_root(), RUNTIME_VERSION, platform_key)


def runtime_is_installed(platform_key=None):
    """Return True if the current runtime exists and has a completion marker."""
    return os.path.isfile(_marker_path(get_runtime_install_dir(platform_key)))


def runtime_download_available(platform_key=None):
    """Return True if this build has a usable bundled runtime entry."""
    asset = get_runtime_asset(platform_key)
    return bool(asset and _manifest_ready(asset))


def ensure_word_runtime(parent=None, allow_download=False):
    """
    Ensure the optional word-mode runtime is present and importable.

    When ``allow_download`` is False, only already-installed runtimes are
    activated. The UI should pass ``allow_download=True`` after the user
    confirms the one-time setup.
    """
    platform_key = current_platform_key()
    asset = get_runtime_asset(platform_key)
    if asset is None:
        raise WordRuntimeError(
            "Word mode is not available for this Calibre runtime yet "
            f"({platform_key})."
        )

    install_dir = get_runtime_install_dir(platform_key)
    if runtime_is_installed(platform_key):
        _activate_runtime_path(install_dir)
        try:
            _validate_runtime_import(install_dir)
        except WordRuntimeError:
            if not allow_download:
                raise
            if not _manifest_ready(asset):
                raise WordRuntimeError(
                    "The installed word-mode runtime is broken, and this plugin "
                    "build does not include a replacement runtime asset yet."
                )

            reporter = _ProgressReporter(parent) if parent is not None else None
            try:
                _clear_runtime_modules(("pkuseg", "numpy"))
                shutil.rmtree(install_dir, ignore_errors=True)
                _install_runtime(asset, platform_key, install_dir, reporter)
                _activate_runtime_path(install_dir)
                _validate_runtime_import(install_dir)
            finally:
                if reporter is not None:
                    reporter.close()

        _prune_old_runtime_versions(keep_version=RUNTIME_VERSION)
        return install_dir

    if not allow_download:
        raise WordRuntimeError(
            "Word mode requires a one-time runtime install before "
            "word segmentation can be used."
        )

    if not _manifest_ready(asset):
        raise WordRuntimeError(
            "Word mode runtime assets are not configured for this build yet."
        )

    reporter = _ProgressReporter(parent) if parent is not None else None
    try:
        _install_runtime(asset, platform_key, install_dir, reporter)
        _activate_runtime_path(install_dir)
        try:
            _validate_runtime_import(install_dir)
        except WordRuntimeError:
            _clear_runtime_modules(("pkuseg", "numpy"))
            shutil.rmtree(install_dir, ignore_errors=True)
            raise
        _prune_old_runtime_versions(keep_version=RUNTIME_VERSION)
        return install_dir
    finally:
        if reporter is not None:
            reporter.close()


def _manifest_ready(asset):
    return bool(asset.get("resource_path")) and _looks_like_sha256(asset.get("sha256"))


def _looks_like_sha256(value):
    if not value or len(value) != 64:
        return False
    try:
        int(value, 16)
    except (TypeError, ValueError):
        return False
    return True


def _activate_runtime_path(install_dir):
    if not os.path.isfile(_marker_path(install_dir)):
        raise WordRuntimeError(
            "The installed word-mode runtime is incomplete. Please retry the "
            "setup."
        )
    if install_dir not in sys.path:
        sys.path.insert(0, install_dir)


def _validate_runtime_import(install_dir):
    importlib.invalidate_caches()
    try:
        importlib.import_module("pkuseg")
    except Exception as e:
        detail = type(e).__name__
        if str(e):
            detail = f"{detail}: {e}"
        raise WordRuntimeError(
            "The installed word-mode runtime could not be imported. "
            f"Please retry setup. Import failed with {detail}."
        ) from e


def _clear_runtime_modules(prefixes):
    prefixes = tuple(prefixes)
    for name in list(sys.modules):
        for prefix in prefixes:
            if name == prefix or name.startswith(f"{prefix}."):
                sys.modules.pop(name, None)
                break


def _install_runtime(asset, platform_key, install_dir, reporter=None):
    parent_dir = os.path.dirname(install_dir)
    os.makedirs(parent_dir, exist_ok=True)
    _cleanup_stale_temp_dirs(parent_dir, platform_key)

    tmp_root = tempfile.mkdtemp(prefix=f"{platform_key}-", dir=parent_dir)
    bundle_path = os.path.join(tmp_root, asset["filename"])
    staging_dir = os.path.join(tmp_root, "staging")

    try:
        _copy_bundled_asset(asset, bundle_path, reporter)
        _verify_asset_sha256(bundle_path, asset["sha256"])
        _extract_asset(bundle_path, staging_dir, reporter)
        _write_marker(staging_dir, asset, platform_key)
        if os.path.isdir(install_dir):
            shutil.rmtree(install_dir)
        os.replace(staging_dir, install_dir)
    except Exception:
        if os.path.isdir(install_dir) and not runtime_is_installed(platform_key):
            shutil.rmtree(install_dir, ignore_errors=True)
        raise
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)


def _copy_bundled_asset(asset, destination, reporter=None):
    payload = _read_bundled_asset_bytes(asset["resource_path"])
    total = len(payload)
    chunk_size = 1024 * 128
    completed = 0
    with open(destination, "wb") as fh:
        for offset in range(0, total, chunk_size):
            chunk = payload[offset: offset + chunk_size]
            fh.write(chunk)
            completed += len(chunk)
            if reporter is not None:
                reporter.update_bytes(
                    "Installing bundled word-mode runtime…",
                    completed,
                    total=total,
                )


def _read_bundled_asset_bytes(resource_path):
    try:
        resource_loader = get_resources
    except NameError:
        resource_loader = None

    if resource_loader is not None:
        data = resource_loader(resource_path)
        if data is not None:
            return data

    data = pkgutil.get_data(PACKAGE_NAME, resource_path)
    if data is not None:
        return data

    local_path = os.path.join(
        os.path.dirname(__file__),
        resource_path.replace("/", os.sep),
    )
    if os.path.isfile(local_path):
        with open(local_path, "rb") as fh:
            return fh.read()

    raise WordRuntimeError(
        "The bundled word-mode runtime asset is missing from this plugin build."
    )


def _verify_asset_sha256(path, expected_sha256):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 128), b""):
            digest.update(chunk)
    actual_sha256 = digest.hexdigest()
    if actual_sha256.lower() != expected_sha256.lower():
        raise WordRuntimeError(
            "Bundled word-mode runtime failed checksum verification. "
            "Please reinstall the plugin."
        )


def _extract_asset(bundle_path, staging_dir, reporter=None):
    os.makedirs(staging_dir, exist_ok=True)
    with zipfile.ZipFile(bundle_path) as zf:
        members = zf.infolist()
        total = len(members)
        for idx, member in enumerate(members, start=1):
            _ensure_safe_member_path(staging_dir, member.filename)
            zf.extract(member, staging_dir)
            if reporter is not None:
                reporter.update_steps(
                    "Installing word segmentation runtime…",
                    idx,
                    total,
                )


def _ensure_safe_member_path(root, member_name):
    destination = os.path.abspath(os.path.join(root, member_name))
    root = os.path.abspath(root)
    if not destination.startswith(root + os.sep) and destination != root:
        raise WordRuntimeError("Runtime archive contains an unsafe file path.")


def _write_marker(staging_dir, asset, platform_key):
    marker = {
        "installed_at": datetime.now(timezone.utc).isoformat(),
        "platform_key": platform_key,
        "runtime_version": asset["version"],
        "packages": asset.get("packages", []),
        "resource_path": asset["resource_path"],
    }
    with open(_marker_path(staging_dir), "w", encoding="utf-8") as fh:
        json.dump(marker, fh, indent=2, sort_keys=True)


def _marker_path(install_dir):
    return os.path.join(install_dir, ".runtime-install.json")


def _cleanup_stale_temp_dirs(parent_dir, platform_key):
    prefix = f"{platform_key}-"
    try:
        names = os.listdir(parent_dir)
    except OSError:
        return
    for name in names:
        if not name.startswith(prefix):
            continue
        path = os.path.join(parent_dir, name)
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)


def _prune_old_runtime_versions(keep_version):
    root = get_runtime_root()
    if not os.path.isdir(root):
        return
    for name in os.listdir(root):
        if name == keep_version:
            continue
        path = os.path.join(root, name)
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
