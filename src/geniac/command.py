#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Foobar.py: Description of what foobar does."""

import logging
from abc import ABC, abstractmethod
from configparser import ConfigParser, ExtendedInterpolation
from os import getcwd
from os.path import isdir, isfile

from pkg_resources import resource_stream

__author__ = "Fabrice Allain"
__copyright__ = "Institut Curie 2020"

_logger = logging.getLogger(__name__)


class GCommand(ABC):
    """Abstract base class for Geniac commands"""

    default_config = "conf/geniac.ini"

    def __init__(self, project_dir=None, config_file=None):
        """

        Args:
            project_dir (str): path to the Nextflow Project Dir
            config_file (str): path to a configuration file (INI format)
        """
        self.project_dir = project_dir
        self.config_file = config_file
        self.config = self.load_config(self.config_file)

    def load_config(self, config_file=None):
        """Load default configuration file and update option with config_file

        Returns:
            :obj:`configparser.ConfigParser`: config instance
        """
        config = ConfigParser(
            interpolation=ExtendedInterpolation(), allow_no_value=True
        )
        # TODO: add defauldict in order to init tree. sections with required, path,
        #  files, opt_files and exclude keys
        # TODO: remove has_section checks in GCheck after previous todo
        # Read default config file
        config.read_string(
            resource_stream(__name__, self.default_config).read().decode()
        )
        if config_file:
            # Read configuration file
            config.read(config_file)
        return config

    @property
    def project_dir(self):
        """Project Dir path property

        Returns:

        """
        return self._project_dir

    @project_dir.setter
    def project_dir(self, value):
        """If value is not a directory, set the project dir to the current directory"""
        self._project_dir = value if value and isdir(value) else getcwd()

    @property
    def config_file(self):
        """Configuration file (optional)

        Returns:

        """
        return self._config_file

    @config_file.setter
    def config_file(self, value):
        """"""
        self._config_file = value if value and isfile(value) else None

    @property
    def config(self):
        """ConfigParser property

        Returns:
            :obj:`configparser.ConfigParser`: config instance
        """
        return self._config

    @config.setter
    def config(self, value):
        """Update base dir with project dir"""
        value.set("tree.base", "path", self.project_dir)
        self._config = value

    @abstractmethod
    def run(self):
        """Main entry point for every geniac sub command"""
        pass
