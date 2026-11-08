---
title: 'Mettre à jour sans casser : canaux, snapshots, noyau'
chapter: 7
order: 1
duration: 14
level: Intermédiaire
tags:
- omarchy update
- snapshots
- Limine
- canaux
- noyau
- fwupd
cards:
- q: Que fait `omarchy update`, dans l'ordre ?
  a: Il prend un **snapshot** du système, installe la dernière version d'**Omarchy** (paquets du dépôt Omarchy), lance les **migrations** (adaptations de configuration entre versions), puis met à jour **les paquets du système** depuis le miroir Arch d'Omarchy et, si tu en as, depuis l'AUR.
- q: Qu'est-ce que le canal stable, et pourquoi a-t-il un mois de retard ?
  a: 'Le canal par défaut : il suit les versions officielles d''Omarchy et un **miroir d''Arch décalé d''environ un mois**. Ce délai laisse aux mainteneurs le temps de repérer les nouveautés d''Arch qui demandent une adaptation, avant qu''elles n''arrivent chez toi.'
- q: Quels sont les quatre canaux ?
  a: '**stable** (défaut, recommandé), **rc** (validation avant une version majeure), **edge** (derniers paquets d''Arch et de développement, pour qui sait réparer), **dev** (une copie git d''Omarchy dans `~/omarchy`, pour les contributeurs). On change avec *Update > Channel* ou `omarchy-channel-set`.'
- q: Que contient un snapshot, et que ne contient-il pas ?
  a: 'Il photographie la **racine du système** (`/` : paquets, configuration système). Il ne contient **ni `/home` ni `~/.config`** : restaurer un snapshot ne fait pas perdre tes fichiers, mais ne répare pas non plus une erreur dans tes propres réglages.'
- q: Comment revenir en arrière après une mise à jour ratée ?
  a: Redémarre et choisis, dans le **menu Limine**, le snapshot d'avant la mise à jour (date et version affichées en bas à gauche). Une fois démarré et vérifié, tu peux rendre le retour définitif avec `omarchy-snapshot restore`.
- q: Que fait `omarchy reinstall` ?
  a: 'Le grand nettoyage : réinstalle les paquets par défaut, **remet sur le canal stable**, rétrograde les paquets trop récents et **réinitialise tous les fichiers de configuration**. Tes modifications sont écrasées : c''est le dernier recours. `omarchy reinstall configs` ne remet que les configurations.'
- q: Comment changer de noyau ?
  a: '*Update > Kernel*, ou `omarchy-kernel list` puis `omarchy-kernel set <noyau>` ; effet au redémarrage. Les autres noyaux installés restent dans le menu de démarrage, ce qui permet de revenir au noyau `linux-omarchy` si un autre pose problème.'
quiz:
- q: Une mise à jour faite hier soir empêche le son de fonctionner. Première chose à essayer ?
  options:
  - Réinstaller Omarchy
  - Redémarrer sur le snapshot d'avant la mise à jour depuis le menu Limine
  - Passer sur le canal edge
  - Supprimer ~/.config
  answer: 1
  explain: 'Le snapshot ramène le système à l''état d''avant, sans toucher à tes fichiers. Si tout remarche, la mise à jour est en cause : attends un correctif ou signale-le.'
- q: Tu as cassé ton bindings.lua et Hyprland ne démarre plus correctement. Un snapshot va-t-il réparer ça ?
  options:
  - Oui, il restaure tout
  - 'Non : les snapshots ne contiennent pas ~/.config ; il faut corriger le fichier (ou `omarchy reinstall configs`)'
  - Oui, si tu passes sur edge
  - Seulement en Secure Boot
  answer: 1
  explain: Les snapshots protègent le système, pas tes réglages. D'où l'intérêt de versionner ses dotfiles avec git (fiche 8).
- q: Tu as activé Setup > Direct Boot pour gagner une seconde au démarrage. Quel inconvénient ?
  options:
  - Aucun
  - 'Le menu Limine est sauté : pour démarrer un snapshot, il faudra choisir Limine dans le menu de démarrage de l''UEFI'
  - Le chiffrement est désactivé
  - Les mises à jour sont bloquées
  answer: 1
  explain: 'Le manuel le précise : si tu arrives directement au déchiffrement, choisis Limine dans le menu de démarrage de la carte mère pour retrouver les snapshots.'
- q: Tu démarres Omarchy depuis le T7 une fois toutes les trois semaines. Quel canal choisir ?
  options:
  - edge, pour avoir les dernières nouveautés
  - stable, et lancer `omarchy update` en début de session
  - dev
  - Aucun, ne jamais mettre à jour
  answer: 1
  explain: Stable est le plus sûr, surtout quand on rattrape plusieurs semaines de mises à jour d'un coup. Mettre à jour au début d'une session laisse le temps de réagir s'il y a un souci.
---

Sur une distribution en mise à jour continue, la vraie question n'est pas « faut-il mettre à jour ? » mais « comment mettre à jour sans risque ? ». Omarchy répond avec trois outils : des **canaux** qui filtrent les nouveautés, des **snapshots** pris avant chaque mise à jour, et une réinstallation des configurations en dernier recours. D'après le manuel Omarchy 4.

> **Les outils cités dans cette fiche.**
> - **snapshot** : une photo instantanée de l'état du système de fichiers, qu'on peut redémarrer ou restaurer.
> - **Btrfs** : le système de fichiers utilisé par Omarchy ; il sait prendre des snapshots presque instantanés, sans copier les données.
> - **Limine** : le chargeur de démarrage d'Omarchy ; son menu liste les snapshots démarrables.
> - **canal** : la source de mises à jour suivie (stable, rc, edge, dev).
> - **migration** : un script d'Omarchy qui adapte ta configuration quand une nouvelle version change quelque chose.
> - **noyau** (kernel) : le cœur du système ; Omarchy fournit le sien, `linux-omarchy`.
> - **fwupd** / **LVFS** : l'outil Linux de mise à jour des micrologiciels (BIOS, SSD) et le service des constructeurs qui les fournit.
> - **firmware** (micrologiciel) : le logiciel embarqué dans un composant matériel (carte mère, SSD, dock).

## Comprendre : le filet de sécurité

<!-- schema:miseajour -->
<figure class="diagram"><svg viewBox="0 0 680 300" role="img" aria-label="Une mise à jour avec filet" style="--minw:560px"><defs><marker id="g4-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g4-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g4-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g4-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="14" y="40" width="150" height="56" rx="9"/></g><text x="89.0" y="65.0" class="dg-t" text-anchor="middle" style="--d:0">snapshot</text><text x="89.0" y="83.0" class="dg-s" text-anchor="middle" style="--d:0">photo de /</text><g class="dg-box dg-pop" style="--d:1"><rect x="182" y="40" width="150" height="56" rx="9"/></g><text x="257.0" y="65.0" class="dg-t" text-anchor="middle" style="--d:1">Omarchy</text><text x="257.0" y="83.0" class="dg-s" text-anchor="middle" style="--d:1">dépôt Omarchy</text><path d="M166 68 L180 68" class="dg-l c" marker-end="url(#g4-c)"/><g class="dg-box dg-pop" style="--d:2"><rect x="350" y="40" width="150" height="56" rx="9"/></g><text x="425.0" y="65.0" class="dg-t" text-anchor="middle" style="--d:2">migrations</text><text x="425.0" y="83.0" class="dg-s" text-anchor="middle" style="--d:2">configs adaptées</text><path d="M334 68 L348 68" class="dg-l c" marker-end="url(#g4-c)"/><g class="dg-box dg-pop" style="--d:3"><rect x="518" y="40" width="150" height="56" rx="9"/></g><text x="593.0" y="65.0" class="dg-t" text-anchor="middle" style="--d:3">paquets Arch</text><text x="593.0" y="83.0" class="dg-s" text-anchor="middle" style="--d:3">miroir stable (≈ 1 mois)</text><path d="M502 68 L516 68" class="dg-l c" marker-end="url(#g4-c)"/><text x="14" y="26" class="dg-zl" text-anchor="start">omarchy update</text><g class="dg-box dg-ok dg-pop" style="--d:4"><rect x="14" y="150" width="300" height="56" rx="9"/></g><text x="164.0" y="175.0" class="dg-t" text-anchor="middle" style="--d:4">tout va bien</text><text x="164.0" y="193.0" class="dg-s" text-anchor="middle" style="--d:4">tu continues, le snapshot reste disponible</text><g class="dg-box dg-a dg-pop" style="--d:4"><rect x="366" y="150" width="300" height="56" rx="9"/></g><text x="516.0" y="175.0" class="dg-t" text-anchor="middle" style="--d:4">quelque chose casse</text><text x="516.0" y="193.0" class="dg-s" text-anchor="middle" style="--d:4">redémarrer, menu Limine, snapshot d&#x27;avant</text><path d="M588 96 L588 116 L164 116 L164 148" class="dg-l ok" marker-end="url(#g4-ok)"/><path d="M588 116 L516 116 L516 148" class="dg-l a" marker-end="url(#g4-a)"/><g class="dg-box dg-ghost dg-pop" style="--d:5"><rect x="366" y="236" width="300" height="50" rx="9"/></g><text x="516.0" y="258.0" class="dg-t" text-anchor="middle" style="--d:5">omarchy-snapshot restore</text><text x="516.0" y="276.0" class="dg-s" text-anchor="middle" style="--d:5">rendre le retour définitif</text><path d="M516 206 L516 234" class="dg-l a" marker-end="url(#g4-a)"/><text x="14" y="250" class="dg-s" text-anchor="start">les snapshots ne couvrent ni /home</text><text x="14" y="268" class="dg-s" text-anchor="start">ni ~/.config : tes réglages se protègent avec git</text></svg><figcaption>Le snapshot pris avant la mise à jour est ton bouton « annuler ».</figcaption></figure>
<!-- /schema:miseajour -->

À chaque `omarchy update`, Omarchy commence par **photographier** le système. Si la mise à jour casse quelque chose, tu redémarres sur la photo d'avant. Le principe est le même que les points de restauration de Windows, en beaucoup plus rapide et fiable : Btrfs ne copie rien, il « fige » simplement l'état des fichiers à cet instant.

## Mettre à jour

Trois portes d'entrée, même effet :

- l'**icône en flèche circulaire** à droite de l'horloge, quand une version est disponible ;
- **Super+Espace > Update > Omarchy** ;
- **`omarchy update`** dans un terminal (le plus lisible : tu vois tout ce qui se passe).

Étapes :

1. **snapshot** de la racine du système ;
2. installation de la **dernière version d'Omarchy** (paquets du dépôt Omarchy) ;
3. **migrations** : adaptations des fichiers de configuration quand une version change de structure ;
4. mise à jour des **paquets Arch** depuis le miroir d'Omarchy, puis de l'**AUR** si tu en utilises.

Avec un système sur le T7 que tu démarres de temps en temps, prends l'habitude de lancer la mise à jour **en début de session**, pas juste avant d'éteindre : s'il y a un souci, tu as le temps d'y réagir.

## Les canaux

| Canal | Ce qu'il suit | Pour qui |
| --- | --- | --- |
| **stable** (défaut) | versions officielles + miroir Arch décalé d'**environ un mois** | tout le monde, et toi |
| **rc** | versions candidates avant une version majeure | testeurs volontaires |
| **edge** | derniers développements + paquets Arch du jour | qui sait réparer un système cassé |
| **dev** | code source d'Omarchy dans `~/omarchy` + paquets edge | contributeurs d'Omarchy |

Le mois de décalage du canal stable est son principal atout : les nouveautés d'Arch qui demandent une adaptation (un changement de format de configuration, par exemple) sont repérées et corrigées avant d'arriver chez toi. Pour changer : *Update > Channel* ou `omarchy-channel-set`.

## Les snapshots

| Point | Détail |
| --- | --- |
| Ce qui est sauvegardé | la **racine** `/` : paquets, configuration système |
| Ce qui ne l'est pas | **`/home`** et donc **`~/.config`** : tes fichiers et tes réglages |
| Quand | automatiquement avant chaque mise à jour, ou à la main |
| Créer à la main | `omarchy-snapshot create` |
| Démarrer un snapshot | menu **Limine** au démarrage (date et version en bas à gauche) |
| Rendre le retour définitif | `omarchy-snapshot restore` |

Que tes fichiers ne soient pas dans les snapshots est une bonne nouvelle : revenir en arrière ne fait jamais perdre de documents. Mais c'est aussi une limite : si **tu** casses un fichier de `~/.config`, aucun snapshot ne le répare. C'est pour ça qu'on versionne ses dotfiles (fiche 8).

Prends un snapshot manuel avant toute manipulation risquée : nouveau pilote graphique, changement de noyau, gros paquet AUR.

### Le piège de Direct Boot

*Setup > Direct Boot* fait sauter le menu Limine pour démarrer un peu plus vite. Le menu des snapshots disparaît alors aussi. Le manuel indique la sortie : si tu arrives directement à l'écran de déchiffrement, choisis **Limine** dans le menu de démarrage de la carte mère. Avec un système sur disque externe, garder Limine visible est plus confortable.

## Après une mise à jour : les fichiers .bak

Quand une mise à jour doit remettre une configuration par défaut à la place de la tienne, Omarchy garde ta version en **`.bak`** à côté (par exemple `bindings.lua.bak`). Après une grosse version, cherche-les :

```bash
fd '\.bak$' ~/.config
```

Compare (`diff fichier.bak fichier`) et reporte tes réglages dans le nouveau fichier.

## Le noyau

Omarchy démarre sur son noyau **`linux-omarchy`**, mais tu peux en installer d'autres (par exemple `linux-lts`, le noyau à support long d'Arch, plus conservateur).

| Action | Menu | Commande |
| --- | --- | --- |
| Voir le noyau par défaut | *Update > Kernel* | `omarchy-kernel` |
| Lister les noyaux installés | *Update > Kernel* | `omarchy-kernel list` |
| Changer le noyau par défaut | *Update > Kernel* | `omarchy-kernel set <noyau>` |

Le changement prend effet au redémarrage, et les autres noyaux restent dans le menu de démarrage. Installer `linux-lts` à côté est une bonne assurance : si un nouveau noyau pose problème avec ton matériel, tu démarres sur l'autre.

## Les micrologiciels

*Update > Firmware* installe **fwupd** au premier lancement puis récupère les mises à jour de BIOS, de SSD et de docks publiées par les constructeurs sur le **LVFS**. Certaines s'appliquent au redémarrage. Sur un PC fixe, la couverture dépend de la marque de la carte mère ; le T7 lui-même se met à jour avec l'outil Samsung Magician sous Windows.

## En dernier recours

| Commande | Effet |
| --- | --- |
| `omarchy reinstall configs` | remet **toutes les configurations** par défaut |
| `omarchy reinstall` | réinstalle les paquets par défaut, **repasse en stable**, rétrograde les paquets trop récents et remet toutes les configurations |

Dans les deux cas, tes modifications de configuration sont écrasées : sauvegarde `~/.config` avant (ou mieux, aie-le dans git).

> **À retenir.** Mets à jour avec `omarchy update`, en début de session, sur le canal stable. Chaque mise à jour est précédée d'un snapshot du système, démarrable depuis le menu Limine : c'est ton bouton « annuler ». Les snapshots ne couvrent pas `~/.config` : tes réglages se protègent avec git. Un second noyau (`linux-lts`) et un snapshot manuel avant toute manipulation risquée complètent le filet.
