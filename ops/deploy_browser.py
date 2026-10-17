"""Transfer/operate only through the shared exclusive Debian starter. No secrets.

Install requires a clean committed source package. Every remote process is under
one lock invocation. Own transferred temporary package is removed on success;
operations and evidence remain in the private active release.
"""
import base64
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
LOCK='/Users/landjunge/agent-bridge/queues/gesamtabschluss-20261017T084846Z/with-debian-lock.py'

def remote(code, payload=None):
    command=shlex.join(['python3','-c',code])
    return subprocess.run([sys.executable,LOCK,'ssh','-o','BatchMode=yes','netcup',command],input=payload,capture_output=True,check=True,timeout=240).stdout

def install():
    package=ROOT/'dist/browser-dauerbetrieb/agent-authority-browser.pyz'
    manifest=json.loads(package.with_name('PACKAGE-MANIFEST.json').read_text())
    assert manifest['sourceClean']
    files={p.name:base64.b64encode(p.read_bytes()).decode() for p in (package,ROOT/'ops/browser_service.py',ROOT/'ops/check_browser_service.py')}
    payload=json.dumps(files).encode()
    digest=hashlib.sha256(package.read_bytes()).hexdigest()
    code='''import base64,json,os,pathlib,subprocess,sys,tempfile,shutil
os.umask(0o077)
files=json.load(sys.stdin)
stage=pathlib.Path(tempfile.mkdtemp(prefix='aa-browser-install-',dir='/var/tmp'))
for name,data in files.items():
 assert name in {'agent-authority-browser.pyz','browser_service.py','check_browser_service.py'}
 (stage/name).write_bytes(base64.b64decode(data))
try:
 subprocess.run(['systemd-run','--unit=aa-browser-install-20261017','--slice=aa-browser.slice','--pipe','--wait','--collect','-p','MemoryMax=256M','-p','MemorySwapMax=0','-p','CPUQuota=40%','-p','TasksMax=16','-p','RuntimeMaxSec=180','/usr/bin/python3','-B',str(stage/'browser_service.py'),'install',str(stage/'agent-authority-browser.pyz'),DIGEST],check=True)
 operations=pathlib.Path('/opt/agent-authority-browser/operations');operations.mkdir(mode=0o700)
 for name in ('browser_service.py','check_browser_service.py'):shutil.copyfile(stage/name,operations/name)
 shutil.rmtree(stage)
except BaseException:
 print('Own private transfer preserved for recovery:',stage,file=sys.stderr)
 raise
'''.replace('DIGEST',repr(digest))
    print(remote(code,payload).decode())

def probe():
    code='''import subprocess,pathlib
result=subprocess.run(['systemd-run','--unit=aa-browser-probe-20261017','--slice=aa-browser.slice','--pipe','--wait','--collect','-p','MemoryMax=256M','-p','MemorySwapMax=0','-p','CPUQuota=40%','-p','TasksMax=16','-p','RuntimeMaxSec=120','/usr/bin/python3','-B','/opt/agent-authority-browser/operations/check_browser_service.py'],capture_output=True,text=True)
if result.returncode:
 print(result.stdout);print(result.stderr);raise SystemExit(result.returncode)
pathlib.Path('/opt/agent-authority-browser/live-checks.json').write_text(result.stdout)
print(result.stdout)
'''
    raw=remote(code).decode();value=json.loads(raw)
    out=ROOT/'docs/browser-dauerbetrieb-20261017/live-checks.json';out.write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps({'passed':value['passed'],'checks':len(value['checks']),'evidence':str(out)},indent=2))

if __name__=='__main__':
    action=sys.argv[1]
    try:
        if action=='install':install()
        elif action=='probe':probe()
        else:raise SystemExit('install | probe')
    except subprocess.CalledProcessError as exc:
        # Operation scripts print booleans/paths only, never request headers.
        print(exc.stdout.decode(errors='replace'),file=sys.stderr)
        print(exc.stderr.decode(errors='replace'),file=sys.stderr)
        raise SystemExit(exc.returncode)
