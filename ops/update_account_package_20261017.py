"""Exact private AA package update; preserves existing data, keys and limits."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
from deploy_browser import remote

PROGRAM=r'''
import base64,grp,hashlib,json,os,socket,subprocess,sys,time
from pathlib import Path
os.umask(0o077);data=json.load(sys.stdin)
raw=base64.b64decode(data['package']);digest=hashlib.sha256(raw).hexdigest();assert digest==data['sha256']
root=Path('/opt/agent-authority-browser');target=root/'current';previous=str(target.resolve());release=root/'releases'/('account-'+digest[:20]);assert not release.exists();release.mkdir(mode=0o750)
(release/'browser.pyz').write_bytes(raw)
for p in (release,release/'browser.pyz'):
 os.chown(p,0,grp.getgrnam('aa-browser').gr_gid);p.chmod(0o750 if p.is_dir() else 0o640)
link=target.with_name('current.account-update');assert not link.exists();link.symlink_to(release);os.replace(link,target)
subprocess.run(['systemctl','restart','agent-authority-browser.service'],check=True,timeout=40)
token=Path('/var/lib/agent-authority-browser/proxy.token').read_text().strip()
request=('GET /agent-authority/api/session HTTP/1.0\r\nHost: v2202608211799501333.goodsrv.de\r\nX-AA-Proxy-Token: '+token+'\r\n\r\n').encode()
ready=False
for attempt in range(40):
 try:
  with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as c:
   c.settimeout(.5);c.connect('/opt/4allpass/sites/.aa-transport/browser.sock');c.sendall(request);status=c.recv(128).split(b'\r\n')[0].split(b' ')[1]
   if status==b'401':ready=True;break
 except OSError:pass
 time.sleep(.1)
assert ready,'AA private readiness failure'
a=Path('/var/lib/ki-hilfezentrum/aa-service.key').read_bytes();b=Path('/var/lib/agent-authority-browser/help-service.key').read_bytes();assert a==b
result={'passed':True,'aa_source_commit':data['source_commit'],'aa_package_sha256':digest,'previous_release':previous,'active_release':str(release),'own_service_key_file_sha256':hashlib.sha256(a).hexdigest(),'data_or_key_replacement':False,'foreign_agent_identity':'unknown','private_readiness_401':True}
path=Path('/var/backups/ki-hilfezentrum/20261017-own-service-grants')/('aa-package-update-'+digest[:12]+'.json');path.write_text(json.dumps(result,indent=2));print(json.dumps(result))
'''
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--package',type=Path,required=True);p.add_argument('--evidence',type=Path,required=True);a=p.parse_args()
 raw=a.package.read_bytes();manifest=json.loads(a.package.with_name('PACKAGE-MANIFEST.json').read_text());assert manifest['sourceClean']
 payload=json.dumps({'package':base64.b64encode(raw).decode(),'sha256':hashlib.sha256(raw).hexdigest(),'source_commit':manifest['sourceCommit']}).encode()
 out=remote(PROGRAM,payload);a.evidence.write_bytes(out);a.evidence.chmod(0o600);print(out.decode())
