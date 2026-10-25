---
title: Services avec systemd
chapter: 4
order: 1
duration: 10
level: intermédiaire
tags:
- LFCS
cards:
- q: Que fait `systemctl enable --now nginx` ?
  a: Il **active** le démarrage automatique au boot (`enable`) **et** démarre le service immédiatement (`--now`).
- q: Quand faut-il lancer `systemctl daemon-reload` ?
  a: Après avoir **créé ou modifié** un fichier d'unité. Sinon systemd utilise encore l'ancienne version.
- q: Où mettre une unité personnalisée, et comment surcharger une unité fournie par un paquet ?
  a: 'Les unités personnalisées vont dans `/etc/systemd/system/`. Pour surcharger sans copier : `systemctl edit nginx`, qui crée un fichier `override.conf`.'
- q: À quoi sert `Restart=on-failure` ?
  a: À relancer le service s'il s'arrête en erreur. `RestartSec=` règle le délai, et `StartLimitBurst` limite le nombre d'essais.
- q: Quelle est l'alternative systemd à cron ?
  a: 'Les **timers** : une unité `.timer` qui déclenche une unité `.service`. Avantages : logs dans journald, et `Persistent=true` rattrape les exécutions manquées.'
- q: Comment voir pourquoi un service ne démarre pas ?
  a: '`systemctl status app` (dernières lignes de log, code de sortie), puis `journalctl -u app -b --no-pager`.'
- q: Différence entre `Wants=` et `After=` ?
  a: '`Wants=` dit **quoi** démarrer avec l''unité, `After=` dit **dans quel ordre**. Il faut souvent les deux.'
- q: À quoi sert `Type=oneshot` ?
  a: Une tâche **qui se termine** (script, migration), souvent avec `RemainAfterExit=yes`.
- q: Service modifié mais ancienne config toujours utilisée ?
  a: '`systemctl daemon-reload` oublié avant le restart.'
quiz:
- q: Tu modifies `/etc/systemd/system/app.service`, puis `systemctl restart app`. L'ancienne config est utilisée. Pourquoi ?
  options:
  - Il fallait `systemctl daemon-reload` avant
  - Il faut redémarrer le serveur
  - Le fichier doit être dans /usr/lib
  - Il faut `systemctl enable`
  answer: 0
  explain: systemd garde les unités en mémoire. `systemctl status` affiche d'ailleurs un avertissement quand le fichier a changé sur le disque.
- q: Quelle directive fait démarrer ton service après que le réseau soit vraiment disponible ?
  options:
  - After=network.target
  - After=network-online.target avec Wants=network-online.target
  - Requires=sshd.service
  - WantedBy=multi-user.target
  answer: 1
  explain: '`network.target` signifie seulement que la pile réseau est lancée, pas que les interfaces ont une adresse.'
---

systemd démarre le système et gère les services. Chaque service est décrit par un fichier **unité**.


> **Les termes et outils cités dans cette fiche.**
> - **démon** : un programme qui tourne en arrière-plan en permanence (sshd, dockerd).

## Une unité de service

```ini
# /etc/systemd/system/api.service
[Unit]
Description=API interne
Wants=network-online.target
After=network-online.target

[Service]
User=api
WorkingDirectory=/opt/api
EnvironmentFile=/etc/api/env
ExecStart=/opt/api/bin/api --port 8080
Restart=on-failure
RestartSec=5
# Durcissement
NoNewPrivileges=true
ProtectSystem=strict
ReadWritePaths=/var/lib/api

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable --now api
systemctl status api
systemctl list-units --type=service --state=failed
```

## Surcharger sans copier

<!-- schema:dropin -->
<figure class="diagram"><svg viewBox="0 0 680 200" role="img" aria-label="Surcharger une unité avec un drop-in" style="--minw:560px"><defs><marker id="g6-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g6-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g6-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g6-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-pop" style="--d:0"><rect x="14" y="20" width="250" height="56" rx="9"/></g><text x="139.0" y="45.0" class="dg-s" text-anchor="middle" style="--d:0">/lib/systemd/system/nginx.service</text><text x="139.0" y="63.0" class="dg-s" text-anchor="middle" style="--d:0">fourni par le paquet</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="14" y="110" width="250" height="70" rx="9"/></g><text x="139.0" y="134.0" class="dg-s" text-anchor="middle" style="--d:1"><tspan x="139.0" dy="0">/etc/systemd/system/</tspan><tspan x="139.0" dy="14">nginx.service.d/override.conf</tspan></text><text x="139.0" y="168.0" class="dg-s" text-anchor="middle" style="--d:1">systemctl edit nginx</text><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="350" y="56" width="150" height="76" rx="9"/></g><text x="425.0" y="91.0" class="dg-t" text-anchor="middle" style="--d:2">systemd fusionne</text><text x="425.0" y="109.0" class="dg-s" text-anchor="middle" style="--d:2">daemon-reload</text><g class="dg-box dg-pop" style="--d:3"><rect x="540" y="56" width="126" height="76" rx="9"/></g><text x="603.0" y="91.0" class="dg-t" text-anchor="middle" style="--d:3">unité finale</text><text x="603.0" y="109.0" class="dg-s" text-anchor="middle" style="--d:3">systemctl cat nginx</text><path d="M264 48 L300 48 L300 82 L348 82" class="dg-l" marker-end="url(#g6-n)"/><path d="M264 145 L300 145 L300 106 L348 106" class="dg-l c" marker-end="url(#g6-c)"/><path d="M500 94 L538 94" class="dg-l c flow" marker-end="url(#g6-c)"/><text x="140" y="98" class="dg-s" text-anchor="middle">gagne en cas de conflit ↓</text></svg><figcaption>Le fichier du paquet n&#x27;est jamais modifié : une mise à jour ne casse pas ta surcharge.</figcaption></figure>
<!-- /schema:dropin -->

```bash
systemctl edit nginx          # crée /etc/systemd/system/nginx.service.d/override.conf
systemctl cat nginx           # affiche l'unité et ses surcharges
```

## Un timer à la place de cron

```ini
# backup.timer
[Timer]
OnCalendar=*-*-* 03:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
systemctl enable --now backup.timer
systemctl list-timers
```

## Comprendre les dépendances

Deux familles de directives, souvent confondues :

| Directive | Sens |
| --- | --- |
| `Wants=` / `Requires=` | **Quoi** démarrer avec l'unité (`Requires` arrête aussi l'unité si la dépendance échoue) |
| `After=` / `Before=` | **Dans quel ordre** démarrer |

`After=network.target` sans `Wants=` n'impose rien : il dit seulement « si le réseau démarre, attends-le ». C'est pourquoi on écrit les deux pour `network-online.target`.

## Les types de service

- `Type=simple` (défaut) : le processus lancé **est** le service.
- `Type=exec` : comme simple, mais systemd attend que l'exécution ait vraiment démarré.
- `Type=forking` : pour les anciens démons qui se dupliquent en arrière-plan, avec un `PIDFile=`.
- `Type=oneshot` : une tâche qui se termine (script de migration, préparation), souvent avec `RemainAfterExit=yes`.
- `Type=notify` : le programme prévient systemd quand il est prêt.

## Déboguer un service qui ne démarre pas

```bash
systemctl status api              # état, dernières lignes de log, code de sortie
journalctl -u api -b --no-pager   # tous les logs depuis le démarrage
systemd-analyze verify api.service
systemctl show api -p ExecStart -p User -p Restart
```

Les causes classiques : `daemon-reload` oublié après modification, chemin relatif dans `ExecStart` (il faut un chemin absolu), utilisateur sans droits sur `WorkingDirectory`, ou service qui **redémarre en boucle** jusqu'à atteindre la limite (`StartLimitBurst`).

## Mesurer le démarrage

```bash
systemd-analyze blame             # unités les plus lentes
systemd-analyze critical-chain    # le chemin qui retarde le démarrage
```

> **À retenir.** `enable` agit sur le **prochain démarrage**, `start` sur **maintenant**. Oublier l'un ou l'autre est la cause classique du service « qui marchait avant le reboot ».
