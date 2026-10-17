"""One narrow, bounded live recovery exercise; never restores synthetic state."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

ROOT=Path('/opt/agent-authority-browser')
UNIT='agent-authority-browser.service'

def run(*args):
    return subprocess.run(args,check=True,capture_output=True,text=True).stdout

def active():
    return subprocess.run(['systemctl','is-active','--quiet',UNIT]).returncode==0

def exercise():
    spec=importlib.util.spec_from_file_location('operations',ROOT/'operations/browser_service.py')
    op=importlib.util.module_from_spec(spec);spec.loader.exec_module(op)
    activation=json.loads((ROOT/'activation.json').read_text())
    hashes={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path('/opt/4allpass/Caddyfile'),Path('/var/lib/agent-authority-browser/data/config.json'))}
    before=(ROOT/'current').resolve();rows=Path('/var/lib/agent-authority-browser/data/reports.sqlite3').read_bytes()
    assert active() and not (ROOT/'SECURITY-STOP').exists()
    checks=[]
    op.rollback_code(activation['package_sha256'])
    assert active() and (ROOT/'current').resolve()==before
    checks.append('pinned_first_release_code_switch_restarts_successfully')
    # First installation has no older production AA release; test same pin only.
    op.security_stop()
    try:
        assert not active() and (ROOT/'SECURITY-STOP').is_file()
        checks.append('persistent_security_latch_disables_service')
        run('systemctl','start',UNIT)
        assert not active()
        checks.append('manual_start_cannot_bypass_latch')
        try:op.rollback_code(activation['package_sha256'])
        except ValueError:pass
        else:raise AssertionError('code_switch_bypassed_security_latch')
        checks.append('code_switch_cannot_clear_latch')
    finally:
        marker=ROOT/'SECURITY-STOP'
        assert marker.read_text()=='Operator security stop: explicit operator clearance required before restart.\n'
        marker.unlink()
        run('systemctl','enable','--now',UNIT)
        op.wait_ready()
    assert active() and not (ROOT/'SECURITY-STOP').exists()
    assert all(hashlib.sha256(path.read_bytes()).hexdigest()==digest for path,digest in hashes.items())
    assert Path('/var/lib/agent-authority-browser/data/reports.sqlite3').read_bytes()==rows
    checks+=['explicit_root_recovery_active','caddy_and_account_configuration_retained','database_bytes_retained']
    print(json.dumps({'passed':True,'checks':checks,'older_aa_release_available':False,'code_switch_target':activation['package_sha256'],'service_active':active()},indent=2))

if __name__=='__main__':exercise()
