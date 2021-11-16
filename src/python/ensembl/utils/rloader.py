# See the NOTICE file distributed with this work for additional information
#   regarding copyright ownership.
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#       http://www.apache.org/licenses/LICENSE-2.0
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
Allow to seamlessly load / read the content of a remote file as if it was located locally.

@author: Marc Chakiachvili

"""
import configparser
import json
import logging
from io import StringIO

import dotenv
import requests
import requests.exceptions as exc
import yaml

# Add exception processing
# File does not exists.
# Return as dict ?
# Add Loading parser ?
logger = logging.getLogger(__name__)


class RemoteFileLoader(object):
    format = ('yaml', 'ini', 'env', 'json')

    def __init__(self, parser=None) -> None:
        super().__init__()
        self.format = parser

    def __parse(self, content):
        if self.format == 'yaml':
            return yaml.load(content, yaml.SafeLoader)
        elif self.format == 'ini':
            config = configparser.ConfigParser()
            try:
                config.read_string(content)
            except configparser.MissingSectionHeaderError:
                content = StringIO("[top]\n" + content).read()
                config.read_string(content)
            return config
        elif self.format == 'env':
            return dotenv.dotenv_values(stream=StringIO(content))
        elif self.format == 'json':
            return json.loads(content)
        else:
            # only return content, no parsing
            return content

    def r_open(self, url):
        try:
            r = requests.get(url)
            if r.status_code == 200:
                return self.__parse(r.text)
            else:
                raise exc.HTTPError("Non 200 response received: %s (%s)" % (r.status_code, r.reason))
        except exc.HTTPError as ex:
            logger.exception("Error with request to %s: %s", url, ex)
        except exc.Timeout as ex:
            logger.exception("Request timed out %s: %s", url, ex)
        return None
