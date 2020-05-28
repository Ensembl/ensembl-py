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

import json
import os

import eHive
import requests_mock
from eHive.Process import Job

from ensembl.hive.HiveRESTClient import HiveRESTClient

in_pipe = open('hive.in', mode='rb', buffering=0)
out_pipe = open('hive.out', mode='wb', buffering=0)


class TestHiveRest(object):
    class RESTClient(HiveRESTClient):
        def __init__(self, d):
            params = self.param_defaults()
            params.update(d)
            self._BaseRunnable__params = eHive.Params.ParamContainer(params)
            self._BaseRunnable__read_pipe = in_pipe
            self._BaseRunnable__write_pipe = out_pipe
            self.__pid = os.getpid()
            self.input_job = Job()
            self.input_job.transient_error = True
            self.debug = 1

    def test_ApiCall200(self):
        with requests_mock.Mocker() as m:
            m.get("http://ensembl.local/api/", json={"data": "content"})
            # TODO ask hive Team why I can't access param_defaults in here
            rest_client = self.RESTClient({
                'endpoint': 'http://ensembl.local/api/'
            })
            # check default params are retrieved
            assert rest_client.param_is_defined('method')
            assert rest_client.param('endpoint') == 'http://ensembl.local/api/'
            rest_client.fetch_input()
            rest_client.run()
            # FIX ME reuse some mocking concept to get dataflow working in Process class for testing.
            rest_client.write_output()
            with open('hive.out', mode='r') as f:
                line1 = json.loads(f.readline())
                assert "event" in line1
                assert "content" in line1
                assert "You may do something with retrieved response {'data': 'content'}".__eq__(
                    line1['content']['message'])
                line2 = json.loads(f.readline())
                assert "rest_response" in line2['content']['output_ids']
                assert {"data": "content"}.__eq__(line2['content']['output_ids']['rest_response'])
