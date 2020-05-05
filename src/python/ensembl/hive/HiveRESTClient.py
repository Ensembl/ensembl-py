"""
.. See the NOTICE file distributed with this work for additional information
   regarding copyright ownership.
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
import logging

import eHive
import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

logger = logging.getLogger(__name__)


class HiveRESTClient(eHive.BaseRunnable):
    """
    Basic Root class to interact with random REST api in a Hive Pipeline.
    Allow random call to an API from a Ensembl-Hive Pipeline config file
    TODO: Authentication, Secured, Files upload.

    """
    available_method = ('post', 'get', 'put', 'patch')

    def param_defaults(self):
        return {
            'endpoint': 'http://localhost/api/endpoint',
            'payload': {},
            'headers': None,
            'files': None,
            'method': 'get',
            'timeout': 1,
            'retry': 3,
            'status_retry': Retry.RETRY_AFTER_STATUS_CODES,
            'method_retry': Retry.DEFAULT_METHOD_WHITELIST
        }

    def __init__(self, read_fileno, write_fileno, debug):
        super(HiveRESTClient, self).__init__(read_fileno, write_fileno, debug)
        retry_strategy = Retry(
            total=self.param('retry'),
            status_forcelist=self.param('status_retry'),
            method_whitelist=self.param('method_retry')
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.http = requests.Session()
        self.http.mount("https://", adapter)
        self.http.mount("http://", adapter)

    def run(self):
        """
        Basic call to request parameters specified in pipeline parameters
        Return response received.
        """
        try:
            response = self.http.request(method=self.param('method'),
                                         url=self.param('endpoint'),
                                         headers=self.param('headers'),
                                         files=self.param('files'),
                                         data=self.param('payload'),
                                         timeout=self.param('timeout'))
            self.process_response(response)
            return response
        except requests.HTTPError as e:
            message = "Error performing request {}: {}".format(self.param('endpoint'), e.strerror)
            logger.error(message)
            self.warning(message)

    def process_response(self, response):
        """
        Added code to process the response received from api call.
        This is the only required override needed.
        """
        self.dataflow( { 'result': response.json() }, 1)
