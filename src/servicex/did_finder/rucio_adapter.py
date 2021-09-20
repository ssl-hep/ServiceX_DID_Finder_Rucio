# Copyright (c) 2019, IRIS-HEP
# Copyright (c) 2019, IRIS-HEP
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import logging
import xmltodict

from rucio.common.exception import DataIdentifierNotFound


class RucioAdapter:
    def __init__(self, replica_client):
        self.replica_client = replica_client

        # set logging to a null handler
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

    @staticmethod
    def parse_did(did):
        """
        Parse a DID string into the scope and name
        Allow for no scope to be included
        :param did:
        :return: Dictionary with keys "scope" and "name"
        """
        d = dict()
        if ':' in did:
            d['scope'], d['name'] = did.split(":")
        else:
            d['scope'], d['name'] = '', did
        return d

    @staticmethod
    def get_paths(replicas):
        """
        extracts all the replica paths in a list sorted according
        to their priorities.
        """
        paths = [None] * len(replicas)
        for replica in replicas:
            paths[int(replica['@priority'], 10)-1] = replica['#text']
        return paths

    def list_files_for_did(self, did):
        """
        from rucio, gets list of file replicas in metalink xml,
        parses it, and returns a sorted list of all possible paths,
        together with checksum and filesize.
        """
        parsed_did = self.parse_did(did)
        try:
            reps = self.replica_client.list_replicas(
                [{'scope': parsed_did['scope'], 'name': parsed_did['name']}],
                schemes=['root'],
                metalink=True,
                sort='geoip'
            )
            g_files = []
            d = xmltodict.parse(reps)
            for f in d['metalink']['file']:
                g_files.append(
                    {
                        'adler32': f['hash']['#text'],
                        'file_size': int(f['size'], 10),
                        'file_events': 0,
                        'file_path': self.get_paths(f['url'])
                    }
                )
            return g_files
        except DataIdentifierNotFound:
            self.logger.warning(f"{did} not found")
            return None
