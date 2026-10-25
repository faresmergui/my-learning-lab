from svg import D, figure
from inject import put

# ================================ AWS =================================
M = 'aws'

# --- 02 : comment AWS décide ------------------------------------------
d = D(680, 390)
qs = [('Un Deny explicite quelque part ?', 'oui', 'non', 'REFUS'),
      ("Une SCP de l'organisation l'autorise ?", 'non', 'oui', 'REFUS'),
      ('Un Allow (identité ou ressource) ?', 'non', 'oui', 'REFUS par défaut'),
      ('Limite de permissions et session OK ?', 'non', 'oui', 'REFUS')]
d.text(40, 44, 'requête', 'ct')
d.arrow([(70, 40), (108, 40)], color='c')
for i, (q, bad, good, r) in enumerate(qs):
    y = 16 + i * 82
    d.box(110, y, 330, 48, q, k='c', d=i)
    d.box(520, y + 6, 146, 36, r, k='a', d=i)
    d.arrow([(440, y + 24), (518, y + 24)], color='a', label=bad, dy=-7)
    d.arrow([(275, y + 48), (275, y + 80)], color='ok' if i == 3 else 'c', d=i)
    d.text(285, y + 68, good, 's', anchor='start')
d.box(185, 344, 180, 38, 'AUTORISÉ', k='ok', d=4)
d.arrow([(275, 312), (275, 342)], color='ok')
put(f'{M}/02-iam-et-organizations.md', 'decision', figure(d, "Comment AWS décide d'autoriser une requête", "Un seul Deny suffit à refuser ; sans Allow explicite, la réponse est non."), fence='Deny explicite quelque part')

# --- 03 : un VPC typique ----------------------------------------------
d = D(680, 360)
d.zone(14, 14, 652, 334, 'VPC 10.0.0.0/16 · eu-west-3', k='c')
d.box(290, 26, 100, 36, 'Internet Gateway', tk='s', k='a', d=0)
for j, (az, base) in enumerate([('AZ a', 0), ('AZ b', 1)]):
    x = 30 + j * 314
    d.zone(x, 80, 306, 254, az)
    subs = [('public', f'10.0.{base}.0/24', 'ALB, NAT Gateway\n0.0.0.0/0 → IGW', 'a'),
            ('privé', f'10.0.1{base}.0/24', 'instances applicatives\n0.0.0.0/0 → NAT', 'c'),
            ('données', f'10.0.2{base}.0/24', 'RDS\npas de route Internet', '')]
    for i, (n, cidr, s, k) in enumerate(subs):
        d.box(x + 16, 106 + i * 74, 274, 62, f'{n} · {cidr}', s, k=k, d=1 + i)
    d.arrow([(340, 62), (340, 94), (x + 153, 94), (x + 153, 104)], color='a', d=1)
put(f'{M}/03-vpc-et-reseau.md', 'vpc', figure(d, 'Un VPC typique sur deux zones', "Seuls les sous-réseaux publics ont une route vers l'IGW ; le privé sort par la NAT, les données ne sortent pas."), fence='VPC 10.0.0.0/16 (eu-west-3)')

# --- 05 : ALB et Auto Scaling -----------------------------------------
d = D(680, 340)
d.box(270, 14, 140, 36, 'Internet', d=0)
d.box(200, 78, 280, 50, 'ALB', 'sous-réseaux publics, AZ a + AZ b', k='a', d=1)
d.arrow([(340, 50), (340, 76)], color='a')
d.zone(14, 176, 652, 150, '', k='c')
d.arrow([(340, 128), (340, 152)], color='c', end=False)
d.arrow([(105, 152), (585, 152)], color='c', end=False)
d.text(350, 146, 'health checks /health', 's', anchor='start')
for i, az in enumerate(['AZ a', 'AZ a', 'AZ b', 'AZ b']):
    x = 40 + i * 160
    d.box(x, 206, 130, 48, 'instance', f'{az} · privé', k='c', d=2 + i)
    d.arrow([(x + 65, 152), (x + 65, 204)], color='c')
d.text(340, 286, 'groupe cible géré par un Auto Scaling group : min 2, desired 4, max 10', 'ct', d=6)
d.text(340, 306, 'launch template : AMI, m7g.large, rôle IAM, user data', 's', d=6)
put(f'{M}/05-load-balancing-et-auto-scaling.md', 'asg', figure(d, "L'architecture de base : ALB et Auto Scaling", "Une instance qui échoue au health check est retirée puis remplacée ; l'ASG garde le nombre voulu."), fence='Internet ─► ALB')

# --- 08 : RDS Multi-AZ et réplicas ------------------------------------
d = D(680, 270)
d.box(30, 104, 190, 60, 'principale', 'AZ a · lecture et écriture', k='c', d=0)
d.box(470, 20, 196, 56, 'secours Multi-AZ', 'AZ b · non lisible', k='ok', d=1)
d.box(470, 106, 196, 56, 'read replica', 'AZ c · lisible', d=2)
d.box(470, 192, 196, 56, 'read replica', 'eu-west-1 · promouvable', d=3)
d.arrow([(220, 124), (330, 124), (330, 48), (468, 48)], color='ok', k='thick')
d.arrow([(220, 134), (468, 134)], k='dash')
d.arrow([(220, 144), (330, 144), (330, 220), (468, 220)], k='dash')
d.text(400, 40, 'synchrone', 'okt')
d.text(400, 68, 'bascule auto', 's')
d.text(400, 126, 'asynchrone', 's')
d.text(400, 212, 'asynchrone', 's')
put(f'{M}/08-bases-de-donnees.md', 'rds', figure(d, 'RDS : Multi-AZ et réplicas de lecture', "Le Multi-AZ sert à la disponibilité, les réplicas à la lecture et à la reprise dans une autre région."), fence='Multi-AZ (synchrone, bascule auto)')

# --- 14 : les stratégies de reprise -----------------------------------
d = D(680, 300)
d.arrow([(60, 262), (664, 262)], end=True)
d.arrow([(60, 262), (60, 16)], end=True)
d.text(664, 284, 'rapidité de reprise', 's', anchor='end')
d.text(70, 20, 'coût', 's', anchor='start')
pts = [(120, 232, 'Backup & restore', 'RTO : heures'), (270, 182, 'Pilot light', 'RTO : dizaines de min'),
       (430, 122, 'Warm standby', 'RTO : minutes'), (590, 56, 'Multi-site actif-actif', 'RTO et RPO ≈ 0')]
d.arrow('M120 232 C 300 200, 450 150, 590 56', color='c', k='dash', end=False)
for i, (x, y, t, s) in enumerate(pts):
    d.circle(x, y, 8, k='c', d=i)
    d.text(x, y - 30 if i < 3 else y + 30, t, 't', d=i)
    d.text(x, y - 16 if i < 3 else y + 44, s, 's', d=i)
put(f'{M}/14-resilience-et-reprise.md', 'dr', figure(d, 'Les quatre stratégies de reprise', 'Plus la reprise est rapide, plus on paie une infrastructure qui attend.'), fence='● Backup & restore')

# =============================== DOCKER ===============================
M = 'docker'

# --- 01 : un processus avec des œillères ------------------------------
d = D(680, 280)
d.zone(14, 14, 652, 254, 'hôte Linux', k='')
d.box(30, 44, 180, 140, "processus de l'hôte", 'sshd, systemd…\nvue normale', d=0)
for i, (n, p, c) in enumerate([('web', 'nginx', '512 Mo, 1 CPU'), ('api', 'node', '1 Go, 2 CPU')]):
    x = 230 + i * 218
    d.box(x, 44, 200, 140, f'conteneur « {n} »', f'processus {p}\n\nnamespaces : se croit seul\ncgroups : {c}\nracine : son image', k='c', d=1 + i)
for x in (120, 330, 548):
    d.arrow([(x, 184), (x, 210)], color='a')
d.box(30, 212, 620, 40, 'un seul noyau Linux, partagé par tous', k='a', d=3)
put(f'{M}/01-comprendre-les-conteneurs.md', 'oeilleres', figure(d, 'Un conteneur est un processus isolé', "Pas de machine virtuelle : les namespaces limitent ce qu'il voit, les cgroups ce qu'il consomme."), fence='Hôte Linux (un seul noyau)')

# --- 01 : les couches d'une image -------------------------------------
d = D(680, 250)
d.box(40, 16, 182, 38, 'écriture conteneur 1', k='a', tk='s', d=0)
d.box(238, 16, 182, 38, 'écriture conteneur 2', k='a', tk='s', d=0)
d.zone(30, 66, 400, 168, 'image · lecture seule', k='c')
layers = [('COPY app/ /app', 'couche 4 : change à chaque commit', 'c'), ('RUN npm ci', 'couche 3 : dépendances', 'c'), ('node:22-alpine', 'couches 1-2 : image de base, partagée', '')]
for i, (t, s, k) in enumerate(layers):
    y = 92 + i * 46
    d.box(40, y, 380, 38, t, k=k, d=1 + i)
    d.text(444, y + 23, s, 's', anchor='start', d=1 + i)
d.text(444, 39, 'disparaît avec le conteneur', 's', anchor='start')
put(f'{M}/01-comprendre-les-conteneurs.md', 'couches', figure(d, "Les couches d'une image", "Deux conteneurs partagent les mêmes couches en lecture ; chacun n'écrit que dans sa propre couche."), fence='couche écrivable du conteneur')

# --- 05 : trois façons de monter --------------------------------------
d = D(680, 250)
d.text(129, 22, 'hôte', 'zl')
d.text(551, 22, 'conteneur', 'zl')
rows = [('volume pgdata', '/var/lib/docker/volumes/…', '/var/lib/postgresql/data', 'volume : géré par Docker, survit', 'c'),
        ('dossier du projet', '/home/fares/projet/src', '/app/src', 'bind mount : pratique en dev', ''),
        ('mémoire', 'RAM', '/tmp', "tmpfs : effacé à l'arrêt", '')]
for i, (t, s, dst, lab, k) in enumerate(rows):
    y = 36 + i * 70
    d.box(14, y, 230, 52, t, s, k=k, d=i)
    d.box(436, y, 230, 52, dst, k=k, d=i)
    d.arrow([(244, y + 26), (434, y + 26)], color='c' if k else '', label=lab, dy=-8, d=i)
put(f'{M}/05-volumes-et-donnees.md', 'montages', figure(d, 'Volume, bind mount et tmpfs', 'Les données qui comptent vont dans un volume : elles survivent à la suppression du conteneur.'), fence='/var/lib/docker/volumes/pgdata/_data')

# --- 06 : le bridge ---------------------------------------------------
d = D(680, 330)
d.box(14, 40, 110, 40, 'Internet', d=0)
d.zone(160, 10, 506, 310, 'hôte')
d.box(190, 40, 190, 40, 'eth0 · 203.0.113.10', k='a', tk='s', d=1)
d.arrow([(124, 60), (188, 60)], color='a')
d.box(240, 130, 340, 46, 'bridge br-shop', '172.18.0.1', k='c', d=2)
d.arrow([(285, 80), (285, 128)], color='a')
d.text(296, 104, 'NAT : port 8080 → 172.18.0.2:80', 's', anchor='start')
d.box(200, 238, 170, 52, 'web', '172.18.0.2:80', d=3)
d.box(450, 238, 170, 52, 'db', '172.18.0.3:5432', d=4)
d.arrow([(285, 176), (285, 236)], color='c', start=True)
d.arrow([(535, 176), (535, 236)], color='c', start=True)
d.text(293, 212, 'veth', 's', anchor='start')
d.text(543, 212, 'veth', 's', anchor='start')
d.text(413, 310, 'web et db se joignent par leur nom (DNS de Docker)', 's', d=5)
put(f'{M}/06-le-reseau-docker.md', 'bridge', figure(d, 'Le réseau bridge de Docker', "Seul le port publié est joignable depuis l'extérieur ; entre conteneurs, on passe par le bridge."), fence='bridge br-shop (172.18.0.1)')
print('ok')
