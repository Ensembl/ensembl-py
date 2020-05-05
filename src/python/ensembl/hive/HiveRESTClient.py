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
import contextlib
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
        super().__init__(read_fileno, write_fileno, debug)
        self.retry_strategy = Retry(
            total=self.param('retry'),
            status_forcelist=self.param('status_retry'),
            method_whitelist=self.param('method_retry')
        )

    @contextlib.contextmanager
    def session_scope(self):
        """ Ensure HTTP session is closed after processing code"""
        session = self.open_session()
        logger.debug("HTTP Session opened %s", session)
        try:
            yield session
        except requests.HTTPError as e:
            logger.exception("Error initialising session")
        finally:
            logger.debug("Closing session")
            session.close()

    def run(self):
        """
        Basic call to request parameters specified in pipeline parameters
        Return response received.
        """
        with self.session_scope() as http:
            try:
                response = http.request(method=self.param('method'),
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
        self.dataflow({'result': response.json()}, 1)

    def open_session(self):
        adapter = HTTPAdapter(max_retries=self.retry_strategy)
        http = requests.Session()
        http.mount("https://", adapter)
        http.mount("http://", adapter)
        return http

    def close_session(self, session):
        session.close()
