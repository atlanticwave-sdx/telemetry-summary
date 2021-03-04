# -*- coding: utf-8 -*-
import pytest

from src.setup.setting import Setting


class TestSettingClass(object):

    def test_setting_up(self):
        setting = Setting(ini_file='config_test.ini')
        assert setting.ini_file == 'config_test.ini'

    def test_setting_up_db(self):
        setting = Setting(ini_file='config_test.ini')
        setting.read_params()
        assert 'l2vpn_bra_usa_11242' in setting.topology['amlight_sdx_1']

    def test_read_params(self):
        setting = Setting(ini_file='config_test.ini')
        setting.read_params()
        assert setting.verbose_status is True

    def test_read_params_open_fail(self):
        setting = Setting(ini_file='config_test_fail.ini')
        with pytest.raises(Exception) as excinfo:
            setting.read_params()
        assert str(excinfo.typename) == "FileNotFoundError"

    def test_read_params_wrong_structure(self):
        setting = Setting(ini_file='config_test_fails.ini')
        with pytest.raises(Exception) as excinfo:
            setting.read_params()
        assert str(excinfo.typename) == "KeyError"

    def test_read_params_wrong_structure_db(self):
        setting = Setting(ini_file='config_test_fails_db.ini')
        with pytest.raises(Exception) as excinfo:
            setting.read_params()
        assert str(excinfo.typename) == "AttributeError"
