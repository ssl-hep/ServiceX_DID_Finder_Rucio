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
from datetime import datetime
from servicex.did_finder.rucio_adapter import RucioAdapter


class LookupRequest:
    def __init__(self, did: str,
                 rucio_adapter: RucioAdapter,
                 prefix: str = '',
                 request_id: str = 'bogus-id'):
        '''Create the `LookupRequest` object that is responsible for returning
        lists of files. Processes things in chunks.

        Args:
            did (str): The DID we are going to lookup
            rucio_adapter (RucioAdapter): Rucio lookup object
            prefix (str, optional): Prefix for xcache use. Defaults to ''.
            request_id (str, optional): ServiceX Request ID that requested this DID.
                Defaults to 'bogus-id'.
        '''
        self.did = did
        self.prefix = prefix
        self.rucio_adapter = rucio_adapter
        self.request_id = request_id

        # set logging to a null handler
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

    async def lookup_files(self):
        """
        lookup files, add cache prefix if needed.
        """
        lookup_start = datetime.now()
        all_files = self.rucio_adapter.list_files_for_did(self.did)
        lookup_finish = datetime.now()
        if not all_files:
            raise Exception(f'DID not found {self.did}')

        ds_size = 0
        total_paths = 0
        for af in all_files:
            ds_size += af['file_size']
            total_paths += len(af['file_path'])
            if self.prefix:
                af['file_path'] = [self.prefix+fp for fp in af['file_path']]
            """
            TODO: remove the following line once we are clear to return multiple
            file replica paths.
            """
            af['file_path'] = af['file_path'][0]

        self.logger.info(f"Dataset contains {len(all_files)} files. " +
                         f"Lookup took {str(lookup_finish-lookup_start)}",
                         extra={
                             'requestId': self.request_id,
                             'size': ds_size,
                             'avg_replicas': float(total_paths)/len(all_files)
                         })

        return all_files
