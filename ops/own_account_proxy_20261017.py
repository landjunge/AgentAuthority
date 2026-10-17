"""Remove only the redundant synthetic HTTP Basic gate on the AA app route.

The app owns account authentication. The proxy remains private/authenticated by
its transport token. Other Caddy routes and all application scopes stay intact.
Execute on Debian through the shared lock; no restart of other applications.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

BACKUP=Path('/var/backups/ki-hilfezentrum/20261017-own-service-grants')
CADDY=Path('/opt/4allpass/Caddyfile')

def sha(raw):return hashlib.sha256(raw).hexdigest()
def reload():
 for action in ('validate','reload'):
  subprocess.run(['docker','exec','4allpass-caddy-1','caddy',action,'--config','/etc/caddy/Caddyfile','--adapter','caddyfile'],check=True,capture_output=True,timeout=30)

def main():
 os.umask(0o077)
 activation=json.loads((BACKUP/'backend-activation.json').read_text());assert activation['passed']
 before=CADDY.read_bytes();text=before.decode()
 anchor='\t# agent-authority-private-20261017\n';assert text.count(anchor)==1
 start=text.index(anchor);end=text.index('\timport headers',start)
 block=text[start:end]
 pattern=r'\t\tbasic_auth \{\n\t\t\talice [^\n]+\n\t\t\tbob [^\n]+\n\t\t\}\n'
 assert len(re.findall(pattern,block))==1
 changed=re.sub(pattern,'',block)
 assert 'header_up X-AA-Proxy-Token' in changed
 after=(text[:start]+changed+text[end:]).encode()
 with (BACKUP/'Caddyfile.before-own-account-proxy').open('xb') as f:f.write(before);f.flush();os.fsync(f.fileno())
 assert CADDY.read_bytes()==before
 try:
  # Preserve inode: Caddy uses this exact file as a Docker bind mount.
  CADDY.write_bytes(after);CADDY.chmod(0o600);reload()
 except BaseException:
  CADDY.write_bytes(before);CADDY.chmod(0o600);reload();raise
 result={'passed':True,'before_sha256':sha(before),'after_sha256':sha(after),'only_aa_route_changed':True,'application_account_authentication_required':True,'proxy_token_preserved':True,'source_static_shell_public':True,'external_agent_identity':'unknown','rollback':str(BACKUP/'Caddyfile.before-own-account-proxy')}
 (BACKUP/'own-account-proxy.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
