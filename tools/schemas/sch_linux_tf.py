from svg import D, figure
from inject import put

# ============================== LINUX ==============================
M = 'linux'

# Inodes et liens
d = D(680, 250)
d.zone(14, 14, 200, 222, 'répertoire')
for i, (n, k) in enumerate([('data.csv', 'c'), ('backup.csv', 'c'), ('current', '')]):
    d.box(30, 44 + i * 64, 168, 46, n, ['entrée → inode 1234', 'entrée → inode 1234', 'entrée → inode 5678'][i], k=k, d=i)
d.box(286, 30, 170, 74, 'inode 1234', 'liens : 2\ntaille, droits, dates', k='c', d=3)
d.box(512, 30, 152, 74, 'blocs de données', 'le contenu', d=4)
d.box(286, 150, 170, 74, 'inode 5678', 'type : lien\ncontenu : « /opt/app/v2 »', d=3)
d.box(512, 150, 152, 74, '/opt/app/v2', 'résolu à l\'usage', k='ghost', d=4)
d.arrow([(198, 67), (240, 67), (240, 60), (284, 60)], color='c')
d.arrow([(198, 131), (240, 131), (240, 76), (284, 76)], color='c')
d.arrow([(198, 195), (284, 187)])
d.arrow([(456, 67), (510, 67)], color='c')
d.arrow([(456, 187), (510, 187)], k='dash')
d.text(365, 128, 'hard link : 2 noms, 1 inode', 'ct')
put(f'{M}/01-inodes-et-liens.md', 'liens', figure(d, 'Hard link et lien symbolique', 'Un hard link est un deuxième nom pour le même inode. Un lien symbolique est un petit fichier qui contient un chemin.'), after='## Les deux types de liens')

# Permissions
d = D(680, 200)
groups = [('type', ['-'], 'fichier', ''), ('propriétaire', ['r', 'w', 'x'], 'fares : 7', 'c'), ('groupe', ['r', '-', 'x'], 'devops : 5', 'c'), ('autres', ['-', '-', '-'], 'tous : 0', '')]
x = 20
vals = [4, 2, 1]
for gi, (name, bits, who, k) in enumerate(groups):
    w = len(bits) * 52 + (len(bits) - 1) * 6
    d.text(x + w / 2, 26, name, 'zl', d=gi)
    for bi, b in enumerate(bits):
        bx = x + bi * 58
        on = b != '-'
        d.box(bx, 40, 52, 56, b, k=(k if on else 'off'), tk='tl', d=gi)
        if len(bits) == 3:
            d.text(bx + 26, 116, str(vals[bi]) if on else '0', 'ct' if on else 's', d=gi)
    if len(bits) == 3:
        d.text(x + w / 2, 150, who, 't', d=gi)
    x += w + 26
d.text(340, 186, 'r = 4 · w = 2 · x = 1, on additionne par groupe : 750', 's')
put(f'{M}/02-permissions.md', 'bits', figure(d, 'Lire une ligne de droits', '-rwxr-x--- se lit en trois groupes de trois : 7 pour le propriétaire, 5 pour le groupe, 0 pour les autres.'), fence='-rwxr-x---  1 fares devops')

# États des processus
d = D(680, 250)
d.raw('<g transform="translate(0,36)">')
d.box(14, 100, 96, 50, 'fork()', 'création', d=0)
d.box(170, 100, 120, 50, 'R', 'exécution / prêt', k='c', d=1)
d.box(360, 14, 130, 50, 'S', 'attend un événement', d=2)
d.box(360, 100, 130, 50, 'D', 'attend une I/O', k='a', d=2)
d.box(360, 186, 130, 50, 'T', 'arrêté', d=2)
d.box(548, 100, 118, 50, 'Z', 'zombie', k='ghost', d=3)
d.arrow([(110, 125), (168, 125)])
d.arrow([(290, 112), (330, 112), (330, 39), (358, 39)], start=True)
d.arrow([(290, 125), (358, 125)], color='a', start=True)
d.arrow([(290, 138), (330, 138), (330, 211), (358, 211)], start=True)
d.arrow(f'M230 98 C 240 -34, 596 -34, 607 98', color='c', k='dash')
d.text(560, 4, 'exit()', 'ct')
d.text(424, 172, 'D : même kill -9 attend', 's')
d.text(608, 170, 'disparaît quand le', 's')
d.text(608, 184, 'parent fait wait()', 's')
d.text(424, 252, 'Ctrl+Z, SIGSTOP / SIGCONT', 's')
d.raw('</g>')
d.h = 296
put(f'{M}/03-processus-et-signaux.md', 'etats', figure(d, 'Les états d\'un processus', 'Beaucoup de processus en D signalent un problème de disque ou de réseau (NFS), pas de CPU.'), before='## Les signaux')

# Diagnostic réseau en 5 marches
d = D(680, 200)
steps = [('1 interface', 'ip -br a'), ('2 route', 'ip r get 1.1.1.1'), ('3 DNS', 'dig +short api'), ('4 port', 'nc -zv api 443'), ('5 appli', 'curl -v https://…')]
for i, (t, cmd) in enumerate(steps):
    x = 14 + i * 132
    y = 120 - i * 24
    d.box(x, y, 122, 58, t, cmd, k='c' if i == 4 else '', d=i)
    if i:
        d.arrow([(x - 10, y + 52), (x - 2, y + 40)], color='c')
d.text(340, 196, 'on monte une marche seulement si la précédente est bonne', 's')
d.h = 206
put(f'{M}/05-diagnostiquer-le-reseau.md', 'marches', figure(d, 'Diagnostiquer le réseau, marche par marche', 'Chaque marche répond à une couche différente. Sauter une marche fait perdre du temps.'), before='## 1. Interface et adresse')

# LVM
d = D(680, 280)
for i, n in enumerate(['/dev/sdb', '/dev/sdc']):
    d.box(120 + i * 250, 14, 190, 44, n, 'disque', d=0)
    d.box(120 + i * 250, 80, 190, 44, f'PV {n}', 'pvcreate', k='c', d=1)
    d.arrow([(215 + i * 250, 58), (215 + i * 250, 78)])
    d.arrow([(215 + i * 250, 124), (215 + i * 250, 144)], color='c')
d.box(120, 146, 440, 44, 'VG vg_data', 'vgcreate : un seul « pool » de 2 disques', k='c', d=2)
d.box(120, 214, 260, 50, 'LV lv_app → /srv/app', 'lvcreate, mkfs, mount', k='c', d=3)
d.box(392, 214, 168, 50, 'LV lv_logs', '→ /var/log/app', d=3)
d.arrow([(250, 190), (250, 212)], color='c')
d.arrow([(476, 190), (476, 212)], color='c')
d.text(20, 40, 'matériel', 'zl', anchor='start')
d.text(20, 106, 'PV', 'zl', anchor='start')
d.text(20, 172, 'VG', 'zl', anchor='start')
d.text(20, 243, 'LV', 'zl', anchor='start')
d.text(620, 172, 'on peut', 's')
d.text(620, 186, 'agrandir', 's')
d.text(620, 243, 'lvextend -r', 'ct')
put(f'{M}/06-disques-montages-lvm.md', 'lvm', figure(d, 'Les trois couches de LVM', 'On agrandit un LV à chaud, en ajoutant un disque au VG si besoin.'), fence='/dev/sdb   /dev/sdc        ← PV')

# systemd : drop-in
d = D(680, 200)
d.box(14, 20, 250, 56, '/lib/systemd/system/nginx.service', 'fourni par le paquet', tk='s', d=0)
d.box(14, 110, 250, 70, '/etc/systemd/system/\nnginx.service.d/override.conf', 'systemctl edit nginx', k='c', tk='s', d=1)
d.box(350, 56, 150, 76, 'systemd fusionne', 'daemon-reload', k='c', d=2)
d.box(540, 56, 126, 76, 'unité finale', 'systemctl cat nginx', d=3)
d.arrow([(264, 48), (300, 48), (300, 82), (348, 82)])
d.arrow([(264, 145), (300, 145), (300, 106), (348, 106)], color='c')
d.arrow([(500, 94), (538, 94)], color='c', k='flow')
d.text(140, 98, 'gagne en cas de conflit ↓', 's')
put(f'{M}/04-systemd.md', 'dropin', figure(d, 'Surcharger une unité avec un drop-in', 'Le fichier du paquet n\'est jamais modifié : une mise à jour ne casse pas ta surcharge.'), after='## Surcharger sans copier')

# ============================== TERRAFORM ==============================
M = 'terraform'

d = D(680, 220)
steps = [('code .tf', 'tu écris', ''), ('init', 'providers, modules,\nbackend', ''), ('plan', 'diff code / state /\nréalité', 'c'), ('relecture', 'surtout les -/+', 'a'), ('apply', 'applique le plan,\nmet à jour le state', 'c')]
for i, (t, s, k) in enumerate(steps):
    x = 14 + i * 134
    d.box(x, 60, 118, 70, t, s, k=k, d=i)
    if i:
        d.arrow([(x - 16, 95), (x - 2, 95)], color='c')
d.arrow(f'M550 132 C 520 200, 120 200, 73 132', k='dash')
d.text(310, 196, 'chaque changement repart du code', 's')
d.text(240, 40, 'terraform plan -out=tfplan', 's')
d.text(560, 40, 'terraform apply tfplan', 's')
put(f'{M}/01-le-workflow.md', 'cycle', figure(d, 'Le cycle de travail Terraform', 'Le plan enregistré est exactement ce qui sera appliqué.'), fence='code .tf ──► terraform init')

d = D(680, 250)
d.box(20, 30, 170, 64, 'code .tf', 'ce que tu veux', k='c', d=0)
d.box(255, 160, 170, 64, 'state', 'ce que Terraform\npense gérer', k='a', d=1)
d.box(490, 30, 170, 64, 'infra réelle', 'ce qui existe', d=2)
d.arrow([(190, 62), (488, 62)], k='dash', label='plan compare les trois', dy=-8)
d.arrow([(105, 94), (105, 192), (253, 192)], color='c', start=True)
d.arrow([(575, 94), (575, 192), (427, 192)], start=True, label='refresh', at=0.5, dy=-8)
d.text(340, 150, 'S3 chiffré + verrou', 's')
d.text(340, 244, 'un seul apply à la fois grâce au verrou', 'at')
put(f'{M}/02-le-state.md', 'triangle', figure(d, 'Code, state et réalité', 'Le state fait le lien entre tes blocs resource et les vrais identifiants dans le cloud.'), before='## Un backend distant avec verrou')

d = D(680, 230)
d.zone(14, 14, 178, 202, 'entrées')
for i, (t, s) in enumerate([('default', 'dans variable {}'), ('*.tfvars', 'par environnement'), ('-var / TF_VAR_', 'gagne sur le reste')]):
    d.box(28, 42 + i * 58, 150, 46, t, s, k='c' if i == 2 else '', d=i)
d.box(236, 82, 120, 56, 'variables', 'var.env', k='c', d=3)
d.box(392, 82, 120, 56, 'locals', 'calculs, noms', d=4)
d.box(548, 30, 118, 56, 'resources', 'utilisent var et local', d=5)
d.box(548, 134, 118, 56, 'outputs', 'ce que tu exposes', k='c', d=6)
d.arrow([(192, 110), (234, 110)], color='c')
d.arrow([(356, 110), (390, 110)])
d.arrow([(512, 100), (530, 100), (530, 58), (546, 58)])
d.arrow([(607, 86), (607, 132)])
put(f'{M}/03-variables-outputs-locals.md', 'flux', figure(d, 'D\'où viennent les valeurs et où elles vont', 'Les variables sont les entrées, les locals les calculs internes, les outputs les sorties.'), before='## Les variables : les entrées')

d = D(680, 240)
d.zone(14, 14, 652, 212, 'module racine : envs/prod', k='c')
d.box(30, 70, 170, 90, 'module "network"', 'in : cidr\nout : subnet_ids', k='c', d=0)
d.box(330, 70, 160, 90, 'module "eks"', 'in : subnet_ids\nout : endpoint', k='c', d=1)
d.box(530, 84, 116, 62, 'output', 'cluster_endpoint', d=2)
d.arrow([(200, 115), (328, 115)], color='c', k='flow')
d.text(264, 100, 'module.network', 's')
d.text(264, 140, '.subnet_ids', 's')
d.arrow([(490, 115), (528, 115)])
d.text(115, 190, 'source = "../../modules/network"', 's')
d.text(410, 190, 'source = "terraform-aws-modules/eks/aws"', 's')
put(f'{M}/04-modules.md', 'modules', figure(d, 'Des modules qui se passent des valeurs', 'Un module ne voit que ses variables. Les modules communiquent par leurs outputs.'), before='## Appeler un module')

d = D(680, 250)
d.text(170, 24, 'avec count : indexé par position', 'at')
d.text(510, 24, 'avec for_each : indexé par clé', 'okt')
for i, (n, after, k) in enumerate([('[0] a', '[0] a', ''), ('[1] b', '[1] c', 'a'), ('[2] c', '✗ détruit', 'a')]):
    d.box(30, 46 + i * 62, 110, 46, n, d=i)
    d.box(200, 46 + i * 62, 110, 46, after, k=k, d=i + 1)
    d.arrow([(140, 69 + i * 62), (198, 69 + i * 62)], color='a' if k else '')
for i, (n, after, k) in enumerate([('["a"]', '["a"]', ''), ('["b"]', '✗ détruit', 'a'), ('["c"]', '["c"]', '')]):
    d.box(370, 46 + i * 62, 110, 46, n, d=i)
    d.box(540, 46 + i * 62, 110, 46, after, k=k or 'ok', d=i + 1)
    d.arrow([(480, 69 + i * 62), (538, 69 + i * 62)], color='a' if k else 'ok')
d.text(170, 242, 'retirer "b" : c est recréé, l\'ancien [2] détruit', 's')
d.text(510, 242, 'retirer "b" : seul b est détruit', 's')
d.line(340, 40, 340, 230, k='grid')
put(f'{M}/05-count-for-each-expressions.md', 'count-vs-foreach', figure(d, 'Retirer un élément avec count ou avec for_each', 'Liste de départ ["a", "b", "c"], on retire "b".'), before="## Avec une map d'objets")

d = D(680, 230)
d.box(20, 20, 200, 56, 'modules/app', 'le code partagé', k='c', d=0)
for i, env in enumerate(['dev', 'staging', 'prod']):
    x = 260 + i * 140
    d.box(x, 20, 124, 56, f'envs/{env}', 'main.tf', d=1 + i)
    d.box(x, 130, 124, 56, f'{env}.tfstate', 'son propre state', k='a' if env == 'prod' else '', d=2 + i)
    d.arrow([(x + 62, 76), (x + 62, 128)])
d.arrow([(220, 48), (258, 48)], color='c')
d.text(470, 214, 'une erreur en dev ne peut pas toucher le state de prod', 's')
put(f'{M}/06-environnements-et-equipe.md', 'separation', figure(d, 'Un dossier et un state par environnement', 'Le code commun vit dans un module, chaque environnement l\'appelle avec ses valeurs.'), before='## Partager des informations entre projets')

d = D(680, 210)
d.text(170, 22, 'renommer sans moved', 'at')
d.text(510, 22, 'renommer avec un bloc moved', 'okt')
d.box(30, 40, 280, 44, '- aws_instance.web', 'destroy', k='a', d=0)
d.box(30, 100, 280, 44, '+ aws_instance.app', 'create : nouvelle IP, coupure', k='a', d=1)
d.box(370, 40, 280, 104, 'aws_instance.web\n→ aws_instance.app', 'même objet, nouvelle adresse\n0 to add, 0 to destroy', k='ok', d=1)
d.text(510, 186, 'moved { from = aws_instance.web  to = aws_instance.app }', 's')
d.line(340, 36, 340, 196, k='grid')
put(f'{M}/07-import-et-refactoring.md', 'moved', figure(d, 'Ce que change un bloc moved', 'Sans moved, Terraform voit une ressource supprimée et une autre ajoutée.'), before='## Protéger avec `lifecycle`')
print('linux tf ok')
