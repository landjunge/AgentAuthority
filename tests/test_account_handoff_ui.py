"""Own local fixture, real browser/HTTP; no foreign session, mail or public write."""
import re
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
from agent_authority.browser import BrowserServer
from agent_authority.browser_auth import init_synthetic
from agent_authority.browser_service import Store
from agent_authority.account_access import AccountAccess
from agent_authority.browser_contracts import Problem
from agent_authority.browser_handoff import _CONTEXT_JSON

class AccountHandoffUITests(unittest.TestCase):
    def test_mobile_keyboard_account_handoff_and_revoke(self):
        from playwright.sync_api import sync_playwright
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'state';init_synthetic(path);store=Store(path)
            used=set();revoked=set();context=json.loads(_CONTEXT_JSON)
            def peer(operation, credential):
                if operation=='redeem':
                    if credential in used:raise Problem(401,'REPLAY')
                    used.add(credential);credential='g'*43
                if credential in revoked:raise Problem(401,'REVOKED')
                if operation=='revoke':revoked.add(credential);return {'revoked':True}
                return {'issuer':'ki-hilfezentrum-account-v1','audience':'agent-authority-browser-v1',
                        'subject':'kh-account-own-ui-fixture','sourceId':'kh-listing-own-ui-fixture',
                        'jobId':context['assignment']['id'],'adapters':['report'],'expires_at':time.time()+299,
                        'agent_identity_verified':False,'external_authority':'unknown','context':context,'credential':credential}
            store.access=AccountAccess(store.access,peer)
            server=BrowserServer(store,0);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            try:
                with sync_playwright() as p:
                    browser=p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True)
                    try:
                        for width,height,ticket in ((390,844,'a'*43),(1280,900,'b'*43)):
                            # Each context receives a new single-use fixture ticket.
                            revoked.clear()
                            page=browser.new_page(viewport={'width':width,'height':height})
                            errors=[];page.on('pageerror',lambda e:errors.append(type(e).__name__))
                            page.goto(server.origin+'/#account-ticket='+ticket)
                            button=page.get_by_role('button',name=re.compile('Sign in with the selected Help Center account|Mit ausgewähltem Hilfezentrum-Konto anmelden'))
                            button.wait_for();self.assertNotIn(ticket,page.url)
                            button.focus();page.keyboard.press('Enter')
                            page.wait_for_selector('#application:not([hidden])')
                            page.wait_for_function("document.querySelectorAll('#graph-nodes > *').length > 0")
                            self.assertFalse(errors,errors)
                            self.assertLessEqual(page.evaluate('document.documentElement.scrollWidth'),width+1)
                            page.locator('#logout').click();page.wait_for_selector('#login-screen:not([hidden])')
                            self.assertTrue(revoked)
                            page.close()
                    finally:browser.close()
            finally:
                server.shutdown();server.server_close();thread.join();store.close()
