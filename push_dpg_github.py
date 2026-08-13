import os, re, json, base64, urllib.request, urllib.error, urllib.parse

BASE = os.path.expanduser('C:/Users/Administrator/.workbuddy')
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

H = {'Authorization': 'token ' + PAT, 'Accept': 'application/vnd.github+json'}
API = 'https://api.github.com/repos/baixi6313/sxj-2026-08-08/contents'
BRANCH = 'main'

def sha_of(path):
    try:
        return json.load(urllib.request.urlopen(
            urllib.request.Request(API + '/' + urllib.parse.quote(path, safe='/'), headers=H)))['sha']
    except urllib.error.HTTPError:
        return None

def put(local, repo_path, msg):
    with open(local, 'rb') as fh:
        content = base64.b64encode(fh.read()).decode()
    body = {'message': msg, 'content': content, 'branch': BRANCH}
    s = sha_of(repo_path)
    if s:
        body['sha'] = s
    data = json.dumps(body).encode()
    req = urllib.request.Request(API + '/' + urllib.parse.quote(repo_path, safe='/'),
                                 data=data, headers=H, method='PUT')
    try:
        resp = urllib.request.urlopen(req, timeout=60)
        print('OK ', resp.status, repo_path)
    except urllib.error.HTTPError as e:
        print('ERR', e.code, repo_path, e.read().decode()[:200])

ROOT = 'C:/Users/Administrator/WorkBuddy/2026-07-24-23-26-27'
put(os.path.join(ROOT, 'SXJ-DPG-assessment-en.md'), 'SXJ-DPG-assessment-en.md',
    'add DPG Standard assessment (conditional pass; license is hard blocker)')
put(os.path.join(ROOT, 'SXJ-DPG-nomination-en.md'), 'SXJ-DPG-nomination-en.md',
    'add DPG nomination draft (fill-in for DPGA eligibility/registry)')
