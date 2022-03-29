import time
import requests
import json

template = """<?xml version="1.0" encoding="UTF-8"?>
<jnlp spec="1.0+" codebase="https://{IP}/Java">
<information>
<title>JViewer</title>
<vendor>American Megatrends, Inc.</vendor>
<description kind="one-line">JViewer Console Redirection Application</description>
<description kind="tooltip">JViewer Console Redirection Application</description>
<description kind="short">
JViewer enables a user to view the video display of managed server via KVM.
It also enables the user to redirect his local keyboard, mouse for managing the server remotely.
</description>
</information>
<security>
<all-permissions/>
</security>
<resources>
<j2se version="1.5+"/>
<jar href="release/JViewer.jar"/>
</resources>
<resources os="Windows" arch="amd64">
<j2se version="1.5+"/>
<nativelib href="release/Win64.jar"/>
</resources>
<resources os="Windows" arch="x86">
<j2se version="1.5+"/>
<nativelib href="release/Win32.jar"/>
</resources>
<resources os="Linux" arch="x86">
<j2se version="1.5+"/>
<nativelib href="release/Linux_x86_32.jar"/>
</resources>
<resources os="Linux" arch="i386">
<j2se version="1.5+"/>
<nativelib href="release/Linux_x86_32.jar"/>
</resources>
<resources os="Linux" arch="x86_64">
<j2se version="1.5+"/>
<nativelib href="release/Linux_x86_64.jar"/>
</resources>
<resources os="Linux" arch="amd64">
<j2se version="1.5+"/>
<nativelib href="release/Linux_x86_64.jar"/>
</resources>
<application-desc>
<argument>{IP}</argument>
<argument>7578</argument>
<argument>{TOKEN}</argument>
<argument>{COOKIE}</argument>
</application-desc>
</jnlp>
"""


class Client:
    def __init__(self, ip, user, password):
        self.api = requests.session()
        self.ip = ip
        self.user = user
        self.password = password
        self.cookie = None
        self.token = None

    @staticmethod
    def _extract_data(payload):
        return payload.split(' [ \n ')[1].split(',')[0].replace(" ", "").replace("'", '"')

    def _get_cookie(self):
        data = {
            'WEBVAR_USERNAME': f'{self.user}',
            'WEBVAR_PASSWORD': f'{self.password}',
        }
        content = self.api.post(f'http://{self.ip}/rpc/WEBSES/create.asp', data=data).text
        result = json.loads(self._extract_data(content))
        self.cookie = result['SESSION_COOKIE']
        if self.cookie != 'Failure_Login_IPMI_Then_LDAP':
            return self.cookie
        raise RuntimeError('Invalid login or password')

    def get_token(self):
        cookie = self._get_cookie()
        headers = {
            'Cookie': f'SessionCookie={cookie}'
        }
        content = self.api.get(f'http://{self.ip}/rpc/getsessiontoken.asp', headers=headers).text
        raw = self._extract_data(content).split('":"')[1].split('"')[0]
        self.token = raw
        return raw

    def gen_file(self):
        self.get_token()
        with open(f'{self.ip}_jviewer_{int(time.time())}.jnlp', 'w') as tpl:
            tpl.write(template.format(IP=self.ip, COOKIE=self.cookie, TOKEN=self.token))


if __name__ == '__main__':
    c = Client('192.168.88.106', 'root', 'superuser')
    c.gen_file()
