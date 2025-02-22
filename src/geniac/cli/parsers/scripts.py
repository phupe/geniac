#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""scripts.py: Nextflow scripts parser."""

import re
import typing
from collections import OrderedDict, defaultdict

from geniac.cli.parsers.base import GeniacParser, PathLike

__author__ = "Fabrice Allain"
__copyright__ = "Institut Curie 2021"


class NextflowScript(GeniacParser):
    """Nextflow script file parser"""

    # process flag
    PROCESS_RE = re.compile(r"^ *process +(?P<processName>\w+) *{")
    # process label
    LABEL_RE = re.compile(r"^ *label +['\"](?P<labelName>\w+)['\"] *")
    # script flag
    SCRIPT_RE = re.compile(
        r"^ *(?P<startScript>[\"']{3})"
        r"((?P<script>.+)(?<=(?P<endScript>[\"']{3})))? *$"
    )

    def _read(
        self,
        in_file: typing.Union[typing.IO, typing.BinaryIO],
        in_path: PathLike = None,
        **kwargs,
    ):
        """Load a Nextflow script file into content property

        Args:
            in_file (BinaryIO): path to nextflow script file
            encoding (str): name of the encoding use to decode config files
            in_path (PathLike): path to the input file
            flush_content (bool): flag used to flush previous content before reading
            warnings (bool): flag to turn on/off warning messages
        """
        script_flag = False
        process = ""
        # TODO: change process keys to ("processName", filePath)
        self.content["process"] = self.content.get("process") or OrderedDict()
        for idx, line in enumerate(super()._read(in_file, **kwargs)):
            if match := self.PROCESS_RE.match(line):
                values = match.groupdict()
                # If process add it to the process dict
                process = values.get("processName")
                self.content["process"][process] = defaultdict(list)
                # Save the path to the nextflow script for future logs
                self.content["process"][process]["NextflowScriptPath"] = str(in_path)
            if match := self.LABEL_RE.match(line):
                values = match.groupdict()
                label = values.get("labelName")
                self.debug("FOUND label %s in process %s.", label, process)
                self.content["process"][process]["label"].append(label)
                continue
            # For the moment we append everything into the same list even with conditional nextflow
            # script
            if match := self.SCRIPT_RE.match(line):
                values = match.groupdict()
                if process:
                    script_flag = not script_flag
                    if values.get("script"):
                        self.content["process"][process]["script"].append(line.strip())
                continue
            # Add to script part if script_flag
            if process and script_flag:
                self.debug("Add line %s to process %s scope.", idx, process)
                self.content["process"][process]["script"].append(line.strip())
                continue
