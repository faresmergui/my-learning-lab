---
title: Performance et grandes infrastructures
chapter: 11
order: 1
duration: 13
level: intermédiaire
tags:
- forks
- serial
- stratégies
- pipelining
- mitogen
cards:
- q: Que règle `forks` ?
  a: 'Le nombre de machines traitées **en parallèle** par le nœud de contrôle. La valeur par défaut est 5 : sur 200 serveurs, c''est très lent. On la monte souvent à 20 ou 50, selon le CPU et la mémoire du nœud de contrôle.'
- q: Différence entre `forks` et `serial` ?
  a: '`forks` dit combien de machines **en même temps** pour chaque tâche. `serial` découpe les machines en **lots** : le play entier se déroule sur le premier lot, puis sur le suivant. `serial` sert à faire des mises à jour progressives.'
- q: Que change la stratégie `free` ?
  a: Par défaut (`linear`), chaque tâche attend que toutes les machines l'aient finie. Avec `free`, chaque machine avance à son rythme, sans attendre les plus lentes.
- q: Qu'apporte le pipelining SSH ?
  a: Ansible envoie le module directement dans la session SSH au lieu de le copier dans un fichier temporaire, ce qui économise plusieurs allers-retours par tâche. Il demande que `requiretty` soit désactivé dans sudoers.
- q: À quoi sert le cache des facts ?
  a: À garder les facts collectés (dans des fichiers JSON ou Redis) pour ne pas les recollecter à chaque exécution. Avec `gathering = smart`, Ansible ne collecte que pour les machines absentes du cache.
- q: Comment lancer une tâche longue sans bloquer la connexion ?
  a: 'Avec `async` (durée maximale) et `poll` (fréquence de vérification). `poll: 0` lance et passe à la suite ; on récupère le résultat plus tard avec `async_status`.'
- q: Qu'est-ce que Mitogen pour Ansible ?
  a: 'Un plugin tiers qui remplace la façon dont Ansible exécute les modules : il garde un interpréteur Python ouvert sur chaque machine au lieu d''en relancer un par tâche. Souvent 2 à 7 fois plus rapide, mais il suit les nouvelles versions d''ansible-core avec retard.'
quiz:
- q: Tu dois mettre à jour 30 serveurs web derrière un load balancer sans couper le service. Quel réglage ?
  options:
  - '`serial: 5` (ou `serial: "20%"`) avec retrait du load balancer pendant la mise à jour'
  - '`forks: 30`'
  - '`strategy: free`'
  - '`async: 3600`'
  answer: 0
  explain: 'Le play complet passe sur 5 serveurs, puis 5 autres : les 25 restants servent le trafic pendant ce temps.'
- q: Ton playbook met 40 minutes sur 300 machines et la collecte des facts en prend 10. Que fais-tu en premier ?
  options:
  - Passer à Mitogen
  - Ajouter `serial`
  - Réécrire en Bash
  - Monter `forks`, activer le pipelining et le cache des facts
  answer: 3
  explain: Ce sont les gains les plus simples et les plus sûrs, intégrés à Ansible. On mesure ensuite avant d'aller plus loin.
- q: 'Avec `serial: 10` et `max_fail_percentage: 0`, un serveur du premier lot échoue. Que se passe-t-il ?'
  options:
  - Le serveur est réessayé
  - Les autres lots continuent
  - Le play s'arrête, les lots suivants ne sont pas touchés
  - Rien, l'échec est ignoré
  answer: 2
  explain: 'C''est le but : une mise à jour défectueuse s''arrête au premier lot au lieu de casser tout le parc.'
- q: Comment savoir quelles tâches prennent le plus de temps ?
  options:
  - Avec ansible-lint
  - En activant le callback `profile_tasks`
  - Avec -vvvv
  - Avec --check
  answer: 1
  explain: '`callbacks_enabled = ansible.posix.profile_tasks` affiche la durée de chaque tâche et le classement des plus lentes.'
---

Sur dix machines, Ansible est rapide sans qu'on y pense. Sur trois cents, un playbook peut prendre une heure, et une mise à jour mal découpée peut couper un service entier. Ce chapitre explique où part le temps, les réglages qui le font gagner, et comment déployer **progressivement** sur un grand parc.

> **Les outils cités dans cette fiche.**
> - **ansible.cfg** : le fichier de configuration d'Ansible, lu dans le dossier courant en priorité ; c'est là qu'on règle la plupart des options de ce chapitre.
> - **forks** : le nombre de machines traitées en parallèle.
> - **serial** : le découpage des machines en lots successifs.
> - **stratégie** (strategy) : la façon dont les machines avancent dans les tâches (`linear`, `free`, `host_pinned`).
> - **ControlPersist** : une option d'OpenSSH qui garde une connexion ouverte pour la réutiliser, au lieu d'en ouvrir une nouvelle à chaque tâche.
> - **pipelining** : une option d'Ansible qui envoie les modules dans la session SSH sans fichier temporaire.
> - **Redis** : une base de données clé-valeur en mémoire, utilisable comme cache des facts partagé.
> - **Mitogen** : une bibliothèque Python tierce qui accélère l'exécution des modules.
> - **callback** : un plugin qui réagit aux événements d'Ansible, par exemple pour chronométrer les tâches.

## Où part le temps

Pour chaque tâche et chaque machine, Ansible : ouvre (ou réutilise) une connexion SSH, crée un dossier temporaire, copie le module, lance Python, récupère le JSON, nettoie. Sur une tâche simple, le module s'exécute en quelques millisecondes : c'est **l'aller-retour** qui coûte. D'où la règle : mesurer d'abord.

```ini
# ansible.cfg
[defaults]
callbacks_enabled = ansible.posix.profile_tasks, ansible.posix.timer
```

`profile_tasks` affiche la durée de chaque tâche et les plus lentes à la fin ; `timer` donne la durée totale.

## Les réglages qui font gagner le plus

```ini
# ansible.cfg
[defaults]
forks = 30
gathering = smart
fact_caching = jsonfile
fact_caching_connection = ~/.cache/ansible-facts
fact_caching_timeout = 7200

[ssh_connection]
pipelining = True
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
```

| Réglage | Gain | Attention |
| --- | --- | --- |
| `forks` | plus de machines en parallèle | chaque fork consomme CPU et mémoire sur le nœud de contrôle |
| `pipelining` | moins d'allers-retours par tâche | `requiretty` doit être désactivé dans sudoers (c'est le cas sur les distributions récentes) |
| `ControlPersist` | une seule connexion SSH réutilisée | activé par défaut, à garder |
| cache des facts | plus de collecte à chaque lancement | des facts périmés si la machine change entre-temps |
| `gather_facts: false` | aucune collecte | seulement si le play n'utilise aucun fact |
| `gather_subset: [network]` | collecte partielle | seulement les familles de facts utiles |

Les gains côté code comptent autant :

- passer une **liste** au module (`apt: name: [a, b, c]`) plutôt que `loop` : une transaction au lieu de trois ;
- éviter les tâches inutiles sur chaque machine : `run_once: true` pour une action à faire une seule fois (une migration de base), `delegate_to: localhost` pour une action à lancer depuis le nœud de contrôle ;
- ne lancer que ce qui a changé avec `--tags` et `--limit`.

## Les stratégies

| Stratégie | Comportement | Usage |
| --- | --- | --- |
| `linear` (défaut) | chaque tâche attend toutes les machines | prévisible, facile à lire |
| `free` | chaque machine avance à son rythme | parcs hétérogènes, machines lentes qui ne doivent pas freiner les autres |
| `host_pinned` | comme `free`, mais une machine commencée est terminée avant d'en prendre une autre | rarement utile |

`strategy: free` rend la sortie difficile à suivre, car les tâches de toutes les machines se mélangent.

## Déployer par lots avec serial

`serial` ne sert pas à aller plus vite, mais à **ne pas tout casser d'un coup**. C'est le rolling update d'Ansible :

```yaml
- name: Mise à jour des serveurs web
  hosts: web
  serial:
    - 1          # d'abord une seule machine (le canari)
    - "20%"      # puis 20 % du parc
    - "100%"     # puis le reste
  max_fail_percentage: 0
  pre_tasks:
    - name: Sortir la machine du load balancer
      community.general.haproxy:
        state: disabled
        host: "{{ inventory_hostname }}"
        backend: web
      delegate_to: "{{ item }}"
      loop: "{{ groups['lb'] }}"
  roles:
    - app
  post_tasks:
    - name: Attendre que l'application réponde
      ansible.builtin.uri:
        url: "http://{{ inventory_hostname }}:8080/health"
      register: sante
      until: sante.status == 200
      retries: 20
      delay: 3
    - name: Remettre la machine dans le load balancer
      community.general.haproxy:
        state: enabled
        host: "{{ inventory_hostname }}"
        backend: web
      delegate_to: "{{ item }}"
      loop: "{{ groups['lb'] }}"
```

<!-- schema:serial -->
<figure class="diagram"><svg viewBox="0 0 680 310" role="img" aria-label="Une mise à jour par lots avec serial" style="--minw:560px"><defs><marker id="g5-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g5-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g5-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g5-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><rect x="14" y="14" width="204" height="150" rx="12" class="dg-zone dg-zc"/><text x="26" y="32" class="dg-zl" text-anchor="start">lot 1 · canari</text><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="101.0" y="84.0" width="24" height="26" rx="5"/></g><rect x="238" y="14" width="204" height="150" rx="12" class="dg-zone "/><text x="250" y="32" class="dg-zl" text-anchor="start">lot 2 · 20 %</text><g class="dg-box dg-pop" style="--d:2"><rect x="280.0" y="84.0" width="24" height="26" rx="5"/></g><g class="dg-box dg-pop" style="--d:2"><rect x="310.0" y="84.0" width="24" height="26" rx="5"/></g><g class="dg-box dg-pop" style="--d:2"><rect x="340.0" y="84.0" width="24" height="26" rx="5"/></g><g class="dg-box dg-pop" style="--d:2"><rect x="370.0" y="84.0" width="24" height="26" rx="5"/></g><path d="M220 90 L235 90" class="dg-l c" marker-end="url(#g5-c)" style="--d:2"/><rect x="462" y="14" width="204" height="150" rx="12" class="dg-zone "/><text x="474" y="32" class="dg-zl" text-anchor="start">lot 3 · le reste</text><g class="dg-box dg-pop" style="--d:4"><rect x="489.0" y="50.0" width="24" height="26" rx="5"/></g><g class="dg-box dg-pop" style="--d:4"><rect x="519.0" y="50.0" width="24" height="26" rx="5"/></g><g class="dg-box dg-pop" style="--d:4"><rect x="549.0" y="50.0" width="24" height="26" rx="5"/></g><g class="dg-box dg-pop" style="--d:4"><rect x="579.0" y="50.0" width="24" height="26" rx="5"/></g><g class="dg-box dg-pop" style="--d:4"><rect x="609.0" y="50.0" width="24" height="26" rx="5"/></g><g class="dg-box dg-pop" style="--d:4"><rect x="489.0" y="84.0" width="24" height="26" rx="5"/></g><g class="dg-box dg-pop" style="--d:4"><rect x="519.0" y="84.0" width="24" height="26" rx="5"/></g><g class="dg-box dg-pop" style="--d:4"><rect x="549.0" y="84.0" width="24" height="26" rx="5"/></g><g class="dg-box dg-pop" style="--d:4"><rect x="579.0" y="84.0" width="24" height="26" rx="5"/></g><g class="dg-box dg-pop" style="--d:4"><rect x="609.0" y="84.0" width="24" height="26" rx="5"/></g><g class="dg-box dg-pop" style="--d:4"><rect x="489.0" y="118.0" width="24" height="26" rx="5"/></g><g class="dg-box dg-pop" style="--d:4"><rect x="519.0" y="118.0" width="24" height="26" rx="5"/></g><g class="dg-box dg-pop" style="--d:4"><rect x="549.0" y="118.0" width="24" height="26" rx="5"/></g><g class="dg-box dg-pop" style="--d:4"><rect x="579.0" y="118.0" width="24" height="26" rx="5"/></g><g class="dg-box dg-pop" style="--d:4"><rect x="609.0" y="118.0" width="24" height="26" rx="5"/></g><path d="M444 90 L459 90" class="dg-l c" marker-end="url(#g5-c)" style="--d:4"/><text x="14" y="190" class="dg-zl" text-anchor="start">dans chaque lot, avant de passer au suivant</text><g class="dg-box dg-pop" style="--d:6"><rect x="14" y="202" width="150" height="50" rx="9"/></g><text x="89.0" y="224.0" class="dg-t" text-anchor="middle" style="--d:6">sortir du LB</text><text x="89.0" y="242.0" class="dg-s" text-anchor="middle" style="--d:6">pre_tasks</text><g class="dg-box dg-pop" style="--d:7"><rect x="182" y="202" width="150" height="50" rx="9"/></g><text x="257.0" y="224.0" class="dg-t" text-anchor="middle" style="--d:7">mettre à jour</text><text x="257.0" y="242.0" class="dg-s" text-anchor="middle" style="--d:7">rôle app</text><path d="M166 227 L180 227" class="dg-l c" marker-end="url(#g5-c)"/><g class="dg-box dg-c dg-pop" style="--d:8"><rect x="350" y="202" width="150" height="50" rx="9"/></g><text x="425.0" y="224.0" class="dg-t" text-anchor="middle" style="--d:8">tester</text><text x="425.0" y="242.0" class="dg-s" text-anchor="middle" style="--d:8">/health</text><path d="M334 227 L348 227" class="dg-l c" marker-end="url(#g5-c)"/><g class="dg-box dg-pop" style="--d:9"><rect x="518" y="202" width="150" height="50" rx="9"/></g><text x="593.0" y="224.0" class="dg-t" text-anchor="middle" style="--d:9">remettre dans le LB</text><text x="593.0" y="242.0" class="dg-s" text-anchor="middle" style="--d:9">post_tasks</text><path d="M502 227 L516 227" class="dg-l c" marker-end="url(#g5-c)"/><text x="340" y="288" class="dg-at" text-anchor="middle" style="--d:10">max_fail_percentage: 0 : un échec arrête tout, le reste du parc garde l&#x27;ancienne version</text></svg><figcaption>Si le canari casse, une seule machine est touchée et le reste du parc n&#x27;a pas bougé.</figcaption></figure>
<!-- /schema:serial -->

Le play complet (sortie, mise à jour, test, retour) se déroule sur un lot avant de passer au suivant. Avec `max_fail_percentage: 0`, le moindre échec arrête tout : le reste du parc tourne encore sur l'ancienne version. Attention, les handlers sont lancés à la fin de **chaque lot**.

## Les tâches longues

Une tâche qui dure longtemps (une mise à jour complète du système, une sauvegarde) peut dépasser le délai SSH. `async` la lance en arrière-plan sur la machine :

```yaml
- name: Mettre à jour tous les paquets
  ansible.builtin.dnf:
    name: "*"
    state: latest
  async: 1800     # 30 minutes au maximum
  poll: 15        # vérifier toutes les 15 secondes
```

Avec `poll: 0`, Ansible lance la tâche et passe immédiatement à la suite ; on récupère le résultat plus tard avec le module `async_status`. Ça permet de lancer une opération longue sur toutes les machines en même temps.

## Encore plus vite

Quand les réglages intégrés ne suffisent plus :

- **Mitogen** remplace le mécanisme d'exécution : un interpréteur Python reste ouvert sur chaque machine. Le gain est souvent important, mais c'est un projet tiers qui prend du retard sur les nouvelles versions d'ansible-core : vérifie la compatibilité avant de l'adopter.
- **Découper l'inventaire** : lancer un playbook par région ou par zone en parallèle depuis plusieurs nœuds de contrôle, ou laisser AWX répartir le travail (chapitre 12).
- **ansible-pull** : inverser le modèle. Chaque machine récupère le dépôt Git et s'applique elle-même le playbook, à intervalle régulier. Plus de goulot sur le nœud de contrôle, mais plus de vision centrale de ce qui a échoué.

## Les inventaires dynamiques à grande échelle

Sur OpenStack ou AWS, un inventaire dynamique interroge l'API à chaque lancement, ce qui peut prendre longtemps sur des milliers de VM. Les plugins d'inventaire savent garder leur résultat en cache :

```yaml
# inventaires/openstack.yml
plugin: openstack.cloud.openstack
cache: true
cache_plugin: ansible.builtin.jsonfile
cache_connection: ~/.cache/ansible-inventory
cache_timeout: 600
```

> **À retenir.** Mesure d'abord avec `profile_tasks`. Puis `forks` plus haut, pipelining, cache des facts et listes passées aux modules : ce sont les gains simples. `serial` avec `max_fail_percentage` sert à déployer par lots sans tout casser, en commençant par une machine canari. `async` pour les tâches longues, Mitogen ou ansible-pull quand le reste ne suffit plus.
