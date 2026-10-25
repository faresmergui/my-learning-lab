---
title: Permissions et bits spéciaux
chapter: 2
order: 1
duration: 8
level: intermédiaire
tags:
- LFCS
cards:
- q: Que signifie `chmod 750 script.sh` ?
  a: 'Propriétaire : `rwx` (7). Groupe : `r-x` (5). Autres : rien (0).'
- q: Que veut dire le droit `x` sur un **répertoire** ?
  a: Le droit d'**y entrer** et d'accéder aux fichiers qu'il contient. `r` permet seulement de lister les noms.
- q: À quoi sert le **setgid** sur un répertoire ?
  a: Les fichiers créés dedans héritent du **groupe du répertoire**, et non du groupe principal de leur créateur. Pratique pour un dossier partagé par une équipe.
- q: À quoi sert le **sticky bit**, comme sur `/tmp` ?
  a: Chacun peut créer des fichiers, mais seul leur **propriétaire** (ou root) peut les supprimer ou les renommer.
- q: Avec un `umask` de `027`, quels droits a un nouveau fichier ?
  a: '`640` (`rw-r-----`) : l''umask retire l''écriture au groupe et tous les droits aux autres, à partir de 666. Pour un répertoire : `750`, à partir de 777.'
- q: Pourquoi le setuid est-il sensible ?
  a: Un binaire setuid s'exécute avec les droits de son **propriétaire**, souvent root (comme `passwd`). Une faille dans ce binaire donne un accès root. `find / -perm -4000` les liste.
quiz:
- q: Un utilisateur a `rw-` sur un fichier, mais aucun droit sur le répertoire parent. Peut-il lire le fichier ?
  options:
  - Oui, les droits du fichier suffisent
  - Non, il lui faut au moins `x` sur le répertoire
  - Oui, s'il connaît le chemin
  - Seulement avec sudo
  answer: 1
  explain: Pour atteindre un fichier, il faut le droit `x` sur **chaque** répertoire du chemin.
- q: Quelle commande donne au groupe le droit d'écrire, sans toucher au reste ?
  options:
  - chmod 775 fichier
  - chmod g+w fichier
  - chown :g fichier
  - chmod +w fichier
  answer: 1
  explain: La notation symbolique ne modifie que ce qu'elle cite. `chmod +w` ajouterait l'écriture selon l'umask, pas seulement au groupe.
---

Chaque fichier a un **propriétaire**, un **groupe** et trois jeux de droits : pour le propriétaire, le groupe et les autres.

<!-- schema:bits -->
<figure class="diagram"><svg viewBox="0 0 680 200" role="img" aria-label="Lire une ligne de droits" style="--minw:560px"><defs><marker id="g2-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g2-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g2-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g2-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><text x="46.0" y="26" class="dg-zl" text-anchor="middle" style="--d:0">type</text><g class="dg-box dg-off dg-pop" style="--d:0"><rect x="20" y="40" width="52" height="56" rx="9"/></g><text x="46.0" y="73.0" class="dg-tl" text-anchor="middle" style="--d:0">-</text><text x="182.0" y="26" class="dg-zl" text-anchor="middle" style="--d:1">propriétaire</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="98" y="40" width="52" height="56" rx="9"/></g><text x="124.0" y="73.0" class="dg-tl" text-anchor="middle" style="--d:1">r</text><text x="124" y="116" class="dg-ct" text-anchor="middle" style="--d:1">4</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="156" y="40" width="52" height="56" rx="9"/></g><text x="182.0" y="73.0" class="dg-tl" text-anchor="middle" style="--d:1">w</text><text x="182" y="116" class="dg-ct" text-anchor="middle" style="--d:1">2</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="214" y="40" width="52" height="56" rx="9"/></g><text x="240.0" y="73.0" class="dg-tl" text-anchor="middle" style="--d:1">x</text><text x="240" y="116" class="dg-ct" text-anchor="middle" style="--d:1">1</text><text x="182.0" y="150" class="dg-t" text-anchor="middle" style="--d:1">fares : 7</text><text x="376.0" y="26" class="dg-zl" text-anchor="middle" style="--d:2">groupe</text><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="292" y="40" width="52" height="56" rx="9"/></g><text x="318.0" y="73.0" class="dg-tl" text-anchor="middle" style="--d:2">r</text><text x="318" y="116" class="dg-ct" text-anchor="middle" style="--d:2">4</text><g class="dg-box dg-off dg-pop" style="--d:2"><rect x="350" y="40" width="52" height="56" rx="9"/></g><text x="376.0" y="73.0" class="dg-tl" text-anchor="middle" style="--d:2">-</text><text x="376" y="116" class="dg-s" text-anchor="middle" style="--d:2">0</text><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="408" y="40" width="52" height="56" rx="9"/></g><text x="434.0" y="73.0" class="dg-tl" text-anchor="middle" style="--d:2">x</text><text x="434" y="116" class="dg-ct" text-anchor="middle" style="--d:2">1</text><text x="376.0" y="150" class="dg-t" text-anchor="middle" style="--d:2">devops : 5</text><text x="570.0" y="26" class="dg-zl" text-anchor="middle" style="--d:3">autres</text><g class="dg-box dg-off dg-pop" style="--d:3"><rect x="486" y="40" width="52" height="56" rx="9"/></g><text x="512.0" y="73.0" class="dg-tl" text-anchor="middle" style="--d:3">-</text><text x="512" y="116" class="dg-s" text-anchor="middle" style="--d:3">0</text><g class="dg-box dg-off dg-pop" style="--d:3"><rect x="544" y="40" width="52" height="56" rx="9"/></g><text x="570.0" y="73.0" class="dg-tl" text-anchor="middle" style="--d:3">-</text><text x="570" y="116" class="dg-s" text-anchor="middle" style="--d:3">0</text><g class="dg-box dg-off dg-pop" style="--d:3"><rect x="602" y="40" width="52" height="56" rx="9"/></g><text x="628.0" y="73.0" class="dg-tl" text-anchor="middle" style="--d:3">-</text><text x="628" y="116" class="dg-s" text-anchor="middle" style="--d:3">0</text><text x="570.0" y="150" class="dg-t" text-anchor="middle" style="--d:3">tous : 0</text><text x="340" y="186" class="dg-s" text-anchor="middle">r = 4 · w = 2 · x = 1, on additionne par groupe : 750</text></svg><figcaption>-rwxr-x--- se lit en trois groupes de trois : 7 pour le propriétaire, 5 pour le groupe, 0 pour les autres.</figcaption></figure>
<!-- /schema:bits -->

| Droit | Sur un fichier | Sur un répertoire |
| --- | --- | --- |
| `r` (4) | lire | lister les noms |
| `w` (2) | modifier | créer, supprimer, renommer dedans |
| `x` (1) | exécuter | entrer, accéder au contenu |

```bash
chmod 640 config.yaml
chmod u+x,g-w script.sh
chown fares:devops config.yaml
chmod -R g+rwX /srv/partage     # X : x seulement sur les dossiers
```


> **Les termes et outils cités dans cette fiche.**
> - **noyau** : le cœur du système d'exploitation (le kernel Linux), qui gère processus, mémoire, disques et réseau.
> - **SSH** : le protocole de connexion à distance chiffrée à une machine, en ligne de commande.
> - **conteneur** : un processus isolé qui embarque son application et ses dépendances, lancé à partir d'une image (voir le module Docker).

## Les bits spéciaux

| Bit | Valeur | Effet |
| --- | --- | --- |
| setuid | 4000 | le binaire s'exécute avec les droits de son propriétaire |
| setgid | 2000 | sur un dossier : les fichiers héritent de son groupe |
| sticky | 1000 | sur un dossier : seul le propriétaire supprime ses fichiers |

```bash
chmod 2775 /srv/partage   # dossier d'équipe : setgid + rwxrwxr-x
ls -ld /tmp               # drwxrwxrwt : le t final est le sticky bit
```

## umask

L'umask retire des droits aux nouveaux fichiers. Avec `022` (le plus courant) : fichiers en `644`, dossiers en `755`.

> **Piège classique.** `chmod -R 777` pour « régler un problème de droits » ne règle rien : il crée une faille. Cherche plutôt quel utilisateur a besoin de quel accès.

## Comment Linux décide

À chaque accès, le noyau se pose les questions **dans l'ordre** et s'arrête à la première qui correspond :

1. es-tu **root** ? Alors presque tout est permis ;
2. es-tu le **propriétaire** du fichier ? On applique les droits `u` (et seulement eux) ;
3. fais-tu partie du **groupe** du fichier ? On applique les droits `g` ;
4. sinon, on applique les droits `o` (les autres).

Conséquence surprenante : si le propriétaire a `r--` et les autres `rw-`, le propriétaire ne peut **pas** écrire, car c'est sa ligne qui s'applique.

## Lire `ls -l` sans hésiter

```
-rw-r----- 1 fares devops 1204 oct 22 config.yaml
│└┬┘└┬┘└┬┘   │     │
│ u  g  o   propriétaire, groupe
└ type : - fichier, d répertoire, l lien
```

La notation octale additionne les valeurs : `r`=4, `w`=2, `x`=1. Donc `rw-` = 6, `r--` = 4, `---` = 0 → `640`. Les trois chiffres les plus utiles : `644` (fichier lisible par tous), `600` (fichier privé, comme une clé SSH), `755` (répertoire ou script accessible à tous).

## Le piège des répertoires

Pour ouvrir `/srv/app/config/db.yaml`, il faut le droit `x` sur **chaque répertoire du chemin** : `/srv`, `/srv/app`, `/srv/app/config`. Un « Permission denied » sur un fichier aux droits corrects vient souvent d'un répertoire parent. `namei -l /srv/app/config/db.yaml` affiche les droits de chaque étape.

Autre surprise : supprimer un fichier dépend des droits sur le **répertoire** (`w`), pas sur le fichier. D'où l'intérêt du sticky bit sur `/tmp`, où tout le monde peut écrire.

## Pourquoi setuid est sensible

Un binaire setuid root (comme `passwd`, qui doit modifier `/etc/shadow`) s'exécute **en root**, quel que soit l'utilisateur qui le lance. Une faille dans un tel programme donne root à n'importe qui. C'est pourquoi on liste régulièrement ces binaires (`find / -perm -4000 -type f 2>/dev/null`) et pourquoi les conteneurs utilisent `no-new-privileges`.

> **À retenir.** Le noyau applique **une seule** ligne de droits : celle du propriétaire, sinon du groupe, sinon des autres. Sur un répertoire, `x` permet d'y entrer et `w` d'y créer ou supprimer. Un « Permission denied » vient souvent d'un répertoire parent : `namei -l` le montre.
