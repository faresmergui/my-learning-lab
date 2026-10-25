---
title: 'Les playbooks : plays, tâches et handlers'
chapter: 4
order: 1
duration: 12
level: intermédiaire
tags:
- playbook
- handlers
- check mode
cards:
- q: Qu'est-ce qu'un playbook ?
  a: Un fichier YAML contenant un ou plusieurs **plays**. Chaque play associe un groupe de machines (`hosts`) à une liste de **tâches**, exécutées dans l'ordre.
- q: Dans quel ordre Ansible exécute-t-il les tâches sur plusieurs machines ?
  a: 'Tâche par tâche : la tâche 1 sur toutes les machines, puis la tâche 2 sur toutes, etc. (stratégie `linear` par défaut). Une machine en échec sort du jeu, les autres continuent.'
- q: À quoi sert un handler ?
  a: À exécuter une action **seulement si** une tâche a changé quelque chose, typiquement redémarrer un service après modification de sa configuration. Il est déclenché par `notify` et lancé une seule fois, en fin de play.
- q: 'Que fait `become: true` ?'
  a: Exécute les tâches avec élévation de privilèges, par défaut via `sudo` en root.
- q: Que font `--check` et `--diff` ?
  a: '`--check` simule sans rien modifier (dry run). `--diff` montre les différences dans les fichiers. Ensemble, ils montrent ce qu''un passage changerait.'
- q: Pourquoi donner un `name` à chaque tâche ?
  a: C'est ce qui s'affiche dans la sortie et les logs. Un nom clair (« Installer nginx ») rend le rapport lisible et sert de documentation.
quiz:
- q: Tu modifies `nginx.conf` via une tâche `template` qui notifie un handler de redémarrage. Au passage suivant, le fichier n'a pas changé. Que se passe-t-il ?
  options:
  - nginx redémarre quand même
  - nginx ne redémarre pas
  - Le playbook échoue
  - nginx est réinstallé
  answer: 1
  explain: Le handler ne part que si la tâche qui le notifie est `changed`.
- q: Trois tâches notifient le même handler dans un play. Combien de fois s'exécute-t-il ?
  options:
  - Trois fois
  - Une fois, en fin de play
  - Zéro
  - Une fois après chaque tâche
  answer: 1
  explain: 'Les handlers sont dédupliqués et lancés à la fin du play (ou à un `meta: flush_handlers`).'
- q: Avant de lancer un playbook en prod, quelle commande montre ce qu'il changerait sans rien toucher ?
  options:
  - ansible-playbook site.yml --check --diff
  - ansible-playbook site.yml -v
  - ansible-lint site.yml
  - ansible-playbook site.yml --step
  answer: 0
  explain: Le mode check simule, le diff affiche les changements de fichiers.
---

Un **playbook** est un fichier YAML qui décrit la configuration à appliquer. Il contient un ou plusieurs **plays** ; chaque play dit « sur ces machines, fais ces tâches ». C'est le cœur du travail quotidien avec Ansible.

> **Les outils cités dans cette fiche.**
> - **playbook** : un fichier YAML qui contient un ou plusieurs plays.
> - **play** : un bloc qui associe un groupe de machines (`hosts`) à une liste de tâches.
> - **tâche** (task) : l'appel d'un module avec ses paramètres, et un nom lisible.
> - **handler** : une tâche spéciale qui ne s'exécute que si une autre tâche l'a notifiée et a changé quelque chose.
> - **facts** : les informations qu'Ansible collecte sur chaque machine au début du play (détaillés au chapitre 5).
> - **template** : un module qui génère un fichier à partir d'un modèle `.j2` écrit en **Jinja2** (chapitre 6).
> - **nginx** : un serveur web et reverse proxy très répandu, pris ici comme exemple.

## Un premier playbook

```yaml
# web.yml
- name: Serveurs web
  hosts: web
  become: true
  tasks:
    - name: Installer nginx
      ansible.builtin.apt:
        name: nginx
        state: present
        update_cache: true

    - name: Déposer la configuration
      ansible.builtin.template:
        src: nginx.conf.j2
        dest: /etc/nginx/nginx.conf
        mode: "0644"
      notify: Recharger nginx

    - name: Démarrer nginx au boot
      ansible.builtin.service:
        name: nginx
        state: started
        enabled: true

  handlers:
    - name: Recharger nginx
      ansible.builtin.service:
        name: nginx
        state: reloaded
```

On le lance avec :

```bash
ansible-playbook -i inventaires/prod web.yml
```

## Comment il s'exécute

1. Ansible lit l'inventaire et retient les machines du groupe `web`.
2. Il collecte les **facts** de chaque machine (système, IP, mémoire…), sauf si `gather_facts: false`.
3. Il exécute la **première tâche sur toutes les machines** en parallèle (5 à la fois par défaut), puis la deuxième, et ainsi de suite.
4. Si une tâche échoue sur une machine, cette machine est retirée du play ; les autres continuent.
5. À la fin, il lance les handlers notifiés, puis affiche le **récapitulatif** (`PLAY RECAP`) : combien de tâches `ok`, `changed`, `failed` par machine.

<!-- schema:ordre -->
<figure class="diagram"><svg viewBox="0 0 680 350" role="img" aria-label="L&#x27;ordre d&#x27;exécution d&#x27;un playbook" style="--minw:560px"><defs><marker id="g2-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g2-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g2-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g2-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-pop" style="--d:0"><rect x="275" y="14" width="110" height="36" rx="9"/></g><text x="330.0" y="37.0" class="dg-t" text-anchor="middle" style="--d:0">web1</text><g class="dg-box dg-pop" style="--d:0"><rect x="405" y="14" width="110" height="36" rx="9"/></g><text x="460.0" y="37.0" class="dg-t" text-anchor="middle" style="--d:0">web2</text><g class="dg-box dg-pop" style="--d:0"><rect x="535" y="14" width="110" height="36" rx="9"/></g><text x="590.0" y="37.0" class="dg-t" text-anchor="middle" style="--d:0">web3</text><text x="24" y="85" class="dg-t" text-anchor="start" style="--d:1">facts</text><line x1="180" y1="102" x2="650" y2="102" class="dg-grid"/><circle cx="330" cy="80" r="10" class="dg-dot dg-ok dg-pop" style="--d:1"/><circle cx="460" cy="80" r="10" class="dg-dot dg-ok dg-pop" style="--d:1"/><circle cx="590" cy="80" r="10" class="dg-dot dg-ok dg-pop" style="--d:1"/><text x="24" y="129" class="dg-t" text-anchor="start" style="--d:2">tâche 1 · paquet</text><line x1="180" y1="146" x2="650" y2="146" class="dg-grid"/><circle cx="330" cy="124" r="10" class="dg-dot dg-c dg-pop" style="--d:2"/><circle cx="460" cy="124" r="10" class="dg-dot dg-c dg-pop" style="--d:2"/><circle cx="590" cy="124" r="10" class="dg-dot dg-ok dg-pop" style="--d:2"/><text x="24" y="173" class="dg-t" text-anchor="start" style="--d:3">tâche 2 · config</text><line x1="180" y1="190" x2="650" y2="190" class="dg-grid"/><circle cx="330" cy="168" r="10" class="dg-dot dg-c dg-pop" style="--d:3"/><circle cx="460" cy="168" r="10" class="dg-dot dg-a dg-pop" style="--d:3"/><circle cx="590" cy="168" r="10" class="dg-dot dg-c dg-pop" style="--d:3"/><text x="24" y="217" class="dg-t" text-anchor="start" style="--d:4">tâche 3 · service</text><line x1="180" y1="234" x2="650" y2="234" class="dg-grid"/><circle cx="330" cy="212" r="10" class="dg-dot dg-ok dg-pop" style="--d:4"/><text x="460" y="216" class="dg-s" text-anchor="middle" style="--d:4">—</text><circle cx="590" cy="212" r="10" class="dg-dot dg-c dg-pop" style="--d:4"/><text x="24" y="261" class="dg-t" text-anchor="start" style="--d:5">handlers</text><line x1="180" y1="278" x2="650" y2="278" class="dg-grid"/><circle cx="330" cy="256" r="10" class="dg-dot dg-c dg-pop" style="--d:5"/><text x="460" y="260" class="dg-s" text-anchor="middle" style="--d:5">—</text><circle cx="590" cy="256" r="10" class="dg-dot dg-c dg-pop" style="--d:5"/><text x="24" y="305" class="dg-zl" text-anchor="start">PLAY RECAP</text><text x="330" y="305" class="dg-okt" text-anchor="middle" style="--d:6">réussi</text><text x="460" y="305" class="dg-at" text-anchor="middle" style="--d:6">échec</text><text x="590" y="305" class="dg-okt" text-anchor="middle" style="--d:6">réussi</text><circle cx="30" cy="334" r="6" class="dg-dot dg-ok dg-pop"/><text x="42" y="338" class="dg-s" text-anchor="start">ok : déjà bon</text><circle cx="170" cy="334" r="6" class="dg-dot dg-c dg-pop"/><text x="182" y="338" class="dg-s" text-anchor="start">changed</text><circle cx="270" cy="334" r="6" class="dg-dot dg-a dg-pop"/><text x="282" y="338" class="dg-s" text-anchor="start">failed : web2 sort du play, les autres continuent</text></svg><figcaption>Une tâche se termine sur toutes les machines (5 à la fois par défaut) avant que la suivante commence.</figcaption></figure>
<!-- /schema:ordre -->

## Les handlers

Redémarrer nginx à chaque passage couperait le service pour rien. Un **handler** est une tâche qui ne s'exécute que si une autre tâche l'a notifiée **et** a réellement changé quelque chose. Si trois fichiers de configuration changent, le handler ne tourne qu'une fois, en fin de play. Pour le forcer plus tôt (par exemple avant un test de santé), on ajoute `- ansible.builtin.meta: flush_handlers`.

## Vérifier avant d'appliquer

| Option | Effet |
| --- | --- |
| `--check` | simule : aucune modification, chaque tâche dit ce qu'elle ferait |
| `--diff` | affiche les différences dans les fichiers modifiés |
| `--limit web1` | ne vise qu'une partie des machines |
| `--tags nginx` | ne lance que les tâches marquées de ce tag |
| `--start-at-task "Déposer la configuration"` | reprend au milieu |
| `-v`, `-vvv` | de plus en plus de détails, utile pour déboguer |

`--check --diff --limit web1` est le bon réflexe avant de toucher à la prod : voir ce qui changerait sur une seule machine.

## Organiser plusieurs playbooks

Un projet grandit vite. Une convention courante :

```
site.yml          # importe tous les autres
web.yml
db.yml
inventaires/
roles/
```

```yaml
# site.yml
- ansible.builtin.import_playbook: web.yml
- ansible.builtin.import_playbook: db.yml
```

> **À retenir.** Un play associe des machines à des tâches, exécutées tâche par tâche sur toutes les machines. Les handlers ne réagissent qu'aux vrais changements, une seule fois en fin de play. `--check --diff` avant chaque passage sensible.
