from svg import D, figure
from inject import put

M = 'kubernetes'

# 1. Composants du cluster ---------------------------------------------
d = D(680, 330)
d.box(14, 140, 92, 48, 'kubectl', 'toi', d=0)
d.zone(124, 14, 268, 302, 'control plane', k='c')
d.box(142, 44, 112, 58, 'scheduler', 'place les pods', d=1)
d.box(264, 44, 112, 58, 'controller-\nmanager', 'boucles', d=1)
d.box(142, 136, 234, 56, 'kube-apiserver', 'point d\'entrée unique', k='c', d=2)
d.box(142, 238, 112, 58, 'etcd', 'état du cluster', k='a', d=3)
d.box(264, 238, 112, 58, 'cloud-\ncontroller', 'optionnel', k='ghost', d=3)
d.arrow([(106, 164), (140, 164)], color='c', k='flow')
d.arrow([(198, 104), (198, 134)], start=True)
d.arrow([(320, 104), (320, 134)], start=True)
d.arrow([(198, 194), (198, 236)], color='a', start=True)
d.arrow([(320, 194), (320, 236)], k='dash', start=True)
d.zone(410, 14, 256, 302, 'nœuds (workers)')
for i, y in enumerate((40, 178)):
    d.zone(424, y, 228, 124, f'nœud {i + 1}')
    d.box(436, y + 30, 96, 36, 'kubelet', k='c', d=4 + i)
    d.box(542, y + 30, 98, 36, 'kube-proxy', d=4 + i)
    d.box(436, y + 76, 96, 36, 'containerd', d=4 + i)
    for j in range(3):
        d.circle(566 + j * 26, y + 94, 9, k='c', d=5 + i)
    d.text(592, y + 120, 'pods', 's')
d.arrow([(436, 88), (398, 88), (398, 156), (378, 156)], color='c')
d.arrow([(436, 226), (404, 226), (404, 172), (378, 172)], color='c')
put(f'{M}/01-composants-du-cluster.md', 'architecture', figure(d, 'Architecture d\'un cluster Kubernetes', 'Tout passe par l\'API server : aucun composant ne parle directement à un autre, ni à etcd.'), before='## Le control plane')

# 2. Trajet d'une requête : le hub API server ---------------------------
d = D(680, 300)
d.box(250, 122, 180, 56, 'kube-apiserver', 'stocke et notifie', k='c', d=0)
d.box(20, 124, 120, 52, 'kubectl apply', 'Deployment', d=0)
d.box(280, 236, 120, 50, 'etcd', k='a', d=1)
d.box(40, 18, 170, 52, 'controller-manager', 'crée ReplicaSet et Pods', d=2)
d.box(470, 18, 170, 52, 'scheduler', 'choisit un nœud', d=3)
d.box(530, 124, 130, 52, 'kubelet', 'sur le nœud choisi', d=4)
d.box(530, 236, 130, 50, 'containerd', 'lance les conteneurs', d=5)
steps = [
    ([(140, 150), (248, 150)], '1', (194, 150)),
    ([(340, 180), (340, 234)], '2', (340, 207)),
    ([(210, 60), (290, 120)], '3', (250, 90)),
    ([(470, 60), (392, 120)], '4', (431, 90)),
    ([(432, 150), (528, 150)], '5', (480, 150)),
    ([(595, 178), (595, 234)], '6', (595, 206)),
]
for i, (pts, n, (cx, cy)) in enumerate(steps):
    d.arrow(pts, color='c', start=(n in '345'), d=i)
    d.circle(cx, cy, 10, k='c', d=i)
    d.text(cx, cy + 4, n, 'w', d=i)
d.text(250, 112, 'watch', 's', anchor='end')
d.text(440, 112, 'watch', 's', anchor='start')
put(f'{M}/01-trajet-d-une-requete.md', 'hub', figure(d, 'Le trajet d\'un kubectl apply', '1 la requête arrive, 2 elle est enregistrée, 3 les contrôleurs créent les Pods, 4 le scheduler leur donne un nœud, 5 le kubelet le voit, 6 il lance les conteneurs.'), before='## 1. L\'API server reçoit la requête')

# 3. Pod multi-conteneurs -----------------------------------------------
d = D(680, 262)
d.zone(16, 12, 648, 238, 'pod', k='c')
d.box(36, 56, 104, 50, 'init 1', 'attendre la DB', d=0)
d.box(160, 56, 104, 50, 'init 2', 'migrations', d=1)
d.arrow([(140, 81), (158, 81)])
d.text(150, 128, 'un par un, chacun doit finir avant le suivant', 's')
d.arrow([(264, 81), (300, 81), (300, 72), (320, 72)], color='c')
d.box(322, 46, 150, 50, 'app', 'le conteneur principal', k='c', d=2)
d.box(322, 112, 150, 50, 'sidecar', 'logs, proxy…', d=3)
d.box(504, 46, 140, 116, 'volume\npartagé', 'emptyDir', k='ghost', d=4)
d.arrow([(472, 71), (502, 71)], k='dash', start=True)
d.arrow([(472, 137), (502, 137)], k='dash', start=True)
d.box(36, 186, 608, 44, 'réseau partagé : une seule IP, les conteneurs se parlent en localhost', k='off', d=5)
put(f'{M}/02-pods-multi-conteneurs.md', 'pod', figure(d, 'Ce que contient et partage un pod', 'Les init containers préparent, puis l\'app et ses sidecars tournent ensemble avec le même réseau et les mêmes volumes.'), before='## Ce que partage un pod')

# 4. Probes sur une ligne de temps --------------------------------------
d = D(680, 230)
X0 = 150
lanes = [('startupProbe', 40), ('readinessProbe', 96), ('livenessProbe', 152)]
for name, y in lanes:
    d.text(20, y + 19, name, 't', anchor='start')
    d.line(X0, y + 14, 660, y + 14, k='grid')
def seg(x0, x1, y, k, t, dd):
    d.box(x0, y, x1 - x0, 28, t, k=k, rx=6, d=dd, tk='s')
seg(X0, 300, 40, 'c', 'démarrage lent toléré', 0)
d.text(306, 59, 'réussie : passe la main', 's', anchor='start')
seg(300, 450, 96, 'ok', 'reçoit du trafic', 1)
seg(450, 560, 96, 'a', 'retiré du Service', 2)
seg(560, 660, 96, 'ok', 'trafic', 3)
seg(300, 590, 152, 'ok', 'vivant', 1)
seg(590, 660, 152, 'a', 'restart', 4)
d.line(300, 30, 300, 190, k='grid')
d.arrow([(X0, 204), (660, 204)])
d.text(X0, 222, 'démarrage', 's', anchor='start')
d.text(660, 222, 'temps', 's', anchor='end')
put(f'{M}/02-probes-et-etats.md', 'timeline', figure(d, 'Les trois probes dans la vie d\'un conteneur', 'readiness décide du trafic, liveness décide du redémarrage. startup protège les démarrages lents.'), before='## Les trois probes')

# 5. Deployment > ReplicaSet > Pods --------------------------------------
d = D(680, 236)
d.box(16, 92, 150, 56, 'Deployment api', 'ce que tu écris', k='c', d=0)
d.box(226, 30, 180, 54, 'ReplicaSet api-7d9f', 'révision 2 · 3 réplicas', k='c', d=1)
d.box(226, 152, 180, 54, 'ReplicaSet api-5c8b', 'révision 1 · 0 réplica', k='off', d=1)
d.arrow([(166, 112), (196, 112), (196, 57), (224, 57)], color='c')
d.arrow([(166, 128), (196, 128), (196, 179), (224, 179)], k='dash')
for j in range(3):
    d.box(446 + j * 76, 36, 66, 42, 'pod', 'v2', k='c', d=2 + j, tk='t')
    d.box(446 + j * 76, 158, 66, 42, 'pod', 'v1', k='off', d=2 + j)
d.arrow([(406, 57), (444, 57)], color='c')
d.arrow([(406, 179), (444, 179)], k='dash')
d.text(560, 128, 'gardé pour le rollback', 's')
put(f'{M}/03-deployments-et-rolling-updates.md', 'chaine', figure(d, 'Deployment, ReplicaSets et Pods', 'Chaque changement du template crée un ReplicaSet. L\'ancien reste à 0 réplica pour pouvoir revenir en arrière.'), fence='Deployment api          (ce que tu écris)')

# 6. Service --------------------------------------------------------------
d = D(680, 236)
d.box(16, 92, 110, 52, 'client', 'autre pod', d=0)
d.box(176, 84, 180, 68, 'Service api', 'IP virtuelle stable\nselector app=api', k='c', d=1)
d.arrow([(126, 118), (174, 118)], color='c', k='flow')
pods = [(30, 'pod 10.244.1.12', 'Ready', 'c'), (96, 'pod 10.244.2.8', 'Ready', 'c'), (162, 'pod 10.244.3.4', 'pas Ready', 'off')]
for i, (y, t, s, k) in enumerate(pods):
    d.box(436, y, 200, 46, t, s, k=k, d=2 + i)
d.arrow([(356, 108), (396, 108), (396, 53), (434, 53)], color='c', k='flow')
d.arrow([(356, 118), (434, 118)], color='c', k='flow')
d.arrow([(356, 128), (396, 128), (396, 185), (420, 185)], color='a', k='dash', end=False)
d.text(426, 190, '✗', 'at')
d.text(266, 182, 'la liste des pods prêts', 's')
d.text(266, 196, 'est dans les EndpointSlices', 's')
put(f'{M}/04-services.md', 'service', figure(d, 'Un Service devant ses pods', 'Seuls les pods qui portent le bon label ET qui sont Ready reçoivent du trafic.'), fence='client ──► Service api')

# 7. Ingress --------------------------------------------------------------
d = D(680, 246)
d.box(10, 96, 92, 52, 'client', 'HTTPS', d=0)
d.box(130, 96, 110, 52, 'load balancer', 'du cloud', d=1)
d.box(268, 86, 150, 72, 'ingress controller', 'nginx, traefik…\nlit les règles', k='c', d=2)
d.arrow([(102, 122), (128, 122)], color='c', k='flow')
d.arrow([(240, 122), (266, 122)], color='c', k='flow')
d.box(462, 30, 120, 48, 'Service web', d=3)
d.box(462, 166, 120, 48, 'Service api', d=3)
d.arrow([(418, 108), (440, 108), (440, 54), (460, 54)], color='c', label='shop.fr /', at=0.5, dy=-8)
d.arrow([(418, 136), (440, 136), (440, 190), (460, 190)], color='c', label='shop.fr /api', at=0.5, dy=18)
for y in (54, 190):
    for j in range(2):
        d.circle(610 + j * 24, y, 8, k='c', d=4)
    d.arrow([(582, y), (598, y)])
d.text(343, 182, 'TLS terminé ici', 's')
put(f'{M}/04-ingress-et-gateway-api.md', 'ingress', figure(d, 'Le chemin d\'une requête HTTP jusqu\'aux pods', 'L\'Ingress ne fait que décrire des règles. C\'est le controller qui reçoit le trafic et l\'applique.'), before='## Ingress')

# 8. PV / PVC / StorageClass -----------------------------------------------
d = D(680, 230)
d.box(16, 140, 100, 52, 'Pod', 'monte data', d=0)
d.box(156, 140, 130, 52, 'PVC data', '20Gi · RWO · gp3', k='c', d=1)
d.box(326, 140, 130, 52, 'PV pvc-3f2a', 'le volume réel', k='c', d=4)
d.box(496, 140, 168, 52, 'disque EBS', 'chez le cloud', d=5)
d.arrow([(116, 166), (154, 166)])
d.arrow([(286, 166), (324, 166)], color='c', start=True, label='lié', dy=-8)
d.arrow([(456, 166), (494, 166)])
d.box(156, 24, 130, 52, 'StorageClass', 'gp3', d=2)
d.box(326, 24, 130, 52, 'driver CSI', 'ebs.csi.aws.com', d=3)
d.arrow([(221, 138), (221, 78)], k='dash', label='demande', at=0.5, dy=4)
d.arrow([(286, 50), (324, 50)])
d.arrow([(391, 78), (391, 138)], color='c', label='', d=4)
d.arrow([(456, 50), (580, 50), (580, 138)], k='dash')
d.text(518, 40, 'crée le disque', 's')
d.text(398, 112, 'crée le PV', 's', anchor='start')
put(f'{M}/06-pv-pvc-storageclass.md', 'provisioning', figure(d, 'Le provisionnement dynamique d\'un volume', 'Tu écris seulement le PVC. La StorageClass et le driver CSI créent le disque et le PV.'), fence='Pod ──► PVC data')

# 9. QoS -----------------------------------------------------------------
d = D(680, 250)
cols = [('BestEffort', 'ni request ni limit', None, None, 'a', 'évincé en premier'),
        ('Burstable', 'request < limit', 0.4, 0.85, 'c', 'ensuite'),
        ('Guaranteed', 'request = limit', 0.7, 0.7, 'ok', 'en dernier')]
for i, (t, s, req, lim, k, ev) in enumerate(cols):
    x = 30 + i * 216
    d.box(x, 16, 186, 52, t, s, k=k, d=i)
    d.rect(x + 63, 84, 60, 110, k='floor', rx=6)
    if lim:
        d.raw(f'<rect x="{x + 63}" y="{84 + 110 * (1 - lim)}" width="60" height="{110 * lim}" rx="6" class="dg-fill"/>')
        d.line(x + 55, 84 + 110 * (1 - lim), x + 131, 84 + 110 * (1 - lim), k='court')
        d.text(x + 137, 88 + 110 * (1 - lim), 'limit', 's', anchor='start')
        d.line(x + 55, 84 + 110 * (1 - req), x + 131, 84 + 110 * (1 - req), k='court')
        d.text(x + 137, 88 + 110 * (1 - req) + (12 if req == lim else 0), 'request', 's', anchor='start')
    else:
        d.text(x + 93, 144, 'aucune garantie', 's')
    d.text(x + 93, 214, ev, {'a': 'at', 'c': 'ct', 'ok': 'okt'}[k], d=i)
d.arrow([(30, 234), (650, 234)], k='dash')
d.text(340, 248, 'ordre d\'éviction quand le nœud manque de mémoire', 's')
d.h = 256
put(f'{M}/07-requests-limits-qos.md', 'qos', figure(d, 'Les trois classes QoS', 'La classe dépend uniquement de la façon dont tu remplis requests et limits.'), before='## Encadrer un namespace')

# 10. Taints et tolérations -------------------------------------------------
d = D(680, 236)
d.box(16, 30, 160, 56, 'pod ia', 'tolère gpu=true', k='c', d=0)
d.box(16, 150, 160, 56, 'pod web', 'aucune tolération', d=0)
d.zone(300, 14, 200, 92, 'nœud gpu-1', k='a')
d.text(400, 58, 'taint', 'at')
d.text(400, 76, 'gpu=true:NoSchedule', 's')
d.zone(300, 132, 200, 92, 'nœud std-1')
d.text(400, 184, 'pas de taint', 's')
d.arrow([(176, 58), (296, 58)], color='ok', k='thick', draw=True, d=1)
d.arrow(f'M176 168 C 230 168, 250 110, 290 92', color='a', k='dash', end=False, d=2)
d.text(296, 98, '✗', 'at')
d.arrow([(176, 186), (296, 186)], color='c', k='thick', draw=True, d=3)
d.box(530, 30, 134, 56, 'tolérer ≠ attirer', 'il faut aussi une\naffinité', k='ghost', d=4)
put(f'{M}/07-taints-et-affinites.md', 'taints', figure(d, 'Un taint repousse, une tolération laisse passer', 'Le pod ia PEUT aller sur gpu-1. Pour qu\'il y aille vraiment, ajoute une affinité de nœud.'), before="## Les effets d'un taint")

# 11. Network policies -------------------------------------------------------
d = D(680, 262)
d.zone(16, 14, 470, 234, 'namespace shop', k='c')
d.box(40, 52, 120, 50, 'frontend', d=0)
d.box(200, 52, 120, 50, 'api', 'port 8080', k='c', d=1)
d.box(360, 52, 110, 50, 'postgres', 'port 5432', k='c', d=2)
d.arrow([(160, 77), (198, 77)], color='ok', k='thick')
d.arrow([(320, 77), (358, 77)], color='ok', k='thick')
d.arrow(f'M100 104 C 100 170, 410 170, 412 106', color='a', k='dash', end=False)
d.text(256, 160, '✗ frontend → postgres refusé', 'at')
d.box(40, 186, 430, 44, 'default-deny : tout est fermé, sauf ce qu\'une policy autorise', k='off', d=3)
d.zone(510, 14, 154, 108, 'autre namespace')
d.box(530, 48, 114, 46, 'pod x', d=4)
d.arrow(f'M530 70 C 480 70, 300 20, 262 50', color='a', k='dash', end=False)
d.text(420, 34, '✗', 'at')
d.zone(510, 140, 154, 108, 'kube-system')
d.box(530, 174, 114, 46, 'CoreDNS', 'UDP 53', d=4)
d.arrow(f'M260 104 C 260 130, 480 210, 528 197', color='ok', k='dash')
d.text(395, 128, 'egress DNS à ouvrir', 's')
put(f'{M}/08-network-policies.md', 'policies', figure(d, 'Une politique réseau en refus par défaut', 'On ferme tout, puis on ouvre seulement les flux attendus, sans oublier le DNS.'), before='## Puis ouvrir le nécessaire')

# 12. RBAC --------------------------------------------------------------------
d = D(680, 270)
subj = [('User', 'fares@…'), ('Group', 'devops'), ('ServiceAccount', 'ns/argocd')]
for i, (t, s) in enumerate(subj):
    d.box(14, 22 + i * 80, 140, 52, t, s, d=0)
d.text(84, 264, 'qui', 'zl')
d.zone(214, 10, 450, 118, 'namespace shop', k='c')
d.box(232, 44, 160, 56, 'RoleBinding', 'relie sujets et rôle', k='c', d=1)
d.box(484, 44, 160, 56, 'Role', 'get, list pods', k='c', d=2)
d.arrow([(392, 72), (482, 72)], color='c')
d.zone(214, 148, 450, 114, 'tout le cluster')
d.box(232, 180, 160, 56, 'ClusterRoleBinding', 'droits partout', d=3)
d.box(484, 180, 160, 56, 'ClusterRole', 'view, edit, admin…', d=4)
d.arrow([(392, 208), (482, 208)])
d.arrow(f'M392 92 C 440 120, 470 150, 520 178', color='c', k='dash')
d.text(560, 152, 'droits limités au ns', 's')
d.arrow([(154, 48), (230, 66)], color='c')
d.arrow([(154, 128), (230, 82)], color='c')
d.arrow([(154, 208), (230, 208)])
d.text(440, 264, 'quoi', 'zl')
put(f'{M}/08-rbac.md', 'rbac', figure(d, 'Les quatre objets RBAC', 'Un Role définit des droits, un Binding les donne à des sujets. Un RoleBinding peut réutiliser un ClusterRole, limité à son namespace.'), fence='définit les droits')

# 13. Méthode de debug ------------------------------------------------------------
d = D(680, 270)
d.box(240, 12, 200, 48, 'kubectl get pod', 'quel état ?', k='c', d=0)
cases = [('Pending', 'describe : events', 'ressources, PVC,\ntaints, quota'),
         ('ContainerCreating', 'describe : events', 'image, secret,\nvolume'),
         ('CrashLoopBackOff', 'logs --previous', 'l\'appli plante\nau démarrage'),
         ('Running mais KO', 'readiness, endpoints', 'Service, réseau,\nNetworkPolicy')]
for i, (st, cmd, why) in enumerate(cases):
    x = 14 + i * 166
    d.arrow([(340, 60), (340, 80), (x + 74, 80), (x + 74, 100)], color='c', d=i)
    d.box(x, 102, 148, 44, st, k='a' if i == 2 else '', d=i + 1)
    d.box(x, 162, 148, 40, cmd, k='ghost', tk='s', d=i + 1)
    d.arrow([(x + 74, 146), (x + 74, 160)])
    d.text(x + 74, 222, why, 's', d=i + 1)
put(f'{M}/09-methode-de-debug.md', 'arbre', figure(d, 'Par où commencer selon l\'état du pod', 'L\'état du pod indique la bonne commande. Ne lis pas les logs d\'un pod qui n\'a jamais démarré.'), before='## 1. Où en est le pod ?')

# 14. HPA -------------------------------------------------------------------------
d = D(680, 240)
d.box(20, 92, 140, 56, 'pods', 'CPU utilisé', k='c', d=0)
d.box(200, 14, 160, 56, 'kubelet', 'mesure (cAdvisor)', d=1)
d.box(400, 14, 160, 56, 'metrics-server', 'agrège', d=2)
d.box(470, 120, 190, 64, 'HPA', 'veut 60 % de CPU\nen moyenne', k='c', d=3)
d.box(200, 170, 190, 56, 'Deployment', 'replicas : 3 → 5', d=4)
d.arrow([(90, 90), (90, 42), (198, 42)])
d.arrow([(360, 42), (398, 42)])
d.arrow([(480, 70), (530, 118)])
d.text(516, 92, 'toutes les 15 s', 's', anchor='start')
d.arrow([(470, 170), (440, 198), (392, 198)], color='c')
d.arrow([(200, 198), (90, 198), (90, 150)], color='c')
d.text(286, 130, 'replicas = actuel × utilisation / cible', 's')
d.text(286, 146, '3 × 100 % / 60 % = 5', 'ct')
put(f'{M}/09-metriques-et-monitoring.md', 'hpa', figure(d, 'La boucle de l\'autoscaling horizontal', 'Sans requests CPU sur les pods, le pourcentage n\'a pas de sens et le HPA ne fait rien.'), before="## L'autoscaling horizontal")

# 15. Helm --------------------------------------------------------------------------
d = D(680, 250)
d.box(14, 18, 150, 48, 'templates/', 'deployment.yaml…', d=0)
d.box(14, 80, 150, 48, 'values.yaml', 'défauts du chart', d=0)
d.box(14, 142, 150, 48, '-f values-prod.yaml', 'tes valeurs', k='c', d=1)
d.box(14, 196, 150, 40, '--set image.tag=…', k='c', tk='s', d=1)
d.box(226, 80, 140, 60, 'helm', 'moteur de\ntemplates', k='c', d=2)
for y in (42, 104, 166, 216):
    d.arrow([(164, y), (196, y), (196, 110), (224, 110)], end=(y == 104))
d.box(410, 84, 110, 52, 'manifests', 'YAML final', d=3)
d.arrow([(366, 110), (408, 110)], color='c', k='flow')
d.zone(540, 14, 126, 222, 'release api')
for i, (t, k) in enumerate([('rév. 1', 'off'), ('rév. 2', ''), ('rév. 3', 'c')]):
    d.box(556, 44 + i * 62, 94, 40, t, k=k, d=4 + i)
d.arrow([(520, 110), (538, 110)])
d.arrow(f'M650 188 C 674 176, 674 138, 652 126', color='a', k='dash')
d.text(612, 232, 'rollback → rév. 2', 'at')
put(f'{M}/10-helm.md', 'helm', figure(d, 'Ce que fait helm install ou upgrade', 'Les valeurs se superposent : défauts du chart, puis tes fichiers -f, puis les --set. Chaque upgrade crée une révision.'), before='## Le cycle de vie')

# 16. Kustomize ------------------------------------------------------------------------
d = D(680, 230)
d.box(14, 86, 150, 60, 'base/', 'deployment, service\ncommuns', k='c', d=0)
d.box(236, 24, 170, 60, 'overlays/staging', 'replicas: 2', d=1)
d.box(236, 148, 170, 60, 'overlays/prod', 'replicas: 6\nimage: api:1.8.2', d=1)
d.arrow([(164, 106), (200, 106), (200, 54), (234, 54)], color='c')
d.arrow([(164, 126), (200, 126), (200, 178), (234, 178)], color='c')
d.box(476, 24, 188, 60, 'manifests staging', 'kubectl kustomize', d=2)
d.box(476, 148, 188, 60, 'manifests prod', 'ce que lit ArgoCD', k='c', d=2)
d.arrow([(406, 54), (474, 54)], k='flow')
d.arrow([(406, 178), (474, 178)], color='c', k='flow')
d.text(440, 120, 'patchs appliqués sur la base', 's')
put(f'{M}/10-kustomize-et-gitops.md', 'overlays', figure(d, 'Kustomize : une base, des overlays', 'La base ne change pas. Chaque overlay ne contient que les différences de son environnement.'), before='## GitOps avec ArgoCD')

# 17. StatefulSet ------------------------------------------------------------------------
d = D(680, 250)
d.box(14, 20, 190, 56, 'StatefulSet db', 'serviceName: db', k='c', d=0)
d.box(14, 100, 190, 56, 'Service headless db', 'clusterIP: None', d=0)
for i in range(3):
    x = 250 + i * 142
    d.box(x, 20, 126, 56, f'db-{i}', f'db-{i}.db.ns.svc', k='c', d=1 + i * 2)
    d.box(x, 120, 126, 50, f'data-db-{i}', 'son propre PVC', d=2 + i * 2)
    d.arrow([(x + 63, 76), (x + 63, 118)], start=True)
    if i:
        d.arrow([(x - 16, 48), (x - 2, 48)], color='c')
d.arrow([(204, 48), (248, 48)], color='c')
d.text(450, 200, 'créés dans l\'ordre 0, 1, 2 · supprimés dans l\'ordre inverse', 's')
d.text(450, 218, 'un pod recréé garde son nom et son volume', 'ct')
put(f'{M}/03-statefulset-daemonset-job.md', 'statefulset', figure(d, 'Les garanties d\'un StatefulSet', 'Nom stable, DNS stable, volume dédié : c\'est ce qui permet d\'y faire tourner une base de données.'), before='## Job et CronJob')

# 18. Topology spread -----------------------------------------------------------------------
d = D(680, 210)
for z, (zn, npods) in enumerate([('zone a', 2), ('zone b', 2), ('zone c', 2)]):
    x = 16 + z * 220
    d.zone(x, 14, 208, 150, zn, k='c')
    for n in range(2):
        d.box(x + 14 + n * 98, 44, 86, 104, rx=8, d=z)
        d.text(x + 57 + n * 98, 70, f'nœud {z * 2 + n + 1}', 't', d=z)
        if n < npods - 1 or n == 0:
            pass
    d.circle(x + 57, 112, 11, k='c', d=z + 1)
    d.circle(x + 155, 112, 11, k='c', d=z + 2)
d.text(340, 188, 'topologySpreadConstraints · maxSkew: 1 · topologyKey: zone', 's')
d.text(340, 204, 'la perte d\'une zone ne coupe qu\'un tiers des réplicas', 'ct')
put(f'{M}/07-repartir-et-prioriser.md', 'spread', figure(d, 'Six réplicas répartis sur trois zones', 'Sans contrainte, le scheduler peut tout mettre sur les mêmes nœuds.'), before='## Prioriser')

# 19. ConfigMap : env ou volume ----------------------------------------------------------------
d = D(680, 220)
d.box(14, 80, 150, 60, 'ConfigMap', 'LOG_LEVEL=debug', k='c', d=0)
d.box(250, 14, 200, 64, 'en variable d\'env', 'lue au démarrage', d=1)
d.box(250, 142, 200, 64, 'en fichier (volume)', 'mis à jour en ~1 min', d=2)
d.arrow([(164, 100), (206, 100), (206, 46), (248, 46)], color='c')
d.arrow([(164, 120), (206, 120), (206, 174), (248, 174)], color='c')
d.box(500, 14, 166, 64, 'il faut redémarrer', 'rollout restart', k='a', d=3)
d.box(500, 142, 166, 64, 'l\'appli doit relire', 'sauf avec subPath', k='ok', d=4)
d.arrow([(450, 46), (498, 46)])
d.arrow([(450, 174), (498, 174)])
put(f'{M}/05-injecter-la-configuration.md', 'propagation', figure(d, 'Ce qui se passe quand une ConfigMap change', 'Les variables d\'environnement sont figées au démarrage du conteneur.'), before='## Ce qui se passe quand la config change')
print('k8s ok')
