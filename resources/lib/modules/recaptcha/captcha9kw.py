import xbmc
import json

from resources.lib.modules import client
from resources.lib.modules import control
from resources.lib.modules import utils


class captcha9KW:
    def __init__(self):
        self.ApiKey = control.setting('Captcha9kw.ApiKey')
        self.SolveType = control.setting('Captcha9kw.SolveType')

    def solve(self, url, siteKey):

        if self.ApiKey == "":
            control.infoDialog("Kein Captcha9KW APIKEY Eingetragen!")
            return

        token = ''
        post = {
            'apikey': self.ApiKey,
            'action': 'usercaptchaupload',
            'interactive': '1',
            'json': '1',
            'file-upload-01': siteKey,
            'selfsolve': '1',
            'oldsource': 'recaptchav2',
            'pageurl': url
        }

        try:
            token = ''
            data = client.request('https://www.9kw.eu/index.cgi', post=post)
            if data:
                data = utils.byteify(json.loads(data))
                if 'captchaid' in data:
                    captchaid = data['captchaid']
                    tries = 0
                    while True:
                        tries += 1
                        xbmc.sleep(1)

                        data = client.request('https://www.9kw.eu/index.cgi?apikey=' + self.ApiKey + '&action=usercaptchacorrectdata&json=1&id=' + captchaid)
                        if data:
                            data = utils.byteify(json.loads(data))
                            token = data['answer']
                            if token is not None and token != '':
                                break

        except Exception as e:
            print '9kw Error: ' + str(e)
        return token
