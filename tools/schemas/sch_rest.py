from svg import D, figure
from inject import put

# ============================== SECURITY ==============================
M = 'securite'

d = D(680, 280)
A, B, C = (340, 40), (130, 236), (550, 236)
d.raw(f'<path d="M{A[0]} {A[1]} L{B[0]} {B[1]} L{C[0]} {C[1]} Z" class="dg-zone dg-zc"/>')
d.box(250, 16, 180, 58, 'Confidentialité', 'seuls les bons lisent', k='c', d=0)
d.box(40, 212, 180, 58, 'Intégrité', 'personne ne modifie\nen douce', k='c', d=1)
d.box(460, 212, 180, 58, 'Disponibilité', 'accessible quand\non en a besoin', k='c', d=2)
d.text(340, 150, 'ce qu\'on protège', 'zl')
d.text(150, 120, 'chiffrement, IAM,\nmoindre privilège', 's')
d.text(530, 120, 'redondance, sauvegardes,\nlimites de débit', 's')
d.text(340, 254, 'hash, signatures, journaux', 's')
put(f'{M}/01-principes-et-menaces.md', 'cia', figure(d, 'La triade CIA', 'Chaque mesure de sécurité protège au moins un des trois sommets.'), before='## Les principes qui reviennent partout')

d = D(680, 250)
steps = [('création', 'généré, fort', ''), ('stockage', 'coffre chiffré', 'c'), ('distribution', 'à l\'exécution', 'c'), ('utilisation', 'en mémoire,\npas dans les logs', ''), ('rotation', 'régulière ou auto', 'c')]
for i, (t, s, k) in enumerate(steps):
    x = 14 + i * 134
    d.box(x, 40, 118, 64, t, s, k=k, d=i)
    if i:
        d.arrow([(x - 16, 72), (x - 2, 72)], color='c')
d.arrow(f'M610 106 C 610 170, 140 170, 140 108', color='c', k='dash')
d.text(300, 176, 'nouvelle version, l\'ancienne expire', 's')
d.box(470, 186, 196, 50, 'révocation', 'immédiate en cas de fuite', k='a', d=5)
d.arrow([(475, 104), (475, 150), (560, 150), (560, 184)], color='a')
d.text(14, 220, 'jamais : dans Git, dans l\'image, en clair dans une variable de CI', 'at', anchor='start')
put(f'{M}/02-gestion-des-secrets.md', 'cycle', figure(d, 'Le cycle de vie d\'un secret', 'Un bon système rend la rotation banale : si changer un secret fait peur, il ne sera jamais changé.'), fence='création ──► stockage')

d = D(680, 260)
chain = [('code', 'revue, commits\nsignés', 'compte volé'), ('dépendances', 'lock file, scan', 'paquet piégé'), ('CI', 'OIDC, runners\nisolés', 'secrets volés'),
         ('image', 'SBOM, scan,\nsignature', 'contenu modifié'), ('registre', 'tags immuables', 'image remplacée'), ('cluster', 'admission\nvérifie', 'image non signée')]
for i, (t, prot, thr) in enumerate(chain):
    x = 14 + i * 111
    d.box(x, 96, 98, 52, t, k='c', d=i)
    if i:
        d.arrow([(x - 13, 122), (x - 1, 122)], color='c')
    d.text(x + 49, 40, prot, 'okt' if False else 's', d=i)
    d.text(x + 49, 180, '⚠', 'at', d=i)
    d.text(x + 49, 196, thr, 'as', d=i)
d.text(14, 20, 'protection', 'zl', anchor='start')
d.text(14, 222, 'attaque possible', 'zl', anchor='start')
d.arrow([(14, 236), (666, 236)], k='dash')
d.text(340, 254, 'la confiance doit se vérifier à chaque maillon', 's')
d.h = 262
put(f'{M}/05-supply-chain.md', 'chaine', figure(d, 'La chaîne d\'approvisionnement logicielle', 'Une signature vérifiée à l\'admission garantit que l\'image vient bien de ta CI.'), fence='code ─► dépendances ─► CI (build)')

d = D(680, 290)
layers = [('cloud', 'compte, réseau, IAM', 14, 14, 652, 262), ('cluster', 'API server, RBAC, etcd, admission', 60, 52, 560, 196),
          ('conteneur', 'image, runtime, securityContext', 106, 90, 468, 130), ('code', 'dépendances, secrets, failles', 152, 128, 376, 64)]
for i, (n, s, x, y, w, h) in enumerate(layers):
    d.zone(x, y, w, h, n, k='c' if i % 2 == 0 else '')
    d.text(x + w - 12, y + 18, s, 's', anchor='end', d=i)
d.text(340, 166, 'ton application', 'ct')
put(f'{M}/06-securite-kubernetes.md', '4c', figure(d, 'Les 4C de la sécurité cloud native', 'Chaque couche dépend de celle qui l\'entoure : un code parfait ne sauve pas un cluster ouvert.'), fence='Cloud  ─►  Cluster')

d = D(680, 300)
d.box(20, 14, 110, 40, 'client', k='c', d=0)
d.box(300, 14, 110, 40, 'serveur', k='c', d=0)
d.line(75, 54, 75, 280, k='grid')
d.line(355, 54, 355, 280, k='grid')
msgs = [(80, 'ClientHello : versions, SNI', 1), (124, 'ServerHello + certificat + chaîne', -1), (214, 'échange de clés', 0), (256, 'trafic chiffré', 0)]
for i, (y, t, dirn) in enumerate(msgs):
    if dirn == 1:
        d.arrow([(77, y), (353, y)], color='c', label=t, d=i + 1)
    elif dirn == -1:
        d.arrow([(353, y), (77, y)], color='c', label=t, d=i + 1)
    else:
        d.arrow([(77, y), (353, y)], color='ok' if i == 3 else 'c', start=True, label=t, k='thick' if i == 3 else '', d=i + 1)
d.box(86, 140, 258, 40, 'vérifie : CA connue ? nom dans le SAN ? date ?', k='ghost', tk='s', d=3)
d.zone(452, 14, 214, 270, 'chaîne de confiance')
d.box(470, 46, 178, 52, 'CA racine', 'dans le magasin du système', k='a', d=4)
d.box(470, 132, 178, 52, 'CA intermédiaire', 'envoyée par le serveur', d=5)
d.box(470, 218, 178, 52, 'shop.example.com', 'certificat du site', k='c', d=6)
d.arrow([(559, 98), (559, 130)], label='', d=5)
d.arrow([(559, 184), (559, 216)], d=6)
d.text(566, 118, 'signe', 's', anchor='start')
d.text(566, 204, 'signe', 's', anchor='start')
put(f'{M}/07-tls-et-pki.md', 'handshake', figure(d, 'La poignée de main TLS et la chaîne de certificats', 'L\'erreur la plus fréquente : le serveur oublie d\'envoyer le certificat intermédiaire.'), fence='ClientHello (versions')

d = D(680, 210)
d.zone(14, 14, 300, 182, 'étape build')
d.box(30, 44, 268, 40, 'golang:1.25', 'compilateur, sources, cache', tk='t', d=0)
d.box(30, 96, 268, 40, 'go build', '→ /out/api', k='c', d=1)
d.text(164, 170, '≈ 900 Mo, jamais déployée', 's')
d.zone(366, 14, 300, 182, 'image finale', k='c')
d.box(382, 44, 268, 40, 'distroless:nonroot', 'pas de shell, pas de paquets', k='ok', d=2)
d.box(382, 96, 268, 40, '/api', 'le binaire seul', k='c', d=3)
d.text(516, 170, '≈ 20 Mo, utilisateur non root', 'okt')
d.arrow([(298, 116), (380, 116)], color='c', k='flow', label='COPY --from', dy=20)
put(f'{M}/04-securite-des-conteneurs.md', 'multistage', figure(d, 'Un build multi-étapes', 'Les outils de build restent dans la première étape. L\'image déployée ne contient que le binaire.'), before="## À l'exécution")

# ============================== NETWORKING ==============================
M = 'reseaux'

d = D(680, 260)
d.box(40, 14, 120, 40, 'client', k='c', d=0)
d.box(400, 14, 120, 40, 'serveur', k='c', d=0)
d.line(100, 54, 100, 250, k='grid')
d.line(460, 54, 460, 250, k='grid')
for i, (y, t, r, k) in enumerate([(78, 'SYN', False, 'c'), (110, 'SYN-ACK', True, 'c'), (142, 'ACK', False, 'c'), (182, 'données', None, 'ok'), (226, 'FIN', False, '')]):
    if r is None:
        d.arrow([(102, y), (458, y)], color=k, start=True, k='thick', label=t, d=i)
    elif r:
        d.arrow([(458, y), (102, y)], color=k, label=t, d=i)
    else:
        d.arrow([(102, y), (458, y)], color=k, label=t, d=i)
d.text(476, 114, 'poignée de main', 's', anchor='start')
d.text(476, 128, 'en 3 temps : 1 RTT', 's', anchor='start')
d.text(476, 230, 'fermeture', 's', anchor='start')
put(f'{M}/01-osi-et-tcp-ip.md', 'tcp', figure(d, 'Une connexion TCP', 'Un RST à la place du SYN-ACK : le port est fermé. Pas de réponse du tout : un pare-feu filtre.'), fence='SYN-ACK')

d = D(680, 230)
rows = [('application', [('données HTTP', 'c', 300)]),
        ('transport', [('TCP', '', 70), ('données HTTP', 'c', 300)]),
        ('réseau', [('IP', '', 70), ('TCP', '', 70), ('données HTTP', 'c', 300)]),
        ('liaison', [('Eth', '', 70), ('IP', '', 70), ('TCP', '', 70), ('données HTTP', 'c', 300)])]
for i, (layer, segs) in enumerate(rows):
    y = 20 + i * 50
    d.text(20, y + 24, layer, 'zl', anchor='start')
    x = 666 - sum(w for _, _, w in segs) - 6 * (len(segs) - 1)
    for j, (t, k, w) in enumerate(segs):
        d.box(x, y, w, 36, t, k=k if j == len(segs) - 1 else ('a' if j == 0 and i else ''), tk='s', d=i)
        x += w + 6
d.text(340, 222, 'chaque couche ajoute son en-tête (en rouge) devant ce qu\'elle reçoit', 's')
put(f'{M}/01-osi-et-tcp-ip.md', 'encapsulation', figure(d, 'L\'encapsulation', 'Chaque couche ajoute son en-tête devant ce qu\'elle reçoit. Un tunnel (VXLAN, VPN) en ajoute d\'autres : le MTU utile baisse.'), after='## Encapsulation')

d = D(680, 200)
bits = '00001010 00000000 00001000 00000000'
d.text(340, 24, '10.0.8.0/21', 'tl')
x = 30
for i, ch in enumerate(bits.replace(' ', '')):
    net = i < 21
    d.box(x, 46, 17, 34, ch, k='c' if net else '', tk='s', rx=3)
    x += 19 + (8 if i % 8 == 7 else 0)
d.text(30 + 21 * 19 / 2 + 8, 104, '21 bits réseau : fixes', 'ct')
d.text(520, 104, '11 bits hôtes', 't')
d.text(340, 140, '2¹¹ = 2048 adresses : de 10.0.8.0 à 10.0.15.255', 's')
d.text(340, 160, 'plus le préfixe est grand, plus le réseau est petit', 's')
put(f'{M}/02-adressage-et-cidr.md', 'cidr', figure(d, 'Lire un préfixe CIDR', 'Le nombre après le / dit combien de bits, en partant de la gauche, désignent le réseau.'), before='## Les plages à connaître')

d = D(680, 280)
d.zone(14, 14, 652, 254, 'VPC shop-prod · 10.10.0.0/16', k='c')
tiers = [('public', ['10.10.0.0/24', '10.10.1.0/24', '10.10.2.0/24'], 'load balancers, NAT'),
         ('privé', ['10.10.16.0/20', '10.10.32.0/20', '10.10.48.0/20'], 'nœuds et pods'),
         ('données', ['10.10.64.0/24', '10.10.65.0/24', '10.10.66.0/24'], 'bases')]
for j, az in enumerate('abc'):
    d.text(220 + j * 170, 52, f'zone {az}', 'zl')
for i, (t, cidrs, role) in enumerate(tiers):
    y = 66 + i * 66
    d.text(30, y + 22, t, 't', anchor='start')
    d.text(30, y + 38, role, 's', anchor='start')
    for j, c in enumerate(cidrs):
        d.box(150 + j * 170, y, 140, 52, c, k='c' if i == 1 else '', tk='s', d=i + j)
put(f'{M}/02-adressage-et-cidr.md', 'vpc', figure(d, 'Un plan d\'adressage sur trois zones', 'Les sous-réseaux privés sont larges (/20) car les pods consomment beaucoup d\'adresses.'), fence='VPC shop-prod')

d = D(680, 260)
d.box(14, 100, 100, 52, 'appli', 'api.shop.fr ?', k='c', d=0)
d.box(154, 100, 130, 52, 'résolveur', 'récursif · cache', k='c', d=1)
auth = [('racine .', '« .fr : voir là »', 20), ('serveur .fr', '« shop.fr : voir là »', 100), ('shop.fr', 'faisant autorité\n« 51.15.2.10 »', 180)]
for i, (t, s, y) in enumerate(auth):
    d.box(430, y, 220, 60, t, s, k='ok' if i == 2 else '', d=2 + i)
    d.arrow([(284, 116 + (i - 1) * 8), (360, 116 + (i - 1) * 8), (360, y + 24), (428, y + 24)], color='c', d=2 + i)
    d.circle(400, y + 24, 9, k='c', d=2 + i)
    d.text(400, y + 28, str(i + 2), 'w', d=2 + i)
d.arrow([(114, 120), (152, 120)], color='c')
d.circle(133, 120, 9, k='c')
d.text(133, 124, '1', 'w')
d.arrow([(152, 136), (116, 136)], color='ok', k='thick')
d.text(134, 176, 'réponse,', 's')
d.text(134, 190, 'mise en cache', 's')
d.text(134, 204, 'selon le TTL', 's')
put(f'{M}/03-dns.md', 'resolution', figure(d, 'Une résolution DNS complète', 'Le résolveur fait tout le travail. La prochaine fois, il répondra depuis son cache tant que le TTL n\'est pas écoulé.'), fence='appli ──► résolveur local')

d = D(680, 220)
phases = [('DNS', 20, 'c'), ('TCP', 30, ''), ('TLS', 45, 'c'), ('attente serveur', 120, 'a'), ('téléchargement', 40, 'ok')]
x = 20
total = sum(p[1] for p in phases)
scale = 620 / total
for i, (n, ms, k) in enumerate(phases):
    w = ms * scale
    d.box(x, 40 + i * 30, w, 24, '', k=k, rx=4, d=i)
    last = i == len(phases) - 1
    d.text(x - 8 if last else (x + w + 8 if w < 120 else x + w / 2), 57 + i * 30, f'{n} · {ms} ms', 's', anchor='end' if last else ('start' if w < 120 else 'middle'), d=i)
    x += w
d.line(20 + (20 + 30 + 45 + 120) * scale, 30, 20 + (20 + 30 + 45 + 120) * scale, 196, k='court')
d.text(20 + (20 + 30 + 45 + 120) * scale, 210, 'ttfb', 'at')
d.text(640, 210, 'total', 's', anchor='end')
d.text(20, 24, 'time_namelookup → time_connect → time_appconnect → time_starttransfer → time_total', 's', anchor='start')
put(f'{M}/04-http-et-tls.md', 'waterfall', figure(d, 'Où part le temps d\'une requête HTTPS', 'Ici, c\'est l\'attente serveur qui domine : il faut regarder l\'application, pas le réseau.'), before='## TLS côté réseau')

d = D(680, 260)
d.zone(14, 14, 316, 232, 'L4 : TCP / UDP')
d.box(30, 104, 90, 48, 'client', d=0)
d.box(146, 98, 90, 60, 'NLB', 'IP + port', k='c', d=1)
for j in range(3):
    d.box(256, 46 + j * 62, 60, 40, 'srv', d=2)
    d.arrow([(236, 128), (246, 128), (246, 66 + j * 62), (254, 66 + j * 62)], color='c')
d.arrow([(120, 128), (144, 128)], color='c')
d.text(172, 232, 'TLS passe tel quel', 's')
d.zone(350, 14, 316, 232, 'L7 : HTTP', k='c')
d.box(366, 104, 80, 48, 'client', d=3)
d.box(466, 92, 90, 72, 'ALB', 'lit host,\nchemin, en-têtes', k='c', d=4)
d.box(578, 44, 74, 50, '/', 'web', d=5)
d.box(578, 162, 74, 50, '/api', 'api', d=5)
d.arrow([(446, 128), (464, 128)], color='c')
d.arrow([(556, 116), (566, 116), (566, 69), (576, 69)], color='c')
d.arrow([(556, 140), (566, 140), (566, 187), (576, 187)], color='c')
d.text(508, 232, 'TLS terminé au LB', 's')
put(f'{M}/05-load-balancing-et-proxys.md', 'l4l7', figure(d, 'Load balancer L4 ou L7', 'Un L4 répartit des connexions, un L7 comprend les requêtes HTTP et peut router selon le contenu.'), before='## Un reverse proxy nginx')

d = D(680, 250)
d.text(170, 22, 'SNAT : sortir vers Internet', 'ct')
d.box(14, 60, 120, 52, 'serveur privé', '10.0.1.5', d=0)
d.box(170, 60, 110, 52, 'NAT', '203.0.113.7', k='c', d=1)
d.box(14, 160, 266, 52, 'src 10.0.1.5 → src 203.0.113.7', 'la source est réécrite', k='ghost', tk='s', d=2)
d.arrow([(134, 86), (168, 86)], color='c')
d.arrow([(280, 86), (318, 86)], color='c', k='flow')
d.text(322, 90, 'Internet', 's', anchor='start')
d.line(340, 30, 340, 230, k='grid')
d.text(510, 22, 'DNAT : entrer depuis Internet', 'ct')
d.box(370, 60, 110, 52, 'IP publique', ':443', k='c', d=3)
d.box(540, 60, 126, 52, 'serveur privé', '10.0.1.5:8443', d=4)
d.box(370, 160, 296, 52, 'dst 203.0.113.7:443 → dst 10.0.1.5:8443', 'la destination est réécrite', k='ghost', tk='s', d=5)
d.arrow([(480, 86), (538, 86)], color='c', k='flow')
put(f'{M}/06-pare-feu-et-nat.md', 'nat', figure(d, 'SNAT et DNAT', 'SNAT pour sortir (box, NAT gateway), DNAT pour exposer un service (redirection de port, Service NodePort).'), before='## Dans le cloud')

d = D(680, 290)
for i, (n, ip) in enumerate([('conteneur A', '10.0.0.2'), ('conteneur B', '10.0.0.3')]):
    x = 40 + i * 260
    d.zone(x, 14, 220, 82, f'netns {n}', k='c')
    d.box(x + 40, 40, 140, 40, f'eth0 {ip}', k='c', tk='s', d=i)
    d.arrow([(x + 110, 80), (x + 110, 136)], color='c', start=True, label='veth', at=0.5, dy=4)
d.box(40, 138, 480, 44, 'pont docker0', 'un switch virtuel sur l\'hôte', d=2)
d.box(560, 138, 106, 44, 'iptables', 'SNAT', k='a', d=3)
d.box(400, 222, 266, 52, 'eth0 de l\'hôte', '→ Internet', d=4)
d.arrow([(520, 160), (558, 160)])
d.arrow([(613, 182), (613, 220)], color='a')
d.text(40, 240, 'A et B se parlent directement par le pont.', 's', anchor='start')
d.text(40, 256, 'Pour sortir, la source est réécrite avec l\'IP de l\'hôte.', 's', anchor='start')
put(f'{M}/07-reseau-des-conteneurs.md', 'bridge', figure(d, 'Le réseau bridge de Docker', 'Chaque conteneur a son namespace réseau, relié au pont par une paire veth.'), fence='conteneur A        conteneur B')

d = D(680, 260)
for i, (n, ipn, pods) in enumerate([('nœud 1', '10.10.16.11', ['pod A 10.244.1.5', 'pod B 10.244.1.6']), ('nœud 2', '10.10.16.12', ['pod C 10.244.2.7'])]):
    x = 14 + i * 360
    d.zone(x, 14, 292, 232, f'{n} · {ipn}', k='c')
    for j, p in enumerate(pods):
        d.box(x + 20, 46 + j * 58, 170, 44, p, k='c', tk='s', d=i + j)
        d.arrow([(x + 190, 68 + j * 58), (x + 230, 68 + j * 58), (x + 230, 160)], start=False)
    d.box(x + 150, 160, 120, 40, 'cni0 / eBPF', tk='s', d=2)
d.arrow([(284, 190), (522, 190)], color='c', k='flow thick', start=True)
d.text(400, 180, 'overlay (VXLAN)', 's')
d.text(400, 214, 'ou routage direct', 's')
d.text(340, 244, 'règle : chaque pod joint chaque pod, sans NAT', 'ct')
put(f'{M}/08-reseau-kubernetes-et-cni.md', 'cni', figure(d, 'Le modèle réseau de Kubernetes', 'Le CNI (Calico, Cilium, Flannel…) donne une IP à chaque pod et fait le lien entre les nœuds.'), fence='nœud 1 (10.10.16.11)')

# ============================== DEVOPS ==============================
M = 'devops'

d = D(680, 250)
def commits(xs, y, k='c', labels=None, dd=0):
    for i, x in enumerate(xs):
        d.circle(x, y, 9, k=k, d=dd + i)
        if labels:
            d.text(x, y + 26, labels[i], 's')
d.text(170, 22, 'merge', 't')
d.line(40, 70, 300, 70, k='court')
commits([50, 100, 150], 70, k='', labels=['A', 'B', 'C'])
d.arrow(f'M100 70 C 120 130, 140 130, 160 130', k='')
commits([170, 220], 130, labels=['D', 'E'], dd=1)
d.arrow(f'M220 130 C 240 130, 250 70, 262 70', color='c')
d.circle(270, 70, 11, k='a', d=3)
d.text(270, 48, 'M', 'at')
d.text(170, 186, 'historique fidèle, un commit de fusion', 's')
d.line(340, 30, 340, 220, k='grid')
d.text(510, 22, 'rebase', 't')
d.line(380, 70, 660, 70, k='court')
commits([390, 440, 490], 70, k='', labels=['A', 'B', 'C'])
commits([550, 600], 70, labels=["D'", "E'"], dd=1)
commits([480, 530], 130, k='', dd=0)
d.raw('<circle cx="480" cy="130" r="9" class="dg-dot" style="opacity:.35"/><circle cx="530" cy="130" r="9" class="dg-dot" style="opacity:.35"/>')
d.text(505, 160, 'D et E abandonnés', 's')
d.text(510, 186, 'historique linéaire, nouveaux SHA', 's')
d.h = 210
put(f'{M}/01-git-avance.md', 'merge-rebase', figure(d, 'Merge et rebase', 'Le rebase rejoue D et E sur C : ce sont de nouveaux commits, d\'où le push forcé.'), before='> **À retenir.**')

d = D(680, 230)
stages = [('commit', '', ''), ('lint + tests', 'quelques min', 'c'), ('build', 'image:3f2a9c1', 'c'), ('scan', 'deps, image', 'c'), ('staging', 'tests intégr.', ''), ('prod', 'même image', 'a')]
for i, (t, s, k) in enumerate(stages):
    x = 14 + i * 111
    d.box(x, 100, 98, 54, t, s or None, k=k, d=i)
    if i:
        d.arrow([(x - 13, 127), (x - 1, 127)], color='c')
def brace(x0, x1, y, label, k):
    d.arrow([(x0, y), (x1, y)], color=k, start=True)
    d.text((x0 + x1) / 2, y - 8, label, {'c': 'ct', 'a': 'at', 'ok': 'okt'}[k])
brace(125, 445, 80, 'CI : à chaque commit', 'c')
brace(125, 556, 40, 'Continuous Delivery : prêt pour la prod, bouton manuel', 'ok')
brace(125, 666, 184, 'Continuous Deployment : jusqu\'en prod, automatiquement', 'a')
d.h = 200
put(f'{M}/02-principes-ci-cd.md', 'niveaux', figure(d, 'CI, Continuous Delivery, Continuous Deployment', 'La différence se joue sur la dernière marche : la mise en prod est-elle manuelle ou automatique ?'), fence='CI                     Continuous Delivery')

d = D(680, 250)
cols = [('test', [('lint', ''), ('unit', '')]), ('build', [('build', 'c'), ('docker', 'c')]), ('deploy', [('deploy-prod', 'a')])]
pos = {}
for ci, (st, jobs) in enumerate(cols):
    x = 30 + ci * 230
    d.zone(x - 14, 14, 200, 222, f'stage {st}')
    for j, (job, k) in enumerate(jobs):
        y = 50 + j * 74
        d.box(x, y, 172, 50, job, 'manuel · main' if job == 'deploy-prod' else None, k=k, d=ci * 2 + j)
        pos[job] = (x, y)
d.arrow([(202, 75), (258, 75)], color='c', label='needs', dy=-6)
d.arrow([(432, 75), (488, 75)], color='c', label='needs', dy=-6)
d.text(116, 220, 'cache : node_modules', 's')
d.text(346, 220, 'artifacts : dist/', 's')
d.text(576, 220, 'resource_group', 's')
put(f'{M}/03-gitlab-ci.md', 'dag', figure(d, 'Étapes et needs dans GitLab CI', 'Avec needs, build démarre dès que lint a fini, sans attendre unit.'), before='## Les mots-clés à connaître')

d = D(680, 250)
d.box(14, 90, 150, 70, 'nœud de contrôle', 'ansible-playbook\nton poste ou la CI', k='c', d=0)
d.box(200, 14, 140, 52, 'inventory', 'groupes d\'hôtes', d=1)
d.box(200, 184, 140, 52, 'playbook + rôles', 'l\'état voulu', d=1)
d.arrow([(164, 110), (182, 110), (182, 40), (198, 40)])
d.arrow([(164, 140), (182, 140), (182, 210), (198, 210)])
d.zone(390, 14, 276, 222, 'serveurs (aucun agent)', k='c')
for g, (gn, hosts) in enumerate([('web', ['web01', 'web02']), ('db', ['db01'])]):
    y = 44 + g * 104
    d.text(410, y + 4, gn, 'zl', anchor='start')
    for h, hn in enumerate(hosts):
        d.box(410 + h * 124, y + 12, 112, 44, hn, k='c', tk='s', d=2 + g)
d.arrow([(342, 125), (388, 125)], color='c', k='flow thick', label='SSH', dy=-8)
d.text(528, 222, 'tâche relancée → ok, pas changed', 's')
put(f'{M}/04-ansible.md', 'archi', figure(d, 'Comment Ansible travaille', 'Ansible pousse des modules Python en SSH, les exécute et les supprime. Il suffit de Python sur les serveurs.'), before='## Un rôle simple')

d = D(680, 260)
d.box(14, 20, 150, 52, 'dépôt app', 'code source', d=0)
d.box(214, 20, 160, 52, 'CI', 'build + push', d=1)
d.box(424, 20, 242, 52, 'registre', 'api:3f2a9c1', d=2)
d.arrow([(164, 46), (212, 46)])
d.arrow([(374, 46), (422, 46)])
d.box(214, 120, 160, 56, 'dépôt manifests', 'image: api:3f2a9c1', k='c', d=3)
d.arrow([(294, 72), (294, 118)], color='c', label='commit du tag', at=0.5, dy=4)
d.zone(424, 104, 242, 140, 'cluster', k='c')
d.box(440, 130, 210, 52, 'ArgoCD', 'compare Git et cluster', k='c', d=4)
d.box(440, 194, 210, 38, 'Deployment api', tk='s', d=5)
d.arrow([(438, 148), (374, 148)], color='c', k='flow', label='pull', dy=-6)
d.arrow([(545, 182), (545, 192)], color='c')
d.text(110, 210, 'la CI n\'a aucun accès', 's')
d.text(110, 224, 'au cluster', 's')
put(f'{M}/05-gitops-argocd.md', 'flux', figure(d, 'Le flux GitOps', 'ArgoCD tire l\'état voulu depuis Git et corrige toute différence dans le cluster.'), fence='dépôt app ──► CI')

d = D(680, 250)
for i, t in enumerate(['api', 'worker', 'node-exporter']):
    d.box(14, 20 + i * 70, 140, 50, t, '/metrics', d=i)
    d.arrow([(256, 120), (210, 120), (210, 45 + i * 70), (156, 45 + i * 70)], color='c', end=True)
d.text(212, 236, 'scrape (pull)', 's')
d.box(258, 88, 150, 64, 'Prometheus', 'stocke, évalue\nles règles', k='c', d=3)
d.box(470, 20, 196, 52, 'Grafana', 'tableaux de bord', d=4)
d.box(470, 100, 196, 52, 'Alertmanager', 'regroupe, route', k='a', d=4)
d.box(470, 180, 196, 52, 'Slack, PagerDuty', tk='t', d=5)
d.arrow([(408, 110), (440, 110), (440, 46), (468, 46)], label='PromQL', at=0.4, dy=-6)
d.arrow([(408, 126), (468, 126)], color='a')
d.arrow([(568, 152), (568, 178)], color='a')
put(f'{M}/06-observabilite.md', 'prometheus', figure(d, 'L\'architecture Prometheus', 'Prometheus vient chercher les métriques. Grafana les affiche, Alertmanager prévient.'), before="## PromQL, l'essentiel")

d = D(680, 280)
d.text(110, 22, 'rolling update', 't')
rows = [['v1', 'v1', 'v1'], ['v2', 'v1', 'v1'], ['v2', 'v2', 'v1'], ['v2', 'v2', 'v2']]
for r, row in enumerate(rows):
    for c, v in enumerate(row):
        d.box(30 + c * 56, 40 + r * 52, 48, 40, v, k='c' if v == 'v2' else 'off', tk='s', d=r)
d.text(110, 262, 'un pod à la fois', 's')
d.line(226, 30, 226, 250, k='grid')
d.text(340, 22, 'blue / green', 't')
d.box(280, 50, 120, 44, 'routeur', k='c', d=0)
d.box(250, 150, 80, 50, 'blue', 'v1', k='off', d=1)
d.box(350, 150, 80, 50, 'green', 'v2', k='c', d=2)
d.arrow([(320, 94), (290, 148)], k='dash', end=False)
d.arrow([(360, 94), (390, 148)], color='c', k='thick')
d.text(340, 236, 'bascule d\'un coup,', 's')
d.text(340, 250, 'retour immédiat', 's')
d.line(456, 30, 456, 250, k='grid')
d.text(570, 22, 'canary', 't')
d.box(510, 50, 120, 44, 'routeur', k='c', d=0)
d.box(480, 150, 90, 50, 'v1', '95 %', k='off', d=1)
d.box(590, 150, 76, 50, 'v2', '5 %', k='a', d=2)
d.arrow([(550, 94), (525, 148)], k='thick')
d.arrow([(600, 94), (628, 148)], color='a')
d.text(570, 236, 'on observe, puis', 's')
d.text(570, 250, '25 %, 50 %, 100 %', 's')
put(f'{M}/07-strategies-deploiement.md', 'strategies', figure(d, 'Trois façons de déployer', 'Le rolling update est le défaut de Kubernetes. Blue/green et canary demandent un routage plus fin.'), before='## Rolling update bien réglé')

d = D(680, 260)
X = lambda day: 60 + day * 19
Y = lambda pct: 30 + (100 - pct) * 1.8
d.line(X(0), Y(0), X(30), Y(0), k='court')
d.line(X(0), Y(0), X(0), Y(100), k='court')
for p in (0, 50, 100):
    d.text(X(0) - 8, Y(p) + 4, f'{p} %', 's', anchor='end')
for day in (0, 10, 20, 30):
    d.text(X(day), Y(0) + 18, f'j{day}', 's')
d.arrow(f'M{X(0)} {Y(100)} L {X(30)} {Y(0)}', k='dash', end=False)
d.text(X(21), Y(22), 'rythme régulier', 's', anchor='start')
d.arrow(f'M{X(0)} {Y(100)} L {X(8)} {Y(88)} L {X(9)} {Y(40)} L {X(16)} {Y(28)} L {X(17.5)} {Y(0)}', color='a', k='thick', draw=True, end=False)
d.circle(X(9), Y(40), 5, k='a')
d.text(X(9) + 12, Y(40) + 20, 'incident : alerte burn rate', 'at', anchor='start')
d.text(X(17.5) - 6, Y(0) - 22, 'budget épuisé :', 'at', anchor='end')
d.text(X(17.5) - 6, Y(0) - 7, 'gel des features', 'at', anchor='end')
d.text(X(0) + 4, 20, 'budget d\'erreur restant · SLO 99,9 % sur 30 jours (43 min)', 's', anchor='start')
put(f'{M}/08-pratiques-sre.md', 'budget', figure(d, 'La consommation du budget d\'erreur', 'Une alerte sur la vitesse de consommation prévient bien avant que le budget soit vide.'), before='## Les rituels')

# ============================== JAPANESE ==============================
M = 'japonais'

d = D(680, 330)
vow = ['a', 'i', 'u', 'e', 'o']
rows = [('', 'あいうえお'), ('k', 'かきくけこ'), ('s', None), ('t', None), ('n', None), ('h', None), ('m', None), ('y', None), ('r', None), ('w', None)]
for j, v in enumerate(vow):
    d.text(110 + j * 60, 26, v, 'zl')
for i, (c, kana) in enumerate(rows):
    y = 36 + i * 29
    d.text(60, y + 19, c or '∅', 's')
    for j in range(5):
        if kana:
            d.box(84 + j * 60, y, 52, 25, kana[j], k='c', rx=5, tk='tl', d=i * 5 + j)
        else:
            d.box(84 + j * 60, y, 52, 25, rx=5, k='off')
d.text(530, 60, 'tu commences ici', 'ct')
d.text(530, 78, '5 voyelles, puis', 's')
d.text(530, 92, 'consonne + voyelle', 's')
d.text(530, 160, 'chaque ligne suit', 's')
d.text(530, 174, 'le même ordre :', 's')
d.text(530, 188, 'a · i · u · e · o', 'ct')
d.text(530, 300, 'les autres lignes : fiches suivantes', 's')
put(f'{M}/01-voyelles-et-ligne-ka.md', 'gojuon', figure(d, 'Le tableau des kana (gojūon)', 'Tout le syllabaire tient dans cette grille. Les fiches suivantes remplissent les autres lignes.'), before='## Les cinq voyelles')

d = D(680, 230)
pairs = [('か', 'が', 'k → g'), ('さ', 'ざ', 's → z'), ('た', 'だ', 't → d'), ('は', 'ば', 'h → b')]
for i, (a, b, s) in enumerate(pairs):
    x = 20 + i * 130
    d.box(x, 30, 50, 50, a, tk='tl', d=i)
    d.box(x + 70, 30, 50, 50, b, k='c', tk='tl', d=i)
    d.arrow([(x + 50, 55), (x + 68, 55)], color='c')
    d.text(x + 60, 102, s, 's')
d.box(540, 30, 50, 50, 'は', tk='tl', d=4)
d.box(610, 30, 50, 50, 'ぱ', k='a', tk='tl', d=4)
d.arrow([(590, 55), (608, 55)], color='a')
d.text(600, 102, 'h → p', 's')
d.text(260, 144, '゛ dakuten : la consonne devient sonore', 'ct')
d.text(600, 144, '゜ handakuten', 'at')
d.text(600, 160, 'seulement sur la ligne h', 's')
d.text(340, 206, 'la forme de base ne change pas : on ajoute juste le signe en haut à droite', 's')
put(f'{M}/01-dakuten-et-combinaisons.md', 'dakuten', figure(d, 'Ce que changent ゛ et ゜', 'Cinq lignes de base donnent cinq nouvelles lignes, sans rien apprendre de nouveau à écrire.'), before='## Les combinaisons avec')

d = D(680, 230)
d.text(170, 24, '二十三 = 23', 'tl')
blocks = [('二', '2', 'c'), ('十', '× 10', ''), ('三', '+ 3', 'c')]
for i, (k, v, kk) in enumerate(blocks):
    d.box(50 + i * 84, 46, 70, 70, k, k=kk, tk='big', d=i)
    d.text(85 + i * 84, 140, v, 'ct' if kk else 's', d=i)
d.text(170, 178, 'にじゅうさん', 't')
d.line(340, 20, 340, 210, k='grid')
d.text(510, 24, '三百五十 = 350', 'tl')
blocks = [('三', '3', 'c'), ('百', '× 100', ''), ('五', '+ 5', 'c'), ('十', '× 10', '')]
for i, (k, v, kk) in enumerate(blocks):
    d.box(370 + i * 72, 46, 62, 70, k, k=kk, tk='big', d=i + 3)
    d.text(401 + i * 72, 140, v, 'ct' if kk else 's', d=i + 3)
d.text(510, 178, 'さんびゃくごじゅう', 't')
d.text(510, 200, '百 se prononce びゃく après 三', 's')
put(f'{M}/04-nombres-et-jours.md', 'composition', figure(d, 'Composer les nombres', 'Comme une multiplication suivie d\'une addition : chiffre, puissance de dix, chiffre suivant.'), before='## Les jours de la semaine')

d = D(680, 230)
parts = [('わたし', 'moi', 'thème', 'c', 130), ('は', 'wa', 'particule', 'a', 66), ('がくせい', 'étudiant', 'commentaire', 'c', 150), ('です', 'desu', 'c\'est', '', 90), ('か', 'ka', '?', 'ok', 60)]
x = 40
for i, (jp, rom, role, k, w) in enumerate(parts):
    d.box(x, 50, w, 64, jp, rom, k=k, d=i)
    d.text(x + w / 2, 36, role, 'zl', d=i)
    x += w + 12
d.text(340, 150, 'わたし は がくせい です。 → Je suis étudiant.', 't')
d.text(340, 174, 'わたし は がくせい です か。 → Suis-je étudiant ?', 's')
d.text(340, 206, 'は s\'écrit ha mais se prononce wa quand c\'est une particule', 'at')
put(f'{M}/05-la-phrase-de-base.md', 'structure', figure(d, 'La structure A は B です', 'Le thème, la particule は, le commentaire, puis です. Ajouter か en fait une question.'), before='## Les variantes')

d = D(680, 220)
d.box(285, 40, 110, 110, '山', k='c', tk='big', d=0)
d.text(340, 176, 'montagne', 's')
d.box(30, 60, 190, 70, 'やま (kun)', 'lecture japonaise\nquand il est seul', d=1)
d.box(460, 60, 190, 70, 'サン (on)', 'lecture chinoise\ndans les composés', k='c', d=2)
d.arrow([(283, 95), (222, 95)])
d.arrow([(397, 95), (458, 95)], color='c')
d.text(125, 160, '山 に のぼる : monter sur la montagne', 's')
d.text(555, 160, '富士山 : ふじさん', 'ct')
put(f'{M}/03-premiers-kanji.md', 'lectures', figure(d, 'Les deux lectures d\'un kanji', 'Retiens le kanji avec un mot de chaque lecture, plutôt que les lectures seules.'), before='## Les dix premiers')
print('rest ok')
