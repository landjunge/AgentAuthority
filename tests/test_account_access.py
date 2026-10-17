"""Own-service claims remain a denial boundary, including optimized Python."""
import os
import subprocess
import sys
import time
import unittest
from agent_authority.account_access import AccountAccess
from agent_authority.browser_contracts import Problem

class GrantClaimTests(unittest.TestCase):
    def grant(self):
        return dict(issuer='ki-hilfezentrum-account-v1',audience='agent-authority-browser-v1',
                    agent_identity_verified=False,external_authority='unknown',expires_at=time.time()+60,
                    adapters=['report'],subject='kh-account-own-fixture',sourceId='kh-listing-own-fixture',jobId='own-job')

    def test_foreign_audience_issuer_scopes_expiry_and_asserted_model_identity_rejected(self):
        access=AccountAccess(None,None);self.assertEqual(access.checked(self.grant()).subject,'kh-account-own-fixture')
        for field,value in [('issuer','foreign'),('audience','foreign'),('adapters',['observations']),
                            ('agent_identity_verified',True),('external_authority','verified'),
                            ('expires_at',time.time()-1),('expires_at',float('inf')),('expires_at',True),('subject','../escape')]:
            with self.subTest(field=field,value=str(value)):
                with self.assertRaises(Problem):access.checked({**self.grant(),field:value})

    def test_optimized_interpreter_cannot_remove_audience_check(self):
        code="from agent_authority.account_access import AccountAccess; from agent_authority.browser_contracts import Problem; import time\ngrant="+repr(self.grant())+"\ngrant['audience']='foreign'\ntry: AccountAccess(None,None).checked(grant)\nexcept Problem: print('denied')\nelse: raise SystemExit('accepted foreign audience')"
        result=subprocess.run([sys.executable,'-O','-c',code],capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,0);self.assertEqual(result.stdout.strip(),'denied')
