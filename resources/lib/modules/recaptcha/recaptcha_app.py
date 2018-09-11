import threading

import xbmc
import xbmcgui
from resources.lib.modules import control

from resources.lib.modules.recaptcha import myJDownloader
from resources.lib.modules.recaptcha import captcha9kw


class recaptchaApp:
    def __init__(self):
        self.siteKey = ""
        self.url = ""
        self.result = ""

    def callMyJDownloader(self, recap):
        self.result = recap.solve(self.url, self.siteKey)
        control.execute('Dialog.Close(yesnoDialog)')

    def call9kw(self, recap):
        self.result = recap.solve(self.url, self.siteKey)
        control.execute('Dialog.Close(yesnoDialog)')

    def getSolutionWithDialog(self, url, siteKey, infotext):
        time = int(control.setting('Recaptcha2.TimeOut'))
        self.url = url
        self.siteKey = siteKey
        if "0" == control.setting('Recaptcha2.Mode'):
            recap = myJDownloader.MyJDownloader()
            t = threading.Thread(target=self.callMyJDownloader, args=(recap,))
        else:
            recap = captcha9kw.captcha9KW()
            t = threading.Thread(target=self.call9kw, args=(recap,))

        t.start()

        dialogResult = xbmcgui.Dialog().yesno(heading="Captcha | " + infotext, line1="Loese das Captcha in MyJDownloader!", line2="Zeit: %s s" % time, nolabel="Abbrechen", yeslabel="Mehr Info", autoclose=time*1000)
        if dialogResult:
            xbmc.log("YesNo-Dialog closed with true", xbmc.LOGDEBUG)
        else:
            xbmc.log("YesNo-Dialog closed with false", xbmc.LOGDEBUG)
        if self.result != "":
            #we have gotten a result! :)
            return self.result.strip()
        elif dialogResult:
            #more info
            win = PopupRecapInfoWindow()
            win.doModal()
            win.show()
            while control.condVisibility('Window.IsActive(PopupRecapInfoWindow)'):
                xbmc.log("Info-Dialog still open...", xbmc.LOGDEBUG)
                xbmc.sleep(1000)
            return ""
        else:
            #timeout or cancel
            recap.setKill()
            xbmc.sleep(1000)
            t.join()
            return ""

class PopupRecapInfoWindow(xbmcgui.WindowDialog):
    def __init__(self):
        self.width = 1280
        self.height = 720

        self.dialogWidth = 550
        self.dialogHeight = 220
        self.centerX = (self.width - self.dialogWidth)/2
        self.centerY = (self.height - self.dialogHeight)/2

        PLUGIN_ID = 'plugin.video.lastship'
        MEDIA_URL = 'special://home/addons/{0}/resources/media/'.format(PLUGIN_ID)
        back = MEDIA_URL + 'background.jpg'
        qr = MEDIA_URL + 'qr.png'

        self.addControl(xbmcgui.ControlImage(x=self.centerX, y=self.centerY, width=self.dialogWidth, height=self.dialogHeight, filename=back))
        self.addControl(xbmcgui.ControlImage(x=self.centerX+10, y=self.centerY+10, width=200, height=200, filename=qr))
        self.addControl(xbmcgui.ControlLabel(x=self.centerX+220, y=self.centerY+10, width=600, height=25, font='font14', label="Download the App!"))
        self.addControl(xbmcgui.ControlLabel(x=self.centerX+220, y=self.newLinePos()+10, width=600, height=25, font='font14', label="Use the QR-Code with caution!"))
        self.okButton = xbmcgui.ControlButton(x = self.centerX+250, y = self.centerY + self.dialogHeight-80,height=60,width=300, font='font14', label="OK", alignment=2, textOffsetY=15, focusedColor="0xFF000000", textColor="0xFF00BBFF")
        self.addControl(self.okButton)
        self.setFocus(self.okButton)

    def onControl(self, controlID):
        # Toggle mode(tuning/setting)
        if controlID == self.okButton:
            self.close()

    def onAction(self, action):
        if action == xbmcgui.ACTION_NAV_BACK:
            self.close()

    def newLinePos(self):
        self.centerY = self.centerY + 25
        return self.centerY