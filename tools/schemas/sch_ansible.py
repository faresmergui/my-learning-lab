from svg import D, figure
from inject import put

M = 'ansible'

# --- 01: the agentless model ----------------------------------------
d = D(680, 300)
d.zone(14, 14, 252, 200, 'nœud de contrôle', k='c')
d.box(30, 44, 106, 52, 'inventaire', 'qui', d=0)
d.box(146, 44, 106, 52, 'playbook', 'quoi', d=0)
d.box(30, 130, 222, 56, 'ansible-playbook', 'ton poste, un bastion, la CI', k='c', d=1)
d.arrow([(83, 96), (83, 128)], color='c')
d.arrow([(199, 96), (199, 128)], color='c')
for i, n in enumerate(['web1', 'web2', 'db1']):
    y = 24 + i * 70
    d.box(470, y, 196, 50, n, 'SSH + Python, rien d\'autre', d=2 + i)
    d.arrow([(252, 158), (380, 158), (380, y + 25), (468, y + 25)], color='c')
d.text(316, 150, 'SSH', 's')
for i, t in enumerate(['1. copie le module', '2. l\'exécute (Python)', '3. renvoie du JSON', '4. nettoie']):
    d.box(14 + i * 166, 244, 154, 40, t, k='ghost', tk='s', d=5 + i)
d.text(14, 236, 'à chaque tâche, sur chaque machine', 'zl', anchor='start')
put(f'{M}/01-comprendre-ansible.md', 'push', figure(d, 'Ansible pousse ses tâches en SSH', 'Aucun agent ne tourne sur les serveurs : ils ont seulement besoin de SSH et de Python.'), before="À chaque tâche, Ansible")

# --- 04: execution order -----------------------------------------
d = D(680, 350)
hosts = ['web1', 'web2', 'web3']
cx = [330, 460, 590]
for i, h in enumerate(hosts):
    d.box(cx[i] - 55, 14, 110, 36, h, d=0)
rows = [('facts', ['ok', 'ok', 'ok']), ('tâche 1 · paquet', ['c', 'c', 'ok']), ('tâche 2 · config', ['c', 'a', 'c']),
        ('tâche 3 · service', ['ok', None, 'c']), ('handlers', ['c', None, 'c'])]
for r, (name, cells) in enumerate(rows):
    y = 80 + r * 44
    d.text(24, y + 5, name, 't', anchor='start', d=r + 1)
    d.line(180, y + 22, 650, y + 22, k='grid')
    for i, k in enumerate(cells):
        if k:
            d.circle(cx[i], y, 10, k=k, d=r + 1)
        else:
            d.text(cx[i], y + 4, '—', 's', d=r + 1)
d.text(24, 305, 'PLAY RECAP', 'zl', anchor='start')
for i, (t, k) in enumerate([('réussi', 'okt'), ('échec', 'at'), ('réussi', 'okt')]):
    d.text(cx[i], 305, t, k, d=6)
d.circle(30, 334, 6, k='ok'); d.text(42, 338, 'ok : déjà bon', 's', anchor='start')
d.circle(170, 334, 6, k='c'); d.text(182, 338, 'changed', 's', anchor='start')
d.circle(270, 334, 6, k='a'); d.text(282, 338, 'failed : web2 sort du play, les autres continuent', 's', anchor='start')
d.h = 350
put(f'{M}/04-les-playbooks.md', 'ordre', figure(d, "L'ordre d'exécution d'un playbook", "Une tâche se termine sur toutes les machines (5 à la fois par défaut) avant que la suivante commence."), before='## Les handlers')

# --- 05: variable precedence -----------------------------------
d = D(680, 340)
lv = ["defaults/ d'un rôle", 'group_vars/all', 'group_vars/<groupe>', 'host_vars/<hôte>', 'facts',
      'vars: du play, vars_files', "vars/ d'un rôle", 'set_fact, register', '-e (extra vars)']
for i, t in enumerate(lv):
    w = 220 + i * 50
    k = 'a' if i == 8 else ('c' if i >= 4 else '')
    d.box(20, 14 + i * 34, w, 28, f'{i + 1} · {t}', k=k, rx=7, tk='s', d=i)
d.text(660, 30, 'le plus faible', 's', anchor='end')
d.arrow([(668, 40), (668, 300)], color='c')
d.text(660, 326, 'le plus fort', 'ct', anchor='end')
put(f'{M}/05-variables-et-facts.md', 'priorite', figure(d, 'La priorité des variables', 'Plus la source est précise et tardive, plus elle gagne. Les defaults des rôles sont faits pour être écrasés.'), before="L'idée générale")

# --- 10: testing stages ------------------------------------------
d = D(680, 250)
steps = [('yamllint', '--syntax-check', ''), ('ansible-lint', 'profil production', ''), ('--check --diff', 'sur un vrai\nenvironnement', 'c'), ('Molecule', 'machine jetable', 'c')]
for i, (t, s, k) in enumerate(steps):
    x = 14 + i * 168
    d.box(x, 24, 150, 62, t, s, k=k, d=i)
    if i:
        d.arrow([(x - 16, 55), (x - 2, 55)], color='c')
d.arrow([(14, 110), (664, 110)], k='dash')
d.text(14, 128, 'quelques secondes', 's', anchor='start')
d.text(664, 128, 'plusieurs minutes, mais teste vraiment', 's', anchor='end')
d.text(14, 166, 'molecule test enchaîne', 'zl', anchor='start')
for i, t in enumerate(['create', 'converge', 'idempotence', 'verify', 'destroy']):
    x = 14 + i * 132
    d.box(x, 178, 118, 40, t, k='a' if t == 'idempotence' else 'ghost', d=4 + i)
    if i:
        d.arrow([(x - 12, 198), (x - 2, 198)])
d.text(340, 240, 'idempotence : un deuxième passage ne doit rien changer', 's', d=9)
put(f'{M}/10-tester-son-code-ansible.md', 'etapes', figure(d, 'Du test le plus rapide au plus complet', 'On lance les plus rapides à chaque commit, Molecule en CI à chaque merge request.'), before='## Tout enchaîner')

# --- 11: serial and batches ------------------------------------------
d = D(680, 310)
lots = [('lot 1 · canari', 1), ('lot 2 · 20 %', 4), ('lot 3 · le reste', 15)]
for i, (t, n) in enumerate(lots):
    x = 14 + i * 224
    d.zone(x, 14, 204, 150, t, k='c' if i == 0 else '')
    cols = 5
    for j in range(n):
        r, c = divmod(j, cols)
        gx = x + 102 - (min(n, cols) * 30) / 2 + c * 30
        rows = (n + cols - 1) // cols
        d.box(gx, 14 + (150 - rows * 34) / 2 + 12 + r * 34, 24, 26, '', k='c' if i == 0 else '', rx=5, d=i * 2)
    if i:
        d.arrow([(x - 18, 90), (x - 3, 90)], color='c', d=i * 2)
d.text(14, 190, 'dans chaque lot, avant de passer au suivant', 'zl', anchor='start')
for i, (t, s) in enumerate([('sortir du LB', 'pre_tasks'), ('mettre à jour', 'rôle app'), ('tester', '/health'), ('remettre dans le LB', 'post_tasks')]):
    x = 14 + i * 168
    d.box(x, 202, 150, 50, t, s, k='c' if i == 2 else '', d=6 + i)
    if i:
        d.arrow([(x - 16, 227), (x - 2, 227)], color='c')
d.text(340, 288, "max_fail_percentage: 0 : un échec arrête tout, le reste du parc garde l'ancienne version", 'at', d=10)
put(f'{M}/11-performance-et-grandes-infras.md', 'serial', figure(d, 'Une mise à jour par lots avec serial', "Si le canari casse, une seule machine est touchée et le reste du parc n'a pas bougé."), before='Le play complet (sortie')
print('ok')
