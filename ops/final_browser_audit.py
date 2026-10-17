"""No-secret final read-only audit; run as one bounded lab unit via shared lock."""
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import pwd
import sqlite3
import subprocess
import zipfile

ROOT=Path('/opt/agent-authority-browser')
KH=Path('/var/backups/ki-hilfezentrum/20261017-authority-integration')

def command(*args):
    return subprocess.check_output(args,text=True,stderr=subprocess.DEVNULL).strip()

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def properties(name):
    raw=command('systemctl','show',name,'-p','ActiveState','-p','SubState','-p','User','-p','Group','-p','MemoryMax','-p','MemorySwapMax','-p','CPUQuotaPerSecUSec','-p','TasksMax','-p','MainPID','-p','NRestarts')
    return dict(line.split('=',1) for line in raw.splitlines())

def main():
    activation=json.loads((ROOT/'activation.json').read_text())
    package=ROOT/'current/browser.pyz'
    with zipfile.ZipFile(package) as z:
        manifest=json.loads(z.read('PACKAGE-MANIFEST.json'))
        exact=all(hashlib.sha256(z.read(path)).hexdigest()==digest for path,digest in manifest['files'].items())
    service=properties('agent-authority-browser.service');pid=service['MainPID']
    children=Path(f'/proc/{pid}/task/{pid}/children').read_text().split()
    caddy=Path('/opt/4allpass/Caddyfile').read_text();start=caddy.index('\t# agent-authority-private-20261017\n');end=caddy.index('\timport headers',start)
    unchanged=caddy[:start]+caddy[end:]==Path('/var/backups/agent-authority-browser/20261017/Caddyfile.before').read_text()
    with sqlite3.connect('file:/var/lib/agent-authority-browser/data/reports.sqlite3?mode=ro',uri=True) as db:
        aa_integrity=db.execute('PRAGMA integrity_check').fetchone()[0];reports=db.execute('SELECT count(*) FROM reports').fetchone()[0]
    with sqlite3.connect('file:/var/lib/ki-hilfezentrum/market.sqlite3?mode=ro',uri=True) as db:
        db.execute('BEGIN')
        kh_integrity=db.execute('PRAGMA integrity_check').fetchone()[0]
        counts={name:db.execute('SELECT count(*) FROM '+name).fetchone()[0] for name in ('bots','listings','human_contacts','human_sessions')}
        ledger=bool(db.execute("SELECT 1 FROM privacy_settings WHERE key='ledger_id'").fetchone())
        current_rows={name:sorted(hashlib.sha256(json.dumps(list(row)).encode()).hexdigest() for row in db.execute('SELECT * FROM '+name)) for name in counts}
    with sqlite3.connect((KH/'market.sqlite3').as_uri()+'?mode=ro',uri=True) as before_db:
        before_counts={name:before_db.execute('SELECT count(*) FROM '+name).fetchone()[0] for name in counts}
        before_rows={name:sorted(hashlib.sha256(json.dumps(list(row)).encode()).hexdigest() for row in before_db.execute('SELECT * FROM '+name)) for name in counts}
    # The service remains live. Preserve concurrent additions; never delete them
    # to manufacture a frozen baseline. Compare the original rows without
    # exporting account/subject values or attributing an unknown writer.
    retained={name:not (Counter(before_rows[name])-Counter(current_rows[name])) for name in counts}
    additions={name:sum((Counter(current_rows[name])-Counter(before_rows[name])).values()) for name in counts}
    # Only a schema-shape boolean; it does not claim pin contents or identity.
    # Collector service/socket inactivity is checked separately below.
    outside_legacy_schema=set(json.loads(Path('/etc/aa-private/collector.json').read_text()))!={'sender','receiver'}
    before=json.loads(Path('/var/backups/agent-authority-browser/20261017/before.json').read_text())
    unit_hashes_ok=all(hashlib.sha256(subprocess.check_output(['systemctl','cat',name])).hexdigest()==value for name,value in before['other_units'].items())
    dependencies=json.loads((ROOT/'runtime-provenance.json').read_text())
    dst=ROOT/'runtime/lib/python3.13/site-packages'
    dependency_match=all(sha(dst/name)==digest for name,digest in dependencies['files'].items())
    filesystem={str(p):{'mode':oct(p.stat().st_mode&0o777),'uid':p.stat().st_uid,'gid':p.stat().st_gid} for p in (ROOT,Path('/var/lib/agent-authority-browser'),Path('/var/lib/agent-authority-browser/data'),Path('/etc/agent-authority-browser'),Path('/etc/agent-authority-browser/operator-access.json'),Path('/opt/4allpass'),Path('/opt/4allpass/sites/.aa-transport'))}
    operations=json.loads((ROOT/'operations/SOURCE.json').read_text())
    operation_bytes_match=all(sha(ROOT/'operations'/name)==digest for name,digest in operations['files'].items())
    aggregate=dict(line.split('=',1) for line in command('systemctl','show','aa-browser.slice','-p','MemoryMax','-p','MemorySwapMax','-p','CPUQuotaPerSecUSec').splitlines())
    own_runners=[line.split()[0] for line in command('systemctl','list-units','--state=running','--plain','--no-legend','--no-pager','aa-browser-*.service').splitlines()]
    out={'at':datetime.now(timezone.utc).isoformat(),'audit_source_sha256':sha(Path(__file__)),'operations':{'provenance':operations,'bytes_match_manifest':operation_bytes_match},'aggregate':aggregate,'own_running_lab_units':own_runners,'passed':True,'aa':{'activation':activation,'source_commit':manifest['sourceCommit'],'source_clean':manifest['sourceClean'],'package_bytes_match_manifest':exact,'package_hash_matches_activation':sha(package)==activation['package_sha256'],'unit_hash_matches_activation':sha(Path('/etc/systemd/system/agent-authority-browser.service'))==activation['unit_sha256'],'unit':service,'enabled':command('systemctl','is-enabled','agent-authority-browser.service'),'worker_count':len(children),'worker_uid':int(Path('/proc/'+children[0]+'/status').read_text().split('Uid:')[1].split()[0]),'security_stop_latched':(ROOT/'SECURITY-STOP').exists(),'database_integrity':aa_integrity,'stored_reports':reports,'runtime_file_count':len(dependencies['files']),'runtime_bytes_match_qualified_copy':dependency_match},'caddy':{'only_aa_route_added':unchanged,'container_id':command('docker','inspect','-f','{{.Id}}','4allpass-caddy-1'),'container_id_unchanged':command('docker','inspect','-f','{{.Id}}','4allpass-caddy-1')=='3d2803e5eba4c0363b182446c9be0facd2af832003b5b684ddd1a4b4c069efdb'},'helpcenter':{'source':str(Path('/opt/ki-hilfezentrum').resolve()),'backend_activation':json.loads((KH/'backend-activation.json').read_text()),'web_deployment':json.loads((KH/'web-deployment.json').read_text()),'unit':properties('ki-hilfezentrum.service'),'database_integrity':kh_integrity,'protected_counts':counts,'fresh_backup_counts':before_counts,'all_original_rows_retained':retained,'concurrent_additions_preserved':additions,'addition_actor':'unknown; no attribution from this audit','deletion_ledger_bound':ledger},'legacy':{'unit_definitions_unchanged':unit_hashes_ok,'collector_config_outside_legacy_sender_receiver_schema':outside_legacy_schema,'collector_service':command('systemctl','show','aa-private-collector.service','-p','ActiveState','--value'),'collector_socket':command('systemctl','show','aa-private-collector.socket','-p','ActiveState','--value'),'verifier':command('systemctl','show','aa-private-verifier.service','-p','ActiveState','--value'),'watchdog':command('systemctl','show','aa-private-watchdog.service','-p','ActiveState','--value')},'filesystem':filesystem,'own_install_staging_removed':not Path('/var/tmp/aa-browser-install-7bexenpl').exists(),'other_units_reset':False}
    assert service['ActiveState']=='active' and out['aa']['enabled']=='enabled' and len(children)==1 and out['aa']['worker_uid']==pwd.getpwnam('aa-browser').pw_uid
    assert exact and out['aa']['source_clean'] and out['aa']['package_hash_matches_activation'] and out['aa']['unit_hash_matches_activation'] and dependency_match
    assert aa_integrity==kh_integrity=='ok' and reports==0 and all(retained.values()) and not ledger
    assert unchanged and out['caddy']['container_id_unchanged'] and unit_hashes_ok and outside_legacy_schema and out['legacy']['collector_service']=='inactive' and out['legacy']['collector_socket']=='inactive' and out['legacy']['verifier']=='active' and out['legacy']['watchdog']=='failed'
    assert operation_bytes_match and aggregate=={'CPUQuotaPerSecUSec':'400ms','MemoryMax':'838860800','MemorySwapMax':'0'}
    assert own_runners==['aa-browser-final-audit-20261017.service']
    assert not out['aa']['security_stop_latched'] and out['own_install_staging_removed']
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
