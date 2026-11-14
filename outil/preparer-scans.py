"""Prépare les scans Instax Wide pour le site.

Pour chaque TIFF du dossier images/ :
  1. trouve le tirage sur la vitre du scanner,
  2. le redresse s'il a été scanné un peu de travers (d'après les bords de la photo),
  3. recadre juste à l'intérieur du tirage (plus aucun coin de fond),
  4. remet à l'endroit les tirages paysage scannés à l'envers,
  5. convertit en sRGB et enregistre un JPEG léger dans prints/.
Affiche le code à noter dans index.html (L, P ou Q) et l'angle corrigé.

Utilisation, depuis le dossier du site :
    python3 outil/preparer-scans.py            (tous les scans de images/ -> prints/)
    python3 outil/preparer-scans.py TJ3 TJ4    (seulement ceux-là)
    python3 outil/preparer-scans.py --de images/instax --vers instant
                                               (un autre dossier, par ex. les Instant Photographs)
Les noms de fichiers sont simplifiés pour le web : « Untitled (3) (2).tif » devient « untitled-3-2.jpg ».
Nécessite Python 3 avec Pillow et numpy  (pip3 install pillow numpy)
"""
import os, io, sys, math, re, unicodedata
import numpy as np
from PIL import Image, ImageCms

args = sys.argv[1:]
SRC, OUT = 'images', 'prints'
if '--de' in args: i = args.index('--de'); SRC = args[i+1]; del args[i:i+2]
if '--vers' in args: i = args.index('--vers'); OUT = args[i+1]; del args[i:i+2]
os.makedirs(OUT, exist_ok=True)
only = set(args)
def web_name(n):
    n = unicodedata.normalize('NFKD', n).encode('ascii', 'ignore').decode()
    return re.sub(r'[^A-Za-z0-9]+', '-', n).strip('-') or 'scan'
srgb = ImageCms.createProfile('sRGB')

def line_tilts(mask):
    """Angle (degrés) de chaque bord de la zone True, par ajustement de droite robuste."""
    h, w = mask.shape; out = []
    for side in 'lrtb':
        pts = []
        if side in 'lr':
            for y in range(int(h*.2), int(h*.8), max(1, h//200)):
                xs = np.where(mask[y])[0]
                if len(xs): pts.append((y, xs[0] if side == 'l' else xs[-1]))
        else:
            for x in range(int(w*.2), int(w*.8), max(1, w//200)):
                ys = np.where(mask[:, x])[0]
                if len(ys): pts.append((x, ys[0] if side == 't' else ys[-1]))
        if len(pts) < 20: continue
        u, v = np.array(pts, float).T; keep = np.ones(len(u), bool)
        for _ in range(4):
            a, b = np.polyfit(u[keep], v[keep], 1)
            res = np.abs(v - (a*u + b)); keep = res < max(2.0, np.median(res[keep]) * 3)
        if keep.mean() > .5:
            out.append(math.degrees(math.atan(a)) * (1 if side in 'lr' else -1))
    return float(np.median(out)) if out else None

def analyse(arr, bg):
    d = np.abs(arr - bg).sum(2) > 24
    rows = np.where(d.mean(1) > .3)[0]; cols = np.where(d.mean(0) > .3)[0]
    p = arr[rows[0]:rows[-1]+1, cols[0]:cols[-1]+1]; h, w, _ = p.shape
    fr = np.median(np.concatenate([p[int(h*.4):int(h*.6), int(w*.012):int(w*.025)].reshape(-1, 3),
                                   p[int(h*.012):int(h*.025), int(w*.4):int(w*.6)].reshape(-1, 3)]), 0)
    q = np.abs(p - fr).sum(2) > 45
    mh, mw = int(h*.02), int(w*.02); q[:mh] = q[-mh:] = False; q[:, :mw] = q[:, -mw:] = False
    return d[rows[0]:rows[-1]+1, cols[0]:cols[-1]+1], q

for f in sorted(os.listdir(SRC)):
    if not f.lower().endswith(('.tif', '.tiff', '.jpg', '.jpeg', '.png')): continue
    name = os.path.splitext(f)[0]
    if only and name not in only: continue
    out_name = name if re.fullmatch(r'[A-Za-z0-9_-]+', name) else web_name(name).lower()
    im = Image.open(os.path.join(SRC, f)); icc = im.info.get('icc_profile'); im = im.convert('RGB')
    if icc:
        try: im = ImageCms.profileToProfile(im, ImageCms.ImageCmsProfile(io.BytesIO(icc)), srgb, outputMode='RGB')
        except Exception: pass
    a = np.asarray(im).astype(np.int16)
    bg = np.median(np.concatenate([a[:8].reshape(-1, 3), a[-8:].reshape(-1, 3), a[:, :8].reshape(-1, 3), a[:, -8:].reshape(-1, 3)]), 0)
    bgc = tuple(int(x) for x in bg)
    # 1-2. mesure de l'angle sur une version réduite, puis choix du sens qui redresse
    small = a[::4, ::4]
    dm, q = analyse(small, bg)
    ang = line_tilts(q)
    if ang is None: ang = line_tilts(dm) or 0.0
    best = None
    for sgn in (1, -1):
        r = np.asarray(Image.fromarray(small.astype(np.uint8)).rotate(sgn*ang, resample=Image.BICUBIC, expand=True, fillcolor=bgc)).astype(np.int16)
        resid = line_tilts(analyse(r, bg)[1]); resid = abs(resid) if resid is not None else 99
        if best is None or resid < best[0]: best = (resid, sgn)
    rot = best[1] * ang
    A = np.asarray(Image.fromarray(a.astype(np.uint8)).rotate(rot, resample=Image.BICUBIC, expand=True, fillcolor=bgc)).astype(np.int16)
    # 3. recadrage juste à l'intérieur du tirage
    d = np.abs(A - bg).sum(2) > 24
    rows = np.where(d.mean(1) > .3)[0]; cols = np.where(d.mean(0) > .3)[0]
    y0, x0 = rows[0], cols[0]; sub = d[rows[0]:rows[-1]+1, cols[0]:cols[-1]+1]
    rr = np.where(sub[:, int(sub.shape[1]*.05):int(sub.shape[1]*.95)].mean(1) > .995)[0]
    cc = np.where(sub[int(sub.shape[0]*.05):int(sub.shape[0]*.95)].mean(0) > .995)[0]
    p = A[y0+rr[0]:y0+rr[-1]+1, x0+cc[0]:x0+cc[-1]+1]; h, w, _ = p.shape
    # 4. côté de la bande épaisse
    fr = np.median(np.concatenate([p[int(h*.4):int(h*.6), int(w*.01):int(w*.025)].reshape(-1, 3), p[int(h*.01):int(h*.025), int(w*.4):int(w*.6)].reshape(-1, 3)]), 0)
    like = lambda band: (np.abs(band - fr).sum(2) < 30).mean()
    s = {'left': like(p[int(h*.2):int(h*.8), int(w*.11):int(w*.13)]), 'right': like(p[int(h*.2):int(h*.8), int(w*.87):int(w*.89)]),
         'top': like(p[int(h*.11):int(h*.13), int(w*.2):int(w*.8)]), 'bottom': like(p[int(h*.87):int(h*.89), int(w*.2):int(w*.8)])}
    land = w > h
    thick = max(['top', 'bottom'] if land else ['left', 'right'], key=lambda k: s[k])
    img = Image.fromarray(p.astype(np.uint8))
    if land and thick == 'top': img = img.rotate(180); thick = 'bottom'
    # 5. JPEG pour le web
    W = 1256 if land else 1000
    img.resize((W, round(W * img.height / img.width)), Image.LANCZOS).save(os.path.join(OUT, out_name + '.jpg'), quality=86, optimize=True, progressive=True)
    print(f"{out_name}:{'L' if land else ('P' if thick == 'right' else 'Q')}   (redressé de {rot:+.2f}°)", flush=True)
