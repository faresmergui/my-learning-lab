---
title: 'Variables et facts : paramétrer sans dupliquer'
chapter: 5
order: 1
duration: 13
level: intermédiaire
tags:
- variables
- facts
- group_vars
- précédence
cards:
- q: Où ranger les variables d'un groupe de machines ?
  a: Dans `group_vars/<groupe>.yml` (ou un dossier `group_vars/<groupe>/`), à côté de l'inventaire ou du playbook. Ansible les charge tout seul pour chaque machine du groupe. Même principe par machine avec `host_vars/<hôte>.yml`.
- q: Qu'est-ce qu'un fact ?
  a: Une information **collectée sur la machine** au début du play (système, version, IP, mémoire, disques…). On la lit dans `ansible_facts`, par exemple `ansible_facts['distribution']`.
- q: Quelle variable gagne toujours, quel que soit l'endroit où les autres sont définies ?
  a: 'Une **extra var** passée en ligne de commande : `-e version=1.4`. C''est le niveau le plus fort de l''ordre de priorité.'
- q: Différence entre `defaults/main.yml` et `vars/main.yml` dans un rôle ?
  a: '`defaults` : valeurs par défaut, priorité **la plus faible**, faites pour être surchargées. `vars` : valeurs internes du rôle, priorité forte, qu''on ne veut pas voir changer depuis l''inventaire.'
- q: À quoi sert `register` ?
  a: À **garder le résultat d'une tâche** dans une variable (sortie, code retour, `changed`…) pour s'en servir dans les tâches suivantes.
- q: Que fait `set_fact` ?
  a: Crée ou modifie une variable **pendant l'exécution**, pour la machine en cours. Utile pour calculer une valeur à partir d'autres variables ou d'un résultat.
- q: Pourquoi désactiver `gather_facts` ?
  a: 'La collecte prend une à plusieurs secondes par machine. Si le play n''utilise aucun fact, `gather_facts: false` fait gagner du temps, surtout sur des centaines de machines.'
- q: Comment voir toutes les variables qu'une machine reçoit ?
  a: '`ansible-inventory -i inv --host web1` (variables d''inventaire) ou une tâche `debug: var=hostvars[inventory_hostname]` pendant un play.'
quiz:
- q: '`group_vars/all.yml` définit `nginx_port: 80`, `group_vars/web.yml` définit `nginx_port: 8080`. Quelle valeur reçoit web1, membre de web ?'
  options:
  - '8080'
  - Ça dépend de l'ordre alphabétique
  - '80'
  - Ansible lève une erreur de doublon
  answer: 0
  explain: Un groupe précis l'emporte sur `all`. Plus la définition est proche de la machine, plus elle est forte.
- q: Un rôle définit `app_version` dans `defaults/main.yml`, et ton inventaire la redéfinit dans `group_vars`. Laquelle est utilisée ?
  options:
  - Aucune, il faut `-e`
  - La première chargée
  - Celle de l'inventaire
  - Celle du rôle
  answer: 2
  explain: Les `defaults` d'un rôle ont la priorité la plus basse, justement pour être surchargés depuis l'inventaire.
- q: Tu veux installer un paquet différent selon que la machine est Debian ou Rocky Linux. Sur quoi te baser ?
  options:
  - Sur une extra var à chaque lancement
  - Sur le fichier /etc/hosts
  - Sur le nom d'hôte
  - Sur le fact `ansible_facts['os_family']`
  answer: 3
  explain: 'Le fact `os_family` vaut `Debian` ou `RedHat` : il est collecté automatiquement et ne ment pas.'
- q: Une tâche `command` lit la version installée d'un logiciel. Comment l'utiliser dans la tâche suivante ?
  options:
  - Avec `gather_facts`
  - Avec `register` puis `resultat.stdout`
  - En relisant un fichier temporaire
  - Avec `notify`
  answer: 1
  explain: '`register: resultat` stocke la sortie ; `resultat.stdout` contient le texte affiché par la commande.'
---

Un playbook utile sert à plusieurs environnements et plusieurs types de machines. Plutôt que de copier les tâches avec des valeurs différentes, on écrit des tâches génériques et on met les valeurs dans des **variables**. Ansible y ajoute des **facts**, des variables qu'il découvre lui-même sur chaque machine. Le seul vrai piège, c'est de savoir quelle valeur gagne quand une variable est définie à plusieurs endroits.

> **Les outils cités dans cette fiche.**
> - **variable** : un nom associé à une valeur (texte, nombre, liste, dictionnaire), utilisée dans les tâches avec la syntaxe `{{ nom }}`.
> - **fact** : une variable collectée automatiquement sur la machine gérée (système, réseau, matériel) par le module `setup`.
> - **group_vars / host_vars** : des dossiers dont Ansible charge tout seul les fichiers, par groupe ou par machine.
> - **extra vars** : des variables passées en ligne de commande avec `-e`, plus fortes que toutes les autres.
> - **hostvars** : un dictionnaire qui donne accès aux variables de **toutes** les machines, pas seulement celle en cours.
> - **Jinja2** : le moteur de gabarits utilisé par Ansible pour remplacer `{{ ... }}` par des valeurs (détaillé au chapitre suivant).

## Utiliser une variable

```yaml
- name: Serveurs web
  hosts: web
  vars:
    nginx_port: 8080
  tasks:
    - name: Ouvrir le port
      ansible.posix.firewalld:
        port: "{{ nginx_port }}/tcp"
        state: enabled
        permanent: true
```

Deux règles de syntaxe YAML évitent la moitié des erreurs :

- quand une valeur **commence** par `{{`, il faut la mettre entre guillemets : `port: "{{ nginx_port }}"` ;
- les noms de variables utilisent des lettres, chiffres et `_`, jamais de tiret (`nginx-port` est invalide).

## Où définir les variables

Dans un vrai projet, on ne met presque rien dans le playbook. On range les valeurs à côté de l'inventaire :

```
inventaires/prod/
├── hosts.yml
├── group_vars/
│   ├── all.yml        # pour toutes les machines
│   ├── web.yml        # pour le groupe web
│   └── db/
│       ├── main.yml
│       └── vault.yml  # secrets chiffrés (chapitre 9)
└── host_vars/
    └── web1.yml       # pour une seule machine
```

L'intérêt : `inventaires/staging/` a la même structure avec d'autres valeurs. Le **même playbook** s'applique aux deux environnements, seul l'inventaire change.

## Les facts

Au début de chaque play, Ansible lance le module `setup` sur chaque machine. Il revient avec des centaines d'informations, rangées dans `ansible_facts` :

| Fact | Exemple de valeur |
| --- | --- |
| `ansible_facts['hostname']` | `web1` |
| `ansible_facts['os_family']` | `Debian`, `RedHat` |
| `ansible_facts['distribution_major_version']` | `12` |
| `ansible_facts['default_ipv4']['address']` | `10.0.1.11` |
| `ansible_facts['memtotal_mb']` | `7963` |
| `ansible_facts['processor_vcpus']` | `4` |

Pour les explorer : `ansible web1 -m ansible.builtin.setup -a "filter=*ipv4*"`.

On peut aussi créer ses propres facts, appelés **facts locaux** : un fichier `.fact` (JSON ou INI) déposé dans `/etc/ansible/facts.d/` sur la machine apparaît dans `ansible_facts['ansible_local']`. Pratique pour noter le rôle d'un serveur ou la version déployée.

Collecter les facts coûte du temps. Si un play n'en a pas besoin, `gather_facts: false`. Sur une grosse infra, on peut aussi les **mettre en cache** (chapitre 11).

## Les variables calculées pendant le play

```yaml
- name: Lire la version installée
  ansible.builtin.command: /opt/app/bin/app --version
  register: version_actuelle
  changed_when: false        # lire n'est pas modifier

- name: Mémoriser si une mise à jour est nécessaire
  ansible.builtin.set_fact:
    maj_requise: "{{ version_actuelle.stdout != app_version }}"

- name: Afficher pour vérifier
  ansible.builtin.debug:
    var: maj_requise
```

Un résultat enregistré avec `register` contient notamment `stdout`, `stderr`, `rc` (code retour), `changed` et `failed`. Pour voir sa structure exacte, on l'affiche une fois avec `debug`.

## Lire les variables d'une autre machine

Chaque machine a ses variables, mais `hostvars` permet de lire celles des autres. Exemple classique : la configuration d'un load balancer doit connaître les IP des serveurs web.

```jinja
{% for hote in groups['web'] %}
server {{ hote }} {{ hostvars[hote]['ansible_facts']['default_ipv4']['address'] }}:8080;
{% endfor %}
```

Les facts des machines web doivent avoir été collectés plus tôt dans la même exécution (ou être en cache), sinon la clé n'existe pas.

## L'ordre de priorité

Ansible connaît une vingtaine de niveaux. Inutile de les apprendre tous : retiens l'ordre de ceux que tu utilises vraiment, **du plus faible au plus fort** :

| Rang | Source | Usage |
| --- | --- | --- |
| 1 | `defaults/main.yml` d'un rôle | valeurs par défaut, à surcharger |
| 2 | `group_vars/all` | valeurs communes à tout l'environnement |
| 3 | `group_vars/<groupe>` | valeurs d'un groupe (un enfant bat son parent) |
| 4 | `host_vars/<hôte>` | exceptions pour une machine |
| 5 | facts | ce qu'Ansible a découvert |
| 6 | `vars:` du play, `vars_files` | valeurs propres à un playbook |
| 7 | `vars/main.yml` d'un rôle | constantes internes du rôle |
| 8 | `set_fact`, `register` | valeurs calculées pendant le play |
| 9 | `-e` (extra vars) | gagne toujours |

<!-- schema:priorite -->
<figure class="diagram"><svg viewBox="0 0 680 340" role="img" aria-label="La priorité des variables" style="--minw:560px"><defs><marker id="g3-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g3-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g3-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g3-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-pop" style="--d:0"><rect x="20" y="14" width="220" height="28" rx="7"/></g><text x="130.0" y="33.0" class="dg-s" text-anchor="middle" style="--d:0">1 · defaults/ d&#x27;un rôle</text><g class="dg-box dg-pop" style="--d:1"><rect x="20" y="48" width="270" height="28" rx="7"/></g><text x="155.0" y="67.0" class="dg-s" text-anchor="middle" style="--d:1">2 · group_vars/all</text><g class="dg-box dg-pop" style="--d:2"><rect x="20" y="82" width="320" height="28" rx="7"/></g><text x="180.0" y="101.0" class="dg-s" text-anchor="middle" style="--d:2">3 · group_vars/&lt;groupe&gt;</text><g class="dg-box dg-pop" style="--d:3"><rect x="20" y="116" width="370" height="28" rx="7"/></g><text x="205.0" y="135.0" class="dg-s" text-anchor="middle" style="--d:3">4 · host_vars/&lt;hôte&gt;</text><g class="dg-box dg-c dg-pop" style="--d:4"><rect x="20" y="150" width="420" height="28" rx="7"/></g><text x="230.0" y="169.0" class="dg-s" text-anchor="middle" style="--d:4">5 · facts</text><g class="dg-box dg-c dg-pop" style="--d:5"><rect x="20" y="184" width="470" height="28" rx="7"/></g><text x="255.0" y="203.0" class="dg-s" text-anchor="middle" style="--d:5">6 · vars: du play, vars_files</text><g class="dg-box dg-c dg-pop" style="--d:6"><rect x="20" y="218" width="520" height="28" rx="7"/></g><text x="280.0" y="237.0" class="dg-s" text-anchor="middle" style="--d:6">7 · vars/ d&#x27;un rôle</text><g class="dg-box dg-c dg-pop" style="--d:7"><rect x="20" y="252" width="570" height="28" rx="7"/></g><text x="305.0" y="271.0" class="dg-s" text-anchor="middle" style="--d:7">8 · set_fact, register</text><g class="dg-box dg-a dg-pop" style="--d:8"><rect x="20" y="286" width="620" height="28" rx="7"/></g><text x="330.0" y="305.0" class="dg-s" text-anchor="middle" style="--d:8">9 · -e (extra vars)</text><text x="660" y="30" class="dg-s" text-anchor="end">le plus faible</text><path d="M668 40 L668 300" class="dg-l c" marker-end="url(#g3-c)"/><text x="660" y="326" class="dg-ct" text-anchor="end">le plus fort</text></svg><figcaption>Plus la source est précise et tardive, plus elle gagne. Les defaults des rôles sont faits pour être écrasés.</figcaption></figure>
<!-- /schema:priorite -->

L'idée générale : **plus c'est précis et tardif, plus c'est fort**. Une bonne pratique en découle : définir chaque variable à **un seul endroit**, mettre les valeurs par défaut dans les `defaults` des rôles et les vraies valeurs dans `group_vars`. Si tu cherches pourquoi une variable a telle valeur, `ansible-inventory --host` puis un `debug` règlent la question.

> **À retenir.** Les tâches restent génériques, les valeurs vivent dans `group_vars` et `host_vars`, par environnement. Les facts décrivent la machine réelle et servent aux conditions. En cas de conflit, le plus précis gagne, et `-e` gagne toujours ; les `defaults` d'un rôle sont faits pour être écrasés.
