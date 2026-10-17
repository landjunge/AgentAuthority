"""One exact synthetic package qualification on netcup, through the shared lock.

Run from the named worktree after committing the checker and building the package.
Only an owned temporary transfer directory and transient resource scope are used.
No installed service, production path, key, account or configuration is accessed.
"""

from __future__ import annotations

import hashlib
import io
import json
import shlex
import subprocess
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = Path(__file__).resolve().parent
PACKAGE = ROOT / "dist/browser-debian-abschluss"
LOCK = Path(
    "/Users/landjunge/agent-bridge/queues/gesamtabschluss-20261017T084846Z/with-debian-lock.py"
)

# Executed only inside the new temporary scope. Check effective kernel limits
# before starting any synthetic account or service. No host setting is changed.
RUNNER = r"""
import hashlib,json,os,platform,subprocess,sys
from pathlib import Path
cwd=Path.cwd()
cg=Path('/sys/fs/cgroup')/Path('/proc/self/cgroup').read_text().strip().split('::',1)[1].lstrip('/')
def read(name): return (cg/name).read_text().strip()
def pairs(name): return dict(line.split() for line in read(name).splitlines())
before=pairs('memory.events')
limits={name:read(name) for name in ('cpu.max','memory.max','memory.swap.max','pids.max')}
assert limits == {'cpu.max':'35000 100000','memory.max':'536870912','memory.swap.max':'0','pids.max':'16'}
manifest=json.loads((cwd/'PACKAGE-MANIFEST.json').read_text())
digest=hashlib.sha256((cwd/'agent-authority-browser.pyz').read_bytes()).hexdigest()
assert (cwd/'SHA256SUMS').read_text() == digest+'  agent-authority-browser.pyz\n'
assert manifest['sourceClean'] is True
(cwd/'tmp').mkdir(mode=0o700)
environment=dict(os.environ,TMPDIR=str(cwd/'tmp'))
check=subprocess.run([sys.executable,'-I','-B','check_browser_package.py','--package',str(cwd/'agent-authority-browser.pyz'),'--evidence',str(cwd/'package-result.json')],env=environment,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120)
result=json.loads((cwd/'package-result.json').read_text())
after=pairs('memory.events')
environment={'schema':'aa-browser-debian-environment-v1','python':platform.python_version(),'kernel':platform.release(),'osRelease':dict(line.split('=',1) for line in Path('/etc/os-release').read_text().splitlines() if '=' in line).get('PRETTY_NAME'),'limits':limits,'scopeKind':'own-transient-synthetic-scope','memoryPeakBytes':int(read('memory.peak')),'swapCurrentBytes':int(read('memory.swap.current')),'pidsPeak':int(read('pids.peak')),'memoryEventsDelta':{k:int(after[k])-int(v) for k,v in before.items()},'checkerSha256':hashlib.sha256((cwd/'check_browser_package.py').read_bytes()).hexdigest(),'packageSha256':digest,'packageSourceCommit':manifest['sourceCommit'],'checkerExitCode':check.returncode,'browserExecuted':False}
environment['passed']=check.returncode==0 and result['passed'] is True and result['packageSha256']==digest and result['packageSourceVersion']==manifest['sourceCommit'] and result['packageSourceClean'] is True and environment['swapCurrentBytes']==0 and environment['memoryEventsDelta'].get('oom',0)==0 and environment['memoryEventsDelta'].get('oom_kill',0)==0
print(json.dumps({'package':result,'environment':environment}))
raise SystemExit(0 if environment['passed'] else 2)
"""

# The bootstrap receives only five allowlisted synthetic files on stdin. Its
# finally block removes its own transfer, after the scope has lost all processes.
BOOTSTRAP = r"""
import io,json,os,shutil,subprocess,sys,tarfile,tempfile
from pathlib import Path
os.umask(0o077)
path=Path(tempfile.mkdtemp(prefix='aa-browser-debian-abschluss-'))
unit='aa-browser-abschluss-'+path.name.rsplit('-',1)[-1]+'.scope'
expected={'agent-authority-browser.pyz','PACKAGE-MANIFEST.json','SHA256SUMS','check_browser_package.py','run.py'}
result={'schema':'aa-browser-debian-transfer-v1','passed':False,'ownTransferPath':str(path),'ownScope':unit}
stage='transfer-validation'
try:
 raw=sys.stdin.buffer.read(4*1024*1024+1)
 assert len(raw)<=4*1024*1024
 with tarfile.open(fileobj=io.BytesIO(raw),mode='r:') as archive:
  members=archive.getmembers()
  assert len(members)==len(expected) and {m.name for m in members}==expected
  for member in members:
   assert member.isfile() and member.size<=2*1024*1024
   with archive.extractfile(member) as source:
    (path/member.name).write_bytes(source.read())
 stage='bounded-package-probe'
 command=['systemd-run','--quiet','--scope','--unit='+unit,'--property=CPUQuota=35%','--property=MemoryMax=512M','--property=MemorySwapMax=0','--property=TasksMax=16','--property=RuntimeMaxSec=150s','python3','-I','-B',str(path/'run.py')]
 run=subprocess.run(command,cwd=path,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=165)
 result.update(json.loads(run.stdout))
 result['scopeExitCode']=run.returncode
 result['passed']=run.returncode==0 and result['environment']['passed']
except (Exception,KeyboardInterrupt) as exc:
 result['passed']=False
 result['failureStage']=stage
 result['failureType']=type(exc).__name__
finally:
 # A bus/query failure is not proof that a scope is inactive. Also inspect all
 # remaining process lists under this own scope before deleting its files.
 scope_inactive=False
 cleanup_error=None
 try:
  def scope_state():
   query=subprocess.run(['systemctl','show',unit,'--property=LoadState','--property=ActiveState','--property=ControlGroup'],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=10)
   values=dict(line.split('=',1) for line in query.stdout.decode().splitlines() if '=' in line)
   if query.returncode not in (0,4) or 'LoadState' not in values or 'ActiveState' not in values:
    raise RuntimeError('scope-query-failed')
   return values
  values=scope_state()
  if values['ActiveState'] in ('active','activating','deactivating'):
   subprocess.run(['systemctl','stop',unit],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=15,check=True)
   values=scope_state()
  scope_inactive=values['ActiveState'] in ('inactive','failed') and values['LoadState'] in ('loaded','not-found')
  group=values.get('ControlGroup','')
  if group:
   assert group.startswith('/') and Path(group).name==unit
   cg=Path('/sys/fs/cgroup')/group.lstrip('/')
   scope_inactive=scope_inactive and all(not p.read_text().strip() for p in cg.rglob('cgroup.procs'))
  if scope_inactive:
   shutil.rmtree(path)
 except Exception as exc:
  cleanup_error=type(exc).__name__
 result['cleanup']={'ownScopeInactive':scope_inactive,'ownTransferDirectoryRemoved':not path.exists(),'ownTransferFiles':len(expected),'persistentUnitFilesCreated':False,'productionPathsAccessed':False,'failureType':cleanup_error}
 result['passed']=result['passed'] and all(result['cleanup'][k] for k in ('ownScopeInactive','ownTransferDirectoryRemoved'))
print(json.dumps(result))
raise SystemExit(0 if result['passed'] else 2)
"""


def main() -> None:
    if (OUTPUT / "debian-result.json").exists():
        raise SystemExit("Existing evidence retained; no repeated probe started.")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    assert not subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=normal"], cwd=ROOT
    )
    manifest = json.loads((PACKAGE / "PACKAGE-MANIFEST.json").read_bytes())
    assert manifest["sourceCommit"] == commit and manifest["sourceClean"] is True
    for name, digest in manifest["files"].items():
        if name != "__main__.py":
            assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest
    content = {
        name: (PACKAGE / name).read_bytes()
        for name in ("agent-authority-browser.pyz", "PACKAGE-MANIFEST.json", "SHA256SUMS")
    }
    content["check_browser_package.py"] = (ROOT / "scripts/check_browser_package.py").read_bytes()
    content["run.py"] = RUNNER.encode()
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode="w") as archive:
        for name, raw in content.items():
            member = tarfile.TarInfo(name)
            member.size = len(raw)
            member.mode = 0o600
            archive.addfile(member, io.BytesIO(raw))
    command = [
        "python3",
        str(LOCK),
        "ssh",
        "netcup",
        "python3 -I -B -c " + shlex.quote(BOOTSTRAP),
    ]
    run = subprocess.run(command, input=stream.getvalue(), stdout=subprocess.PIPE, check=False)
    result = json.loads(run.stdout)
    expected_digest = hashlib.sha256(content["agent-authority-browser.pyz"]).hexdigest()
    identity_matches = (
        result.get("package", {}).get("packageSourceVersion") == commit
        and result.get("package", {}).get("packageSha256") == expected_digest
    )
    result["passed"] = result["passed"] and identity_matches and run.returncode == 0
    result["localTransport"] = {
        "expectedSourceCommit": commit,
        "expectedPackageSha256": expected_digest,
        "returnedIdentityMatches": identity_matches,
        "sharedExclusiveStarter": str(LOCK),
        "qualificationScriptSha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "bootstrapSha256": hashlib.sha256(BOOTSTRAP.encode()).hexdigest(),
        "runnerSha256": hashlib.sha256(RUNNER.encode()).hexdigest(),
        "tarSha256": hashlib.sha256(stream.getvalue()).hexdigest(),
        "sshExitCode": run.returncode,
    }
    with (OUTPUT / "debian-result.json").open("x") as target:
        json.dump(result, target, indent=2)
        target.write("\n")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if run.returncode == 0 and result["passed"] else 2)


if __name__ == "__main__":
    main()
