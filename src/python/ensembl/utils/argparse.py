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


def _validate_dst_path(parser: argparse.ArgumentParser, dst_path: os.PathLike, exists_ok: bool) -> Path:
    """Returns the path if it is writable, raises an error through the argument parser otherwise.

    Args:
        parser: Argument parser.
        dst_path: File or directory path to check.
        exists_ok: Do not raise an error if the destination path already exists.

    """
    dst_path = Path(dst_path)
    if dst_path.exists():
        if os.access(dst_path, os.W_OK):
            if exists_ok:
                return dst_path
            else:
                parser.error(f"'{dst_path}' already exists")
        else:
            parser.error(f"'{dst_path}' is not writable")
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
        self.__server_groups = []

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

    def add_argument_dst_path(self, *args, exists_ok: bool = True, **kwargs) -> None:
        """Adds :class:`pathlib.Path` argument, checking if it is writable at parsing time.

        If "metavar" is not defined it is added with "PATH" as value to improve help text readability.

        Args:
            exists_ok: Do not raise an error if the destination path already exists.

        """
        if "metavar" not in kwargs:
            kwargs["metavar"] = "PATH"
        kwargs.pop("type", None)
        self.add_argument(*args, **kwargs, type=lambda x: _validate_dst_path(self, x, exists_ok))

    def add_argument_url(self, *args, **kwargs) -> None:
        """Adds :class:`sqlalchemy.engine.URL` argument.

        If "metavar" is not defined it is added with "URI" as value to improve help text readability.

        """
        if "metavar" not in kwargs:
            kwargs["metavar"] = "URI"
        kwargs.pop("type", None)
        self.add_argument(*args, **kwargs, type=lambda x: make_url(x))

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
        group.add_argument(
            f"--{prefix}host", required=True, default=argparse.SUPPRESS, metavar="HOST", help="Host name"
        )
        group.add_argument(
            f"--{prefix}port",
            required=True,
            type=int,
            default=argparse.SUPPRESS,
            metavar="PORT",
            help="Port number",
        )
        group.add_argument(
            f"--{prefix}user", required=True, default=argparse.SUPPRESS, metavar="USER", help="User name"
        )
        group.add_argument(f"--{prefix}password", metavar="PWD", help="Host password")
        if include_database:
            group.add_argument(
                f"--{prefix}database",
                required=True,
                default=argparse.SUPPRESS,
                metavar="NAME",
                help="Database name",
            )
        self.__server_groups.append(prefix)

    def parse_args(self, *args, **kwargs) -> argparse.Namespace:
        """Extends the parent function by adding a new URL argument for every server group added.

        The type of this new argument will be :class:`sqlalchemy.engine.URL`. It also logs all the parsed
        arguments for debugging purposes.

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
        # Log the parsed arguments for debugging purposes
        logging.debug(f"{self.prog} called with the following arguments:")
        for x in sorted(vars(args)):
            logging.debug("  --%s %s", x, getattr(args, x))
        return args
