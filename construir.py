"""Construye el sitio de una unidad en renta a partir de su ficha oficial de EasyBroker (fotos y descripción) y de CONFIG."""
import io, json, os, re, html, urllib.request, urllib.parse
from PIL import Image, ImageOps
C = json.load(open("config.json", encoding="utf-8"))
E = lambda s: html.escape(str(s), quote=True)
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
def get(u, b=False):
    r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40).read()
    return r if b else r.decode("utf-8", "ignore")
os.makedirs("img", exist_ok=True)
fotos, desc = [], ""
try:
    h = get(C["ficha"])
    urls = []
    for u in re.findall(r"https://assets\.easybroker\.com/property_images/\d+/\d+/" + C["clave"] + r"\.(?:jpg|jpeg|png|webp)", h):
        if u not in urls: urls.append(u)
    for f in os.listdir("img"): os.remove(os.path.join("img", f))
    for i, u in enumerate(urls[:20]):
        try:
            im = ImageOps.exif_transpose(Image.open(io.BytesIO(get(u, True)))).convert("RGB"); im.thumbnail((1800, 1800))
            im.save(f"img/f{i+1:02d}.jpg", "JPEG", quality=80, optimize=True, progressive=True); fotos.append(f"img/f{i+1:02d}.jpg")
        except Exception: pass
    m = re.search(r'<meta[^>]+(?:name|property)="(?:og:)?description"[^>]+content="([^"]+)"', h)
    bloques = re.findall(r'<div[^>]+class="[^"]*(?:description|property-description)[^"]*"[^>]*>(.*?)</div>', h, re.S)
    desc = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", max(bloques, key=len) if bloques else (m.group(1) if m else "")))).strip()
    json.dump({"fotos": fotos, "desc": desc}, open("ficha.json", "w", encoding="utf-8"), ensure_ascii=False)
except Exception as e:
    print("ficha no disponible:", e)
    if os.path.exists("ficha.json"):
        x = json.load(open("ficha.json", encoding="utf-8")); fotos, desc = x["fotos"], x["desc"]
print(len(fotos), "fotos;", len(desc), "caracteres de descripción")
P = C["colores"]; wa = "https://wa.me/523333777337?text=" + urllib.parse.quote(C["wa"])
hero = fotos[0] if fotos else ""
gal = "".join(f'<img src="{f}" alt="{E(C["nombre"])}, foto {i+1}" loading="lazy" data-g>' for i, f in enumerate(fotos[1:13]))
datos = "".join(f"<div><b>{E(a)}</b><span>{E(b)}</span></div>" for a, b in C["datos"])
incl = "".join(f"<li>{E(x)}</li>" for x in C["incluye"])
cerca = "".join(f"<li>{E(x)}</li>" for x in C["cerca"])
faq = "".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in C["faq"])
ld = {"@context": "https://schema.org", "@graph": [{"@type": "Apartment", "@id": "#unidad", "name": C["nombre"], "description": C["sub"], "url": f"https://{C['dominio']}/",
       "numberOfBedrooms": C["rec"], "floorSize": {"@type": "QuantitativeValue", "value": C["m2"], "unitCode": "MTK"}, "image": [f"https://{C['dominio']}/{f}" for f in fotos[:3]],
       "geo": {"@type": "GeoCoordinates", "latitude": C["lat"], "longitude": C["lon"]}, "address": {"@type": "PostalAddress", "addressLocality": C["zona"], "addressRegion": "Jalisco", "addressCountry": "MX"}},
      {"@type": "Offer", "itemOffered": {"@id": "#unidad"}, "priceSpecification": {"@type": "UnitPriceSpecification", "price": C["renta"], "priceCurrency": "MXN", "unitText": "mes"}, "seller": {"@type": "RealEstateAgent", "name": "Acierta Max", "telephone": "+52 33 3377 7337"}},
      {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in C["faq"]]}]}
pagina = f"""<!DOCTYPE html><html lang="es-MX"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(C['titulo'])}</title><meta name="description" content="{E(C['desc_meta'])}"><link rel="canonical" href="https://{C['dominio']}/">
<meta property="og:title" content="{E(C['titulo'])}"><meta property="og:description" content="{E(C['desc_meta'])}"><meta property="og:image" content="https://{C['dominio']}/{hero}"><meta name="theme-color" content="{P['fondo']}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family={C['fuente_titulo']}&family=Figtree:wght@400;600;700&display=swap" rel="stylesheet">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>:root{{--f:{P['fondo']};--a:{P['acento']};--c:{P['claro']};--t:#1b1e22;--s:#5d636b;--wa:#1FA855;--serif:"{C['familia_titulo']}",Georgia,serif;--sans:"Figtree",system-ui,sans-serif}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:var(--c);color:var(--t);font:400 17px/1.6 var(--sans)}}img{{max-width:100%;display:block}}a{{color:inherit}}:focus-visible{{outline:3px solid var(--a);outline-offset:3px}}
.w{{max-width:1150px;margin:0 auto;padding:0 22px}}h1,h2,h3{{font-family:var(--serif);font-weight:400;line-height:1.08;margin:0}}h2{{font-size:clamp(2rem,4.6vw,3rem)}}
.btn{{display:inline-flex;justify-content:center;border-radius:999px;padding:14px 24px;font-weight:700;text-decoration:none}}.bw{{background:var(--wa);color:#fff}}.ba{{background:var(--a);color:var(--f)}}.bl{{box-shadow:inset 0 0 0 1.5px currentColor}}
.top{{position:sticky;top:0;z-index:9;background:var(--f);color:#fff}}.top .w{{display:flex;justify-content:space-between;align-items:center;height:60px}}.top b{{font-family:var(--serif);font-weight:400;font-size:1.4rem}}
.hero{{background:var(--f);color:#fff;padding:44px 0 0}}.hero .w{{display:grid;grid-template-columns:1fr 1.1fr;gap:44px;align-items:end}}
.hero h1{{font-size:clamp(2.4rem,5vw,4rem);margin:12px 0 16px}}.hero p{{color:rgba(255,255,255,.82);font-size:1.12rem}}.eti{{color:var(--a);font-weight:700}}
.precio{{font-family:var(--serif);font-size:clamp(2.4rem,5vw,3.4rem);margin:18px 0 4px}}.hero .foto{{aspect-ratio:4/3;border-radius:18px 18px 0 0;background:url('{hero}') center/cover}}
.hero .acc{{display:flex;gap:12px;flex-wrap:wrap;margin:22px 0 48px}}@media(max-width:900px){{.hero .w{{grid-template-columns:1fr}}.hero .acc{{margin-bottom:10px}}}}
.datos{{display:grid;grid-template-columns:repeat(4,1fr);border-top:2px solid var(--t);margin-top:0}}.datos div{{padding:18px 12px 0 0}}.datos b{{display:block;font-family:var(--serif);font-weight:400;font-size:1.9rem}}.datos span{{color:var(--s)}}
@media(max-width:760px){{.datos{{grid-template-columns:1fr 1fr}}}}.sec{{padding:80px 0}}.intro{{color:var(--s);font-size:1.1rem;max-width:44em;margin-top:14px}}
.dos{{display:grid;grid-template-columns:1fr 1fr;gap:44px}}@media(max-width:900px){{.dos{{grid-template-columns:1fr}}}}ul.l{{line-height:1.9;padding-left:20px}}
.gal{{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:8px;margin-top:24px}}.gal img{{width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:10px;cursor:zoom-in}}
.osc{{background:var(--f);color:#fff}}.osc .intro{{color:rgba(255,255,255,.75)}}iframe{{width:100%;min-height:340px;border:0;border-radius:14px}}
.faq details{{border-bottom:1px solid #ddd;padding:14px 0}}.faq summary{{cursor:pointer;font-family:var(--serif);font-size:1.35rem}}.faq p{{color:var(--s);margin:8px 0 0}}
.desc{{white-space:pre-line;color:var(--s);max-width:48em}}footer{{background:#111;color:#aaa;font-size:.86rem;padding:36px 0 100px;line-height:1.6}}footer b{{color:#fff}}
.flot{{position:fixed;left:12px;right:12px;bottom:calc(12px + env(safe-area-inset-bottom));display:none;z-index:10}}.flot .btn{{width:100%}}@media(max-width:760px){{.flot{{display:block}}}}
.v{{position:fixed;inset:0;background:rgba(0,0,0,.92);display:flex;align-items:center;justify-content:center;z-index:20}}.v[hidden]{{display:none}}.v img{{max-width:94vw;max-height:88vh}}</style></head><body>
<header class="top"><div class="w"><b>{E(C['marca'])}</b><a class="btn bw" style="padding:9px 16px" href="{wa}" target="_blank" rel="noopener">WhatsApp</a></div></header>
<section class="hero"><div class="w"><div><span class="eti">{E(C['etiqueta'])}</span><h1>{E(C['h1'])}</h1><p>{E(C['sub'])}</p>
<div class="precio">${C['renta']:,.0f} <span style="font-size:1rem;font-family:var(--sans)">al mes</span></div>
<div class="acc"><a class="btn ba" href="{wa}" target="_blank" rel="noopener">Agendar una visita</a><a class="btn bl" href="#detalle">Ver detalles</a></div></div>
<div class="foto" role="img" aria-label="{E(C['nombre'])}"></div></div></section>
<section class="sec" id="detalle" style="padding-top:44px"><div class="w"><div class="datos">{datos}</div>
<div class="dos" style="margin-top:56px"><div><h2>{E(C['h2'])}</h2><p class="intro">{E(C['historia'])}</p></div><div><h3>Lo que incluye</h3><ul class="l">{incl}</ul></div></div>
<div class="gal">{gal}</div>{('<h3 style="margin-top:40px">Descripción de la ficha</h3><p class="desc">' + E(desc[:1800]) + '</p>') if desc else ''}</div></section>
<section class="sec osc"><div class="w dos"><div><h2>{E(C['h2_ubic'])}</h2><p class="intro">{E(C['ubic'])}</p><ul class="l">{cerca}</ul>
<p><a class="btn ba" href="https://www.google.com/maps/search/?api=1&query={C['lat']},{C['lon']}" target="_blank" rel="noopener">Cómo llegar</a></p></div>
<iframe title="Mapa" loading="lazy" src="https://www.openstreetmap.org/export/embed.html?bbox={C['lon']-0.012}%2C{C['lat']-0.008}%2C{C['lon']+0.012}%2C{C['lat']+0.008}&layer=mapnik&marker={C['lat']}%2C{C['lon']}"></iframe></div></section>
<section class="sec faq"><div class="w" style="max-width:860px"><h2>Preguntas frecuentes</h2><div style="margin-top:20px">{faq}</div></div></section>
<section class="sec osc" style="text-align:center"><div class="w"><h2>{E(C['cierre'])}</h2><p class="intro" style="margin:12px auto 24px">Te atendemos por WhatsApp las 24 horas; nuestros asesores, todos los días de 9:00 a 19:00.</p><a class="btn bw" href="{wa}" target="_blank" rel="noopener">Agendar mi visita</a></div></section>
<footer><div class="w"><p><b>{E(C['nombre'])}</b> · {E(C['zona'])} · Clave {E(C['clave'])}. Comercializa <b>Acierta Max, S.A. de C.V.</b>, profesionales inmobiliarios, miembros de AMPI y NAR. WhatsApp 33 3377 7337 · <a href="https://acierta.pro">acierta.pro</a> · <a href="https://acierta.pro/aviso-privacidad.html">Aviso de privacidad</a></p>
<p>Renta mensual sujeta a disponibilidad y a la firma de contrato; requisitos, depósito y condiciones se confirman por escrito. {E(C.get('legal',''))}</p></div></footer>
<div class="flot"><a class="btn bw" href="{wa}" target="_blank" rel="noopener">Escríbenos por WhatsApp</a></div><div class="v" id="v" hidden><img alt=""></div>
<script>var v=document.getElementById("v");document.querySelectorAll("[data-g]").forEach(function(i){{i.onclick=function(){{v.querySelector("img").src=i.src;v.hidden=false}}}});v.onclick=function(){{v.hidden=true}};</script></body></html>"""
open("index.html", "w", encoding="utf-8").write(pagina)
open("CNAME", "w").write(C["dominio"] + "\n")
open("robots.txt", "w").write(f"User-agent: *\nAllow: /\nSitemap: https://{C['dominio']}/sitemap.xml\n")
open("sitemap.xml", "w").write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://{C["dominio"]}/</loc></url></urlset>\n')
print("sitio generado")
