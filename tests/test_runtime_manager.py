import importlib
import pathlib
import sys
import tempfile
import types
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_runtime_manager():
    config_module = types.ModuleType("calibre.utils.config")
    config_module.config_dir = tempfile.gettempdir()

    utils_module = types.ModuleType("calibre.utils")
    utils_module.config = config_module

    calibre_module = types.ModuleType("calibre")
    calibre_module.utils = utils_module

    sys.modules["calibre"] = calibre_module
    sys.modules["calibre.utils"] = utils_module
    sys.modules["calibre.utils.config"] = config_module

    sys.modules.pop("runtime_manager", None)
    return importlib.import_module("runtime_manager")


class RuntimeManagerTests(unittest.TestCase):
    def setUp(self):
        self.runtime_manager = load_runtime_manager()

    def tearDown(self):
        for name in list(sys.modules):
            if name == "runtime_manager" or name.startswith("runtime_manager."):
                sys.modules.pop(name, None)

    def test_validate_runtime_import_surfaces_root_cause(self):
        with mock.patch.object(
            self.runtime_manager.importlib,
            "import_module",
            side_effect=ImportError("dlopen failed: missing symbol"),
        ):
            with self.assertRaises(self.runtime_manager.WordRuntimeError) as ctx:
                self.runtime_manager._validate_runtime_import("/tmp/fake-runtime")

        self.assertIn("ImportError: dlopen failed: missing symbol", str(ctx.exception))

    def test_ensure_word_runtime_reinstalls_broken_runtime_when_allowed(self):
        platform_key = "macos-arm64-py314"
        asset = self.runtime_manager.get_runtime_asset(platform_key)
        install_dir = "/tmp/fake-runtime"

        with mock.patch.object(
            self.runtime_manager, "current_platform_key", return_value=platform_key
        ), mock.patch.object(
            self.runtime_manager, "get_runtime_install_dir", return_value=install_dir
        ), mock.patch.object(
            self.runtime_manager, "runtime_is_installed", return_value=True
        ), mock.patch.object(
            self.runtime_manager, "_activate_runtime_path"
        ), mock.patch.object(
            self.runtime_manager,
            "_validate_runtime_import",
            side_effect=[
                self.runtime_manager.WordRuntimeError("broken runtime"),
                None,
            ],
        ), mock.patch.object(
            self.runtime_manager, "_manifest_ready", return_value=True
        ), mock.patch.object(
            self.runtime_manager, "_install_runtime"
        ) as install_runtime, mock.patch.object(
            self.runtime_manager, "_clear_runtime_modules"
        ) as clear_runtime_modules, mock.patch.object(
            self.runtime_manager.shutil, "rmtree"
        ) as rmtree, mock.patch.object(
            self.runtime_manager, "_prune_old_runtime_versions"
        ) as prune_versions:
            result = self.runtime_manager.ensure_word_runtime(
                parent=None,
                allow_download=True,
            )

        self.assertEqual(result, install_dir)
        clear_runtime_modules.assert_called_once_with(("pkuseg", "numpy"))
        rmtree.assert_called_once_with(install_dir, ignore_errors=True)
        install_runtime.assert_called_once_with(asset, platform_key, install_dir, None)
        prune_versions.assert_called_once_with(
            keep_version=self.runtime_manager.RUNTIME_VERSION
        )

    def test_ensure_word_runtime_does_not_reinstall_without_permission(self):
        platform_key = "macos-arm64-py314"
        install_dir = "/tmp/fake-runtime"

        with mock.patch.object(
            self.runtime_manager, "current_platform_key", return_value=platform_key
        ), mock.patch.object(
            self.runtime_manager, "get_runtime_install_dir", return_value=install_dir
        ), mock.patch.object(
            self.runtime_manager, "runtime_is_installed", return_value=True
        ), mock.patch.object(
            self.runtime_manager, "_activate_runtime_path"
        ), mock.patch.object(
            self.runtime_manager,
            "_validate_runtime_import",
            side_effect=self.runtime_manager.WordRuntimeError("broken runtime"),
        ), mock.patch.object(
            self.runtime_manager, "_install_runtime"
        ) as install_runtime:
            with self.assertRaises(self.runtime_manager.WordRuntimeError):
                self.runtime_manager.ensure_word_runtime(
                    parent=None,
                    allow_download=False,
                )

        install_runtime.assert_not_called()

    def test_fresh_install_cleans_up_if_runtime_still_cannot_import(self):
        platform_key = "macos-arm64-py314"
        asset = self.runtime_manager.get_runtime_asset(platform_key)
        install_dir = "/tmp/fake-runtime"

        with mock.patch.object(
            self.runtime_manager, "current_platform_key", return_value=platform_key
        ), mock.patch.object(
            self.runtime_manager, "get_runtime_install_dir", return_value=install_dir
        ), mock.patch.object(
            self.runtime_manager, "runtime_is_installed", return_value=False
        ), mock.patch.object(
            self.runtime_manager, "_manifest_ready", return_value=True
        ), mock.patch.object(
            self.runtime_manager, "_install_runtime"
        ) as install_runtime, mock.patch.object(
            self.runtime_manager, "_activate_runtime_path"
        ), mock.patch.object(
            self.runtime_manager,
            "_validate_runtime_import",
            side_effect=self.runtime_manager.WordRuntimeError("still broken"),
        ), mock.patch.object(
            self.runtime_manager, "_clear_runtime_modules"
        ) as clear_runtime_modules, mock.patch.object(
            self.runtime_manager.shutil, "rmtree"
        ) as rmtree:
            with self.assertRaises(self.runtime_manager.WordRuntimeError):
                self.runtime_manager.ensure_word_runtime(
                    parent=None,
                    allow_download=True,
                )

        install_runtime.assert_called_once_with(asset, platform_key, install_dir, None)
        clear_runtime_modules.assert_called_once_with(("pkuseg", "numpy"))
        rmtree.assert_called_once_with(install_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
