import os, glob

D = r"C:\Users\Administrator\WorkBuddy\2026-07-22-08-14-20\hygzz_cn_domestic"

HEAD = """  <link rel="manifest" href="/manifest.webmanifest">
  <meta name="theme-color" content="#A32D2D">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="事现鉴">
  <link rel="apple-touch-icon" href="/icon-192.png">
"""

BODY = """<script>if('serviceWorker' in navigator){window.addEventListener('load',function(){navigator.serviceWorker.register('/sw.js').catch(function(){});});}</script>
"""

for f in glob.glob(os.path.join(D, "*.html")):
    with open(f, "r", encoding="utf-8") as fh:
        html = fh.read()
    if "manifest.webmanifest" in html:
        print("skip (already injected):", os.path.basename(f))
        continue
    if "</head>" in html:
        html = html.replace("</head>", HEAD + "</head>", 1)
    if "</body>" in html:
        html = html.replace("</body>", BODY + "</body>", 1)
    with open(f, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("injected:", os.path.basename(f))
