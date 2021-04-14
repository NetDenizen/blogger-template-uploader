# Modified from: https://github.com/gilesknap/gphotos-sync/blob/master/gphotos/authorize.py
# The MIT License (MIT)
#
# Original Work Copyright (c) 2015 Yann Rouillard
# Modified Work Copyright (c) 2019 NetDenizen
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from pathlib import Path
from urllib3.util.retry import Retry
from typing import List, Optional
from json import load, dump, JSONDecodeError

from requests.adapters import HTTPAdapter
from requests_oauthlib import OAuth2Session

from blogger_template_uploder.lib.services.gphotos.common import GphotosError

class GphotosAuthorizeError(GphotosError):
	pass

# OAuth endpoints given in the Google API documentation
authorization_base_url = "https://accounts.google.com/o/oauth2/v2/auth"
token_uri = "https://www.googleapis.com/oauth2/v4/token"

class Authorize:
    def __init__(
            self, scope: List[str], token_file: Path,
            secrets_file: Path, max_retries: int = 5
    ):
        """ A very simple class to handle Google API authorization flow
        for the requests library. Includes saving the token and automatic
        token refresh.

        Args:
            scope: list of the scopes for which permission will be granted
            token_file: full path of a file in which the user token will be
            placed. After first use the previous token will also be read in from
            this file
            secrets_file: full path of the client secrets file obtained from
            Google Api Console
        """
        self.max_retries = max_retries
        self.scope: List[str] = scope
        self.token_file: Path = token_file
        self.session = None
        self.token = None
        try:
            with secrets_file.open('r') as stream:
                all_json = load(stream)
            secrets = all_json['installed']
            self.client_id = secrets['client_id']
            self.client_secret = secrets['client_secret']
            self.redirect_uri = secrets['redirect_uris'][0]
            self.token_uri = secrets['token_uri']
            self.extra = {
                'client_id': self.client_id,
                'client_secret': self.client_secret}

        except (JSONDecodeError, IOError):
            GphotosAuthorizeError( ''.join( ( 'Missing or bad secrets file: "', secrets_file, '"' ) )

    def load_token(self) -> Optional[str]:
        try:
            with self.token_file.open('r') as stream:
                token = load(stream)
        except (JSONDecodeError, IOError):
            return None
        return token

    def save_token(self, token: str):
        with self.token_file.open('w') as stream:
            dump(token, stream)
        self.token_file.chmod(0o600)

    def authorize(self):
        """ Initiates OAuth2 authentication and authorization flow
        """
        token = self.load_token()

        if token:
            self.session = OAuth2Session(self.client_id, token=token,
                                         auto_refresh_url=self.token_uri,
                                         auto_refresh_kwargs=self.extra,
                                         token_updater=self.save_token)

        # note we want retries on POST as well, need to review this once we
        # start to do methods that write to Google Photos
        retries = Retry(total=self.max_retries,
                        backoff_factor=0.1,
                        status_forcelist=[500, 502, 503, 504],
                        method_whitelist=frozenset(['GET', 'POST']),
                        raise_on_status=False)
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
