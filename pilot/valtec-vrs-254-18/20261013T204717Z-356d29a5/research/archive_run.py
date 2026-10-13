from pathlib import Path
import shutil,json,hashlib,datetime
src=Path("/Users/nikitas/Documents/ChatGPT/Ворк/plumbing-detailing-/output/cutaways/valtec-vrs-254-18/20261013T204717Z-356d29a5"); dst=Path("/Users/nikitas/Documents/ChatGPT/Ворк/plumbing-detailing-/pilot/valtec-vrs-254-18/20261013T204717Z-356d29a5")
shutil.copytree(src,dst,ignore=shutil.ignore_patterns('*.pdf','*.zip','*.lock','__pycache__'))
s=json.loads((dst/'state.json').read_text())
# Inspect state fields, without dumping history.
print('state_keys',list(s.keys()))
print('archive_MB',round(sum(p.stat().st_size for p in dst.rglob('*') if p.is_file())/1e6,1))
assert len(s['attempts'])==3
for a in s['attempts']:
 assert hashlib.sha256((dst/a['image']).read_bytes()).hexdigest()==a['image_sha256']
 if a.get('preview'): assert hashlib.sha256((dst/a['preview']).read_bytes()).hexdigest()==a['preview_sha256']
assert hashlib.sha256((dst/'final/best.png').read_bytes()).hexdigest()==s['attempts'][2]['preview_sha256']
assert not list(dst.rglob('*.pdf')) and not list(dst.rglob('*.zip'))
print('hashes_verified',3,'plus previews/final')
