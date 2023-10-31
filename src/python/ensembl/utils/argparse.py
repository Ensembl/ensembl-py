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
import os
from pathlib import Path

import sqlalchemy


def _validate_src_path(parser: argparse.ArgumentParser, src_path: os.PathLike) -> Path:
    """Returns the path if exists and it is readable, raises an error through the argument parser otherwise.
    
    Args:
        parser: Argument parser.
        src_path: File or directory path to check.

    """
    src_path = Path(src_path)
    if not src_path.exists():
        parser.error(f"'{src_path}' not found")
    elif not os.access(src_path, os.R_OK):
        parser.error(f"'{src_path}' not readable")
    return src_path


def _validate_dst_path(parser: argparse.ArgumentParser, dst_path: os.PathLike) -> Path:
    """Returns the path if it is writable, raises an error through the argument parser otherwise.
    
    Args:
        parser: Argument parser.
        dst_path: File or directory path to check.

    """
    dst_path = Path(dst_path)
    if dst_path.exists() and os.access(dst_path, os.W_OK):
        return dst_path
    for parent_path in dst_path.parents:
        if parent_path.exists() and not os.access(parent_path, os.W_OK):
            parser.error(f"'{dst_path}' is not writable")
    return dst_path


class ArgumentParser(argparse.ArgumentParser):
    """Extends :class:`argparse.ArgumentParser` with additional methods and functionality.
    
    The default behaviour of the help text will be to display the default values on every non-required
    argument, i.e. optional arguments with "required=False".

    """

    def __init__(self, *args, **kwargs) -> None:
        """Extends the base class to include the information about default argument values by default."""
        super().__init__(*args, **kwargs)
        self.formatter_class = argparse.ArgumentDefaultsHelpFormatter

    def add_argument(self, *args, **kwargs) -> None:
        """Extends the parent function by excluding the default value in the help text when not provided.
        
        Only applied to required arguments without a default value, i.e. positional arguments or optional
        arguments with "required=True".

        """
        if kwargs.get("required", False) and "default" not in kwargs:
            kwargs["default"] = argparse.SUPPRESS
        super().add_argument(*args, **kwargs)

    def add_argument_src_path(self, *args, **kwargs) -> None:
        """Adds :class:`pathlib.Path` argument, checking if it exists and it is readable at parsing time.

        If "metavar" is not defined it is added with "PATH" as value to improve help text readability.

        """
        if "metavar" not in kwargs:
            kwargs["metavar"] = "PATH"
        kwargs.pop("type", None)
        self.add_argument(*args, **kwargs, type=lambda x: _validate_src_path(self, x))

    def add_argument_dst_path(self, *args, **kwargs) -> None:
        """Adds :class:`pathlib.Path` argument, checking if it is writable at parsing time.

        If "metavar" is not defined it is added with "PATH" as value to improve help text readability.

        """
        if "metavar" not in kwargs:
            kwargs["metavar"] = "PATH"
        kwargs.pop("type", None)
        self.add_argument(*args, **kwargs, type=lambda x: _validate_dst_path(self, x))

    def add_argument_url(self, *args, **kwargs) -> None:
        """Adds :class:`sqlalchemy.engine.URL` argument.

        If "metavar" is not defined it is added with "URI" as value to improve help text readability.

        """
        if "metavar" not in kwargs:
            kwargs["metavar"] = "URI"
        kwargs.pop("type", None)
        self.add_argument(*args, **kwargs, type=lambda x: sqlalchemy.engine.make_url(x))

    def add_server_arguments(self, prefix: str = "") -> None:
        """Adds the usual set of arguments needed to connect to a server.
        
        This means: "--host", "--port", "--user" and "--password" (optional).

        Args:
            prefix: Prefix to add the each argument, e.g. if prefix is "src_", the arguments will be
                "--src_host", etc.

        """
        self.add_argument(f"--{prefix}host", required=True, help="Name of the host")
        self.add_argument(f"--{prefix}port", required=True, type=int, help="Port number")
        self.add_argument(f"--{prefix}user", required=True, help="User name")
        self.add_argument(f"--{prefix}password", metavar="PWD", default="", help="Host password")

    def add_database_arguments(self, prefix: str = "") -> None:
        """Adds the usual set of arguments needed to connect to a database.
        
        This means: "--host", "--port", "--user", "--password" (optional) and "--database".

        Args:
            prefix: Prefix to add the each argument, e.g. if prefix is "src_", the arguments will be
                "--src_host", etc.

        """
        self.add_server_arguments(prefix=prefix)
        self.add_argument(f"--{prefix}database", required=True, metavar="NAME", help="Database name")
