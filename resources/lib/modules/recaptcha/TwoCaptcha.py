import xbmc
import json

from resources.lib.modules import client
from resources.lib.modules import control
from resources.lib.modules import utils


class TwoCaptcha:
    def __init__(self):
        self.ApiKey = control.setting('2Captcha.ApiKey')
        self.IsAlive = True
        self.time = int(control.setting('Recaptcha2.TimeOut'))

    def solve(self, url, siteKey):
        if self.ApiKey == "":
            control.infoDialog("Kein 2Captcha APIKEY Eingetragen!")
            return

        token = ''
        post = {
            'key': self.ApiKey,
            'method': 'userrecaptcha',
            'invisible': '1',
            'json': '1',
            'googlekey': siteKey,
            'pageurl': url
        }

        try:
            token = ''
            data = client.request('https://2captcha.com/in.php', post=post)
            if data:
                data = utils.byteify(json.loads(data))
                if 'status' in data and data['status'] == 1:
                    captchaid = data['request']
                    tries = 0
                    while tries < self.time and self.IsAlive:
                        tries += 1
                        xbmc.sleep(1000)

                        data = client.request('https://2captcha.com/res.php?key=' + self.ApiKey + '&action=get&json=1&id=' + captchaid)
                        if data:
                            print str(data)
                            data = utils.byteify(json.loads(data))
                            if data['status'] == 1 and data['request'] != '':
                                token = data['request']
                                break

        except Exception as e:
            print '2Captcha Error: ' + str(e)
        return token

    def setKill(self):
        self.IsAlive = False