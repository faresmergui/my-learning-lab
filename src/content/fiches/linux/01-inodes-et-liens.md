---
title: Inodes, hard links et liens symboliques
chapter: 1
order: 1
duration: 7
level: intermédiaire
tags:
- LFCS
cards:
- q: Que contient un inode, et que ne contient-il pas ?
  a: Les métadonnées du fichier (type, permissions, propriétaire, tailles, dates, pointeurs vers les blocs). Il ne contient **pas** le nom, qui est stocké dans le répertoire parent.
- q: Différence entre un hard link et un lien symbolique ?
  a: Le **hard link** est un second nom pour le même inode, il survit à la suppression de l'original mais reste sur le même système de fichiers. Le **symlink** pointe vers un chemin et casse si la cible disparaît.
- q: '`df -h` indique de la place libre, mais impossible de créer un fichier. Que vérifier ?'
  a: '`df -i` : le système de fichiers n''a peut-être plus d''**inodes** libres, souvent à cause de millions de petits fichiers (cache, sessions…).'
quiz:
- q: Tu supprimes un gros fichier de log, mais l'espace disque ne revient pas. Pourquoi ?
  options:
  - Le fichier est dans la corbeille
  - Un processus le garde encore ouvert, l'inode n'est libéré qu'à la fermeture
  - Il faut lancer `sync`
  - Le hard link a été converti en symlink
  answer: 1
  explain: Les données restent tant qu'un descripteur est ouvert. `lsof +L1` liste ces fichiers supprimés mais ouverts. Redémarre le service, ou vide le fichier avec `> fichier.log` au lieu de le supprimer.
- q: Quelle commande crée un lien symbolique `current` vers `releases/v2` ?
  options:
  - ln releases/v2 current
  - ln -s releases/v2 current
  - ln -s current releases/v2
  - cp -l releases/v2 current
  answer: 1
  explain: L'ordre est toujours `ln -s CIBLE NOM_DU_LIEN`, comme pour `cp SOURCE DESTINATION`.
---

Sous Linux, un fichier, ce sont deux choses séparées : un **inode** qui décrit les données, et un ou plusieurs **noms** qui pointent vers cet inode.


> **Les termes et outils cités dans cette fiche.**
> - **cache** : une copie rapide de données souvent demandées, pour éviter de les recalculer ou de les relire.

## Voir les inodes

```bash
ls -li            # le premier nombre est le numéro d'inode
stat fichier.txt  # détail complet, dont le nombre de liens
df -i             # inodes utilisés et libres par système de fichiers
```

## Les deux types de liens

<!-- schema:liens -->
<figure class="diagram"><svg viewBox="0 0 680 250" role="img" aria-label="Hard link et lien symbolique" style="--minw:560px"><defs><marker id="g1-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g1-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g1-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g1-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><rect x="14" y="14" width="200" height="222" rx="12" class="dg-zone "/><text x="26" y="32" class="dg-zl" text-anchor="start">répertoire</text><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="30" y="44" width="168" height="46" rx="9"/></g><text x="114.0" y="64.0" class="dg-t" text-anchor="middle" style="--d:0">data.csv</text><text x="114.0" y="82.0" class="dg-s" text-anchor="middle" style="--d:0">entrée → inode 1234</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="30" y="108" width="168" height="46" rx="9"/></g><text x="114.0" y="128.0" class="dg-t" text-anchor="middle" style="--d:1">backup.csv</text><text x="114.0" y="146.0" class="dg-s" text-anchor="middle" style="--d:1">entrée → inode 1234</text><g class="dg-box dg-pop" style="--d:2"><rect x="30" y="172" width="168" height="46" rx="9"/></g><text x="114.0" y="192.0" class="dg-t" text-anchor="middle" style="--d:2">current</text><text x="114.0" y="210.0" class="dg-s" text-anchor="middle" style="--d:2">entrée → inode 5678</text><g class="dg-box dg-c dg-pop" style="--d:3"><rect x="286" y="30" width="170" height="74" rx="9"/></g><text x="371.0" y="57.0" class="dg-t" text-anchor="middle" style="--d:3">inode 1234</text><text x="371.0" y="75.0" class="dg-s" text-anchor="middle" style="--d:3"><tspan x="371.0" dy="0">liens : 2</tspan><tspan x="371.0" dy="14">taille, droits, dates</tspan></text><g class="dg-box dg-pop" style="--d:4"><rect x="512" y="30" width="152" height="74" rx="9"/></g><text x="588.0" y="64.0" class="dg-t" text-anchor="middle" style="--d:4">blocs de données</text><text x="588.0" y="82.0" class="dg-s" text-anchor="middle" style="--d:4">le contenu</text><g class="dg-box dg-pop" style="--d:3"><rect x="286" y="150" width="170" height="74" rx="9"/></g><text x="371.0" y="177.0" class="dg-t" text-anchor="middle" style="--d:3">inode 5678</text><text x="371.0" y="195.0" class="dg-s" text-anchor="middle" style="--d:3"><tspan x="371.0" dy="0">type : lien</tspan><tspan x="371.0" dy="14">contenu : « /opt/app/v2 »</tspan></text><g class="dg-box dg-ghost dg-pop" style="--d:4"><rect x="512" y="150" width="152" height="74" rx="9"/></g><text x="588.0" y="184.0" class="dg-t" text-anchor="middle" style="--d:4">/opt/app/v2</text><text x="588.0" y="202.0" class="dg-s" text-anchor="middle" style="--d:4">résolu à l&#x27;usage</text><path d="M198 67 L240 67 L240 60 L284 60" class="dg-l c" marker-end="url(#g1-c)"/><path d="M198 131 L240 131 L240 76 L284 76" class="dg-l c" marker-end="url(#g1-c)"/><path d="M198 195 L284 187" class="dg-l" marker-end="url(#g1-n)"/><path d="M456 67 L510 67" class="dg-l c" marker-end="url(#g1-c)"/><path d="M456 187 L510 187" class="dg-l dash" marker-end="url(#g1-n)"/><text x="365" y="128" class="dg-ct" text-anchor="middle">hard link : 2 noms, 1 inode</text></svg><figcaption>Un hard link est un deuxième nom pour le même inode. Un lien symbolique est un petit fichier qui contient un chemin.</figcaption></figure>
<!-- /schema:liens -->

| | Hard link | Lien symbolique |
| --- | --- | --- |
| Pointe vers | le même inode | un chemin |
| Autre système de fichiers | non | oui |
| Vers un répertoire | non | oui |
| Si l'original est supprimé | continue de marcher | lien cassé |

```bash
ln  data.csv backup.csv     # hard link
ln -s /opt/app/v2 current   # symlink
```

## Comprendre avec une image

Imagine une bibliothèque. L'**inode** est la fiche cartonnée qui décrit un livre : sa taille, son propriétaire, ses droits, ses dates, et surtout **où sont ses pages** sur le disque. Le **nom de fichier** n'est qu'une entrée dans le catalogue d'un rayon (le répertoire) qui renvoie au numéro de la fiche.

Conséquences, qui surprennent souvent :

- l'inode ne contient **pas le nom** du fichier. Un répertoire est juste une liste « nom → numéro d'inode » ;
- **renommer** ou **déplacer** un fichier dans le même système de fichiers est instantané, même pour 50 Go : on modifie seulement le catalogue, les données ne bougent pas ;
- un même inode peut avoir **plusieurs noms** : ce sont les hard links. Ils sont parfaitement égaux, aucun n'est « l'original ».

## Les deux pannes classiques

**« No space left on device » alors que `df -h` montre de la place.** Chaque système de fichiers a un nombre limité d'inodes, fixé à sa création. Des millions de petits fichiers (cache, sessions PHP, mails en file d'attente) peuvent les épuiser avant l'espace disque. `df -i` le montre.

**Un disque plein qui ne se vide pas après un `rm`.** Si un processus garde le fichier ouvert (typiquement un log en cours d'écriture), l'inode survit : le nom a disparu, mais l'espace reste occupé tant que le processus tourne.

```bash
lsof +L1                    # fichiers supprimés mais encore ouverts
# puis redémarrer le service, ou vider le fichier sans le supprimer :
: > /var/log/api/app.log
```

## Quand utiliser quel lien

- **Lien symbolique** : le cas courant. Pointer `current` vers la version déployée (`/opt/app/v2`), et basculer d'un coup en changeant la cible. C'est un petit fichier qui contient un chemin, comme un raccourci.
- **Hard link** : plus rare. Utilisé par certains outils de sauvegarde pour que des copies identiques ne prennent pas de place deux fois.

> **À retenir.** Supprimer un fichier (`rm`) retire seulement un nom. Les données ne disparaissent que quand l'inode n'a plus aucun nom **et** qu'aucun processus ne le garde ouvert.
