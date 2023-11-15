# See the NOTICE file distributed with this work for additional information
# regarding copyright ownership.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Provide an extended version of :class:`argparse.ArgumentParser` with additional functionality."""

__all__ = ["ArgumentParser"]

import argparse
import logging
import os
from pathlib import Path

from sqlalchemy.engine import make_url, URL


class ArgumentParser(argparse.ArgumentParser):
    """Extends :class:`argparse.ArgumentParser` with additional methods and functionality.

    The default behaviour of the help text will be to display the default values on every non-required
    argument, i.e. optional arguments with "required=False".

    """

    def __init__(self, *args, **kwargs) -> None:
        """Extends the base class to include the information about default argument values by default."""
        kwargs.setdefault("argument_default", argparse.SUPPRESS)
        super().__init__(*args, **kwargs)
        self.formatter_class = argparse.ArgumentDefaultsHelpFormatter
        self.__server_groups = []

    def _validate_src_path(self, src_path: os.PathLike) -> Path:
        """Returns the path if exists and it is readable, raises an error through the parser otherwise.

        Args:
            src_path: File or directory path to check.

        """
        src_path = Path(src_path)
        if not src_path.exists():
            self.error(f"'{src_path}' not found")
        elif not os.access(src_path, os.R_OK):
            self.error(f"'{src_path}' not readable")
        return src_path

    def _validate_dst_path(self, dst_path: os.PathLike, exists_ok: bool) -> Path:
        """Returns the path if it is writable, raises an error through the parser otherwise.

        Args:
            dst_path: File or directory path to check.
            exists_ok: Do not raise an error if the destination path already exists.

        """
        dst_path = Path(dst_path)
        if dst_path.exists():
            if os.access(dst_path, os.W_OK):
                if exists_ok:
                    return dst_path
                else:
                    self.error(f"'{dst_path}' already exists")
            else:
                self.error(f"'{dst_path}' is not writable")
        for parent_path in dst_path.parents:
            if parent_path.exists() and not os.access(parent_path, os.W_OK):
                self.error(f"'{dst_path}' is not writable")
        return dst_path

    def add_argument_src_path(self, *args, **kwargs) -> None:
        """Adds :class:`pathlib.Path` argument, checking if it exists and it is readable at parsing time.

        If "metavar" is not defined it is added with "PATH" as value to improve help text readability.

        """
        kwargs.setdefault("metavar", "PATH")
        kwargs["type"] = lambda x: self._validate_src_path(x)
        self.add_argument(*args, **kwargs)

    def add_argument_dst_path(self, *args, exists_ok: bool = True, **kwargs) -> None:
        """Adds :class:`pathlib.Path` argument, checking if it is writable at parsing time.

        If "metavar" is not defined it is added with "PATH" as value to improve help text readability.

        Args:
            exists_ok: Do not raise an error if the destination path already exists.

        """
        kwargs.setdefault("metavar", "PATH")
        kwargs["type"] = lambda x: self._validate_dst_path(x, exists_ok)
        self.add_argument(*args, **kwargs)

    def add_argument_url(self, *args, **kwargs) -> None:
        """Adds :class:`sqlalchemy.engine.URL` argument.

        If "metavar" is not defined it is added with "URI" as value to improve help text readability.

        """
        kwargs.setdefault("metavar", "URI")
        kwargs["type"] = lambda x: make_url(x)
        self.add_argument(*args, **kwargs)

    def add_server_arguments(self, prefix: str = "", include_database: bool = False, help: str = "") -> None:
        """Adds the usual set of arguments needed to connect to a server.

        This means: "--host", "--port", "--user" and "--password" (optional).

        Args:
            prefix: Prefix to add the each argument, e.g. if prefix is "src_", the arguments will be
                "--src_host", etc.
            include_database: Include "--database" argument.
            help: Description message to include for this set of arguments.

        """
        group = self.add_argument_group(f"{prefix}server connection arguments", description=help)
        group.add_argument(f"--{prefix}host", required=True, metavar="HOST", help="host name")
        group.add_argument(f"--{prefix}port", required=True, type=int, metavar="PORT", help="port number")
        group.add_argument(f"--{prefix}user", required=True, metavar="USER", help="user name")
        group.add_argument(f"--{prefix}password", metavar="PWD", help="host password")
        if include_database:
            group.add_argument(f"--{prefix}database", required=True, metavar="NAME", help="database name")
        self.__server_groups.append(prefix)

    def add_log_arguments(self, add_log_file: bool = False) -> None:
        """Adds the usual set of arguments required to set and initialise a logging system.

        The current set includes a mutually exclusive group for the default logging level: "--verbose",
        "--debug" or "--log LEVEL".

        Args:
            add_log_file: Add arguments to allow storing messages into a file, i.e. "--log_file" and
                "--log_file_level".

        """
        # Define the list of log levels available
        log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        # NOTE: from 3.11 this list can be changed to: logging.getLevelNamesMapping().keys()
        # Create logging arguments group
        group = self.add_argument_group("logging arguments")
        # Add 3 mutually exclusive options to set the logging level
        subgroup = group.add_mutually_exclusive_group()
        subgroup.add_argument(
            "-v",
            "--verbose",
            action="store_const",
            const="INFO",
            dest="log_level",
            help="verbose mode, i.e. 'INFO' log level",
        )
        subgroup.add_argument(
            "--debug",
            action="store_const",
            const="DEBUG",
            dest="log_level",
            help="debugging mode, i.e. 'DEBUG' log level",
        )
        subgroup.add_argument(
            "--log",
            choices=log_levels,
            type=str.upper,
            default="WARNING",
            metavar="LEVEL",
            dest="log_level",
            help="level of the events to track: %(choices)s",
        )
        if add_log_file:
            # Add log file-related arguments
            group.add_argument(
                "--log_file",
                type=lambda x: self._validate_dst_path(x, exists_ok=True),
                metavar="PATH",
                default=None,
                help="log file path",
            )
            group.add_argument(
                "--log_file_level",
                choices=log_levels,
                type=str.upper,
                default="DEBUG",
                metavar="LEVEL",
                help="level of the events to track in the log file: %(choices)s",
            )

    def parse_args(self, *args, **kwargs) -> argparse.Namespace:
        """Extends the parent function by adding a new URL argument for every server group added.

        The type of this new argument will be :class:`sqlalchemy.engine.URL`. It also logs all the parsed
        arguments for debugging purposes when logging arguments have been added.

        """
        args = super().parse_args(*args, **kwargs)
        # Build and add an sqlalchemy.engine.URL object for every server group added
        for prefix in self.__server_groups:
            # Raise an error rather than overwriting when the URL argument is already present
            if f"{prefix}url" in args:
                self.error(f"argument '{prefix}url' is already present")
            server_url = URL.create(
                "mysql",
                getattr(args, f"{prefix}user"),
                getattr(args, f"{prefix}password"),
                getattr(args, f"{prefix}host"),
                getattr(args, f"{prefix}port"),
                getattr(args, f"{prefix}database", None),
            )
            setattr(args, f"{prefix}url", server_url)
        return args
