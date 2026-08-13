import os, re, json, base64, shutil, urllib.request, urllib.error, urllib.parse

BASE = os.path.expanduser('C:/Users/Administrator/.workbuddy')

# --- discover PAT (same logic as prior scripts) ---
PAT = None
for r, d, f in os.walk(BASE):
    if r[len(BASE):].count(os.sep) > 3:
        d[:] = []; continue
    for x in f:
        try:
            t = open(os.path.join(r, x), 'r', errors='ignore').read()
        except Exception:
            continue
        for m in re.findall(r'ghp_[A-Za-z0-9]{30,}', t):
            if m.startswith('ghp_JGGccBYRPM25'):
                try:
                    if json.load(urllib.request.urlopen(urllib.request.Request(
                        'https://api.github.com/user',
                        headers={'Authorization': 'token ' + m}))).get('login') == 'baixi6313':
                        PAT = m
                except Exception:
                    pass
        if PAT:
            break
    if PAT:
        break

if not PAT:
    raise SystemExit('PAT not found')
print('PAT OK, login=baixi6313')

H = {'Authorization': 'token ' + PAT, 'Accept': 'application/vnd.github+json'}

ROOT = 'C:/Users/Administrator/WorkBuddy/2026-07-24-23-26-27'

# repo -> local dir (license variant)
TARGETS = {
    'sxj-2026-08-08':  os.path.join(ROOT, 'dpg-remediation'),        # MIT
    'sxj-android-app': os.path.join(ROOT, 'dpg-remediation-apache'), # Apache
}

FILES = ['LICENSE', 'NOTICE', 'README.md', 'CONTRIBUTING.md',
         'PRIVACY.md', 'SECURITY.md', 'GOVERNANCE.md', 'CODE_OF_CONDUCT.md']


def sha_of(repo, path):
    api = f'https://api.github.com/repos/baixi6313/{repo}/contents'
    try:
        return json.load(urllib.request.urlopen(
            urllib.request.Request(api + '/' + urllib.parse.quote(path, safe='/'), headers=H)))['sha']
    except urllib.error.HTTPError:
        return None


def put(repo, local, repo_path, msg):
    with open(local, 'rb') as fh:
        content = base64.b64encode(fh.read()).decode()
    body = {'message': msg, 'content': content, 'branch': 'main'}
    s = sha_of(repo, repo_path)
    if s:
        body['sha'] = s
    data = json.dumps(body).encode()
    api = f'https://api.github.com/repos/baixi6313/{repo}/contents'
    req = urllib.request.Request(api + '/' + urllib.parse.quote(repo_path, safe='/'),
                                 data=data, headers=H, method='PUT')
    try:
        resp = urllib.request.urlopen(req, timeout=60)
        j = json.load(resp)
        print('OK  ', resp.status, repo, '/', repo_path, '->', j.get('commit', {}).get('sha', '')[:10])
    except urllib.error.HTTPError as e:
        print('ERR ', e.code, repo, '/', repo_path, e.read().decode()[:200])


for repo, local_dir in TARGETS.items():
    lic = 'MIT' if repo == 'sxj-2026-08-08' else 'Apache-2.0'
    print(f'\n=== {repo} ({lic}) ===')
    for fn in FILES:
        local = os.path.join(local_dir, fn)
        if not os.path.exists(local):
            print('SKIP', repo, fn, 'missing locally')
            continue
        put(repo, local, fn, f'add DPG compliance pack ({lic}): {fn}')

print('\n=== DONE PUSH ===')
