from svg import D, figure
from inject import put

M = 'openstack'

# --- 02 : architecture ------------------------------------------------
d = D(680, 340)
d.box(14, 92, 96, 44, 'utilisateurs', d=0)
d.box(134, 92, 112, 44, 'VIP HAProxy', k='a', d=1)
d.arrow([(110, 114), (132, 114)])
d.zone(270, 14, 396, 172, 'contrôleurs ×3', k='c')
d.box(286, 40, 364, 56, 'API', 'keystone, nova-api, neutron-server, glance,\ncinder, placement, heat, octavia…', k='c', d=2)
d.box(286, 110, 172, 62, 'planification', 'nova-scheduler\nnova-conductor', d=3)
d.box(472, 110, 178, 62, 'état partagé', 'Galera · RabbitMQ\nmemcached · OVN', d=4)
d.arrow([(246, 114), (262, 114), (262, 68), (284, 68)], color='a')
d.zone(14, 222, 310, 106, 'computes ×N')
d.box(30, 248, 278, 64, 'nova-compute · libvirt/KVM', 'ovn-controller · OVS\nagent metadata', k='c', d=5)
d.zone(376, 222, 290, 106, 'stockage Ceph')
d.box(392, 248, 258, 64, 'MON · OSD · MGR', 'ou hyperconvergé\nsur les computes', d=6)
d.arrow([(372, 186), (372, 204), (169, 204), (169, 246)], color='c', label='ordres via RabbitMQ', at=0.5, dy=-6)
d.arrow([(560, 186), (560, 246)], label='', d=6)
d.text(568, 218, 'API', 's', anchor='start')
d.arrow([(310, 290), (390, 290)], start=True, color='c', label='RBD', dy=-8)
put(f'{M}/02-architecture-d-un-cloud.md', 'archi', figure(d, "Les rôles des machines d'un cloud OpenStack", "Les contrôleurs décident, les computes font tourner les VM, Ceph garde les disques."), fence='Contrôleurs (x3)')

# --- 02 : trajet d'une création d'instance ----------------------------
d = D(680, 350)
row = [('openstack\nserver create', '', ''), ('nova-api', 'jeton, quotas,\nBUILD en base', 'c'), ('nova-conductor', 'orchestre', 'c'), ('nova-scheduler', 'choisit l\'hôte', 'c'), ('nova-compute', 'sur l\'hôte choisi', 'a')]
for i, (t, s, k) in enumerate(row):
    x = 14 + i * 134
    if s:
        d.box(x, 30, 118, 62, t, s, k=k, d=i)
    else:
        d.box(x, 30, 118, 62, t, k=k, d=i)
    if i:
        d.arrow([(x - 16, 61), (x - 2, 61)], color='c')
d.text(484, 24, 'via RabbitMQ', 's')
d.box(14, 132, 118, 48, 'Keystone', 'jeton + catalogue', d=1)
d.arrow([(73, 92), (73, 130)], start=True)
d.box(416, 132, 118, 48, 'Placement', 'qui a la place ?', d=4)
d.arrow([(475, 92), (475, 130)], start=True)
d.arrow([(615, 92), (615, 210)], color='a', end=False)
d.arrow([(90, 210), (615, 210)], color='a', end=False)
low = [('Glance', 'image (ou clone RBD)'), ('Neutron', 'port + réseau OVN'), ('Cinder', 'volume si boot\nsur volume'), ('libvirt', 'démarre la VM KVM')]
for i, (t, s) in enumerate(low):
    x = 30 + i * 162
    d.box(x, 236, 140, 56, t, s, k='c', d=5 + i)
    d.arrow([(x + 70, 210), (x + 70, 234)], color='a')
d.text(340, 322, 'statut ACTIVE, puis cloud-init lit les métadonnées (clé SSH, user data)', 'ct', d=9)
put(f'{M}/02-architecture-d-un-cloud.md', 'trajet', figure(d, "Le trajet d'une création d'instance", "Quand une création échoue, ce trajet dit dans quels logs chercher : nova-api, puis scheduler, puis compute."), fence='1. openstack server create')

# --- 08 : le scheduling en entonnoir ----------------------------------
d = D(680, 340)
stages = [('demande', 'flavor m1.large (4 vCPU, 8 Go, 40 Go) + image + zone', 600, ''),
          ('1. Placement', 'qui a assez de ressources libres ? → 37 hôtes', 500, 'c'),
          ('2. Filtres', 'zone, agrégat, affinité, NUMA… → 12 hôtes', 380, 'c'),
          ('3. Poids', '→ compute-07', 220, 'a')]
for i, (t, s, w, k) in enumerate(stages):
    y = 14 + i * 76
    h = 60 if '\n' in s else 50
    d.box(340 - w / 2, y, w, h, t, s, k=k, d=i)
    if i:
        d.arrow([(340, y - 18), (340, y - 2)], color='c')
d.text(340, 326, "allocation enregistrée dans Placement, puis nova-compute crée l'instance", 's', d=4)
put(f'{M}/08-nova-placement-et-scheduling.md', 'entonnoir', figure(d, "Le choix d'un hôte en trois étapes", "Placement élimine sur les ressources, les filtres sur les règles, les poids classent ceux qui restent."), fence='Demande : flavor m1.large')

# --- 09 : un projet type ----------------------------------------------
d = D(680, 350)
d.box(170, 14, 340, 50, 'réseau externe « public »', 'provider, VLAN 200 · 203.0.113.0/24', k='a', d=0)
d.box(270, 104, 140, 50, 'routeur r1', 'SNAT 203.0.113.10', k='c', d=1)
d.arrow([(340, 64), (340, 102)], start=True, color='a')
d.zone(14, 196, 316, 140, 'app-net · Geneve · 10.0.1.0/24', k='c')
d.zone(350, 196, 316, 140, 'db-net · Geneve · 10.0.2.0/24', k='c')
d.arrow([(300, 154), (300, 174), (172, 174), (172, 194)], color='c', label='10.0.1.1', at=0.5, dy=-6)
d.arrow([(380, 154), (380, 174), (508, 174), (508, 194)], color='c', label='10.0.2.1', at=0.5, dy=-6)
d.box(34, 240, 130, 52, 'web1', '10.0.1.12', d=2)
d.box(182, 240, 130, 52, 'web2', '10.0.1.13', d=3)
d.box(443, 240, 130, 52, 'db1', '10.0.2.20', d=4)
d.arrow('M170 50 C 120 50, 110 150, 100 238', color='a', k='dash')
d.text(140, 100, 'IP flottante', 's', anchor='start')
d.text(140, 114, '203.0.113.25', 's', anchor='start')
d.text(140, 128, '→ web1', 's', anchor='start')
put(f'{M}/09-neutron-les-concepts.md', 'projet', figure(d, 'Un projet type dans Neutron', "Les VM n'ont que des IP privées ; le routeur fait le SNAT vers l'extérieur et l'IP flottante rend web1 joignable."), fence='Réseau externe « public »')

# --- 10 : OVN sous le capot -------------------------------------------
d = D(680, 430)
d.box(40, 14, 260, 40, 'neutron-server (ML2/OVN)', k='c', d=0)
d.box(40, 90, 260, 58, 'OVN Northbound DB', 'switches et routeurs logiques,\nACL, NAT, load balancers', d=1)
d.box(40, 184, 260, 52, 'OVN Southbound DB', 'flux logiques, chassis,\nport bindings', d=2)
d.arrow([(170, 54), (170, 88)], color='c'); d.text(182, 76, 'écrit', 's', anchor='start')
d.arrow([(170, 148), (170, 182)], color='c'); d.text(182, 170, 'ovn-northd traduit', 's', anchor='start')
d.text(340, 40, 'ce que veut l\'utilisateur', 'zl', anchor='start')
d.text(340, 124, 'le réseau décrit logiquement', 'zl', anchor='start')
d.text(340, 214, 'le réseau traduit pour les hôtes', 'zl', anchor='start')
d.zone(14, 266, 466, 152, 'hôte (chassis)', k='c')
d.box(30, 294, 150, 48, 'ovn-controller', k='c', d=3)
d.arrow([(105, 236), (105, 292)], color='c'); d.text(114, 262, 'lit', 's', anchor='start')
d.box(230, 294, 150, 48, 'OVS br-int', 'règles OpenFlow', d=4)
d.arrow([(180, 318), (228, 318)], color='c')
d.box(230, 360, 150, 44, 'br-ex', 'patch port', d=5)
d.arrow([(305, 342), (305, 358)])
d.box(526, 294, 140, 48, 'autres hôtes', d=6)
d.arrow([(380, 318), (524, 318)], start=True, color='a', k='flow', label='tunnels Geneve', dy=-8)
d.box(526, 360, 140, 44, 'réseau externe', 'interface physique', k='a', d=7)
d.arrow([(380, 382), (524, 382)], color='a')
put(f'{M}/10-neutron-ovn-sous-le-capot.md', 'ovn', figure(d, 'De Neutron à OpenFlow avec OVN', "Une règle qui manque sur un hôte se cherche dans l'ordre : NB, SB, puis OpenFlow sur br-int."), fence='OVN Northbound DB')

# --- 12 : placement des données Ceph -----------------------------------
d = D(680, 290)
d.box(40, 24, 190, 54, 'objet', "4 Mo d'un disque RBD", d=0)
d.box(300, 24, 190, 54, 'placement group', 'du pool « volumes »', k='c', d=1)
d.arrow([(230, 51), (298, 51)], color='c', label='hachage', dy=-8)
d.text(506, 46, 'CRUSH : 3 copies,', 's', anchor='start')
d.text(506, 60, 'une par hôte', 's', anchor='start')
for i, (h, o) in enumerate([('hôte A', 'OSD.4'), ('hôte B', 'OSD.11'), ('hôte C', 'OSD.19')]):
    x = 14 + i * 222
    d.zone(x, 136, 208, 96, h)
    d.box(x + 24, 164, 160, 48, o, 'une copie', k='c', d=2 + i)
    d.arrow([(395, 78), (395, 110), (x + 104, 110), (x + 104, 162)], color='c')
d.text(340, 266, 'perdre un hôte ne perd aucune donnée : Ceph recrée la copie manquante ailleurs', 's', d=5)
put(f'{M}/12-ceph-pour-openstack.md', 'crush', figure(d, 'Comment Ceph place un objet', 'Personne ne garde de table « objet → disque » : CRUSH recalcule la position à chaque accès.'), fence='placement group (PG)')

# --- 15 : l'arbre d'un load balancer ----------------------------------
d = D(680, 340)
d.box(14, 20, 110, 44, 'clients', d=0)
d.box(180, 14, 300, 56, 'load balancer « web-lb »', 'VIP 10.20.0.50\nIP flottante 203.0.113.12', k='a', d=1)
d.arrow([(124, 42), (178, 42)], color='a')
d.box(180, 98, 300, 50, 'listener HTTP :80', 'ou HTTPS :443 + certificat Barbican', k='c', d=2)
d.box(180, 176, 300, 50, 'pool « web »', 'ROUND_ROBIN, LEAST_CONNECTIONS…', k='c', d=3)
d.arrow([(330, 70), (330, 96)], color='c')
d.arrow([(330, 148), (330, 174)], color='c')
d.box(506, 176, 160, 50, 'health monitor', 'GET /health, 5 s', d=4)
d.line(480, 201, 506, 201, k='grid')
d.arrow([(330, 226), (330, 248)], color='c', end=False)
d.arrow([(110, 248), (550, 248)], color='c', end=False)
for i, ip in enumerate(['10.20.0.11:80', '10.20.0.12:80', '10.20.0.13:80']):
    x = 40 + i * 220
    d.box(x, 272, 140, 48, 'membre', ip, d=5 + i)
    d.arrow([(x + 70, 248), (x + 70, 270)], color='c')
d.arrow([(640, 226), (640, 296), (622, 296)], k='dash')
put(f'{M}/15-octavia-le-load-balancing.md', 'arbre', figure(d, "L'arbre d'un load balancer Octavia", "Le health monitor retire du pool un membre qui ne répond plus, sans intervention."), fence='load balancer « web-lb »')
print('ok')
