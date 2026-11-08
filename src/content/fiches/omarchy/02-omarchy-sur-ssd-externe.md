---
title: Omarchy sur un SSD externe, à côté de Windows
chapter: 2
order: 1
duration: 14
level: Débutant
tags:
- SSD externe
- UEFI
- Limine
- dual boot
- LUKS
- Secure Boot
cards:
- q: Comment démarrer sur le SSD externe plutôt que sur Windows ?
  a: 'Au démarrage du PC, appuie sur la touche du **menu de démarrage** de la carte mère (souvent **F8** sur ASUS, **F11** sur MSI, **F12** sur Gigabyte) et choisis le SSD. Pour démarrer dessus par défaut, mets-le en tête de l''**ordre de démarrage** dans l''UEFI : Windows démarrera tout seul quand le SSD est débranché.'
- q: Qu'est-ce que l'ESP, et où est celle d'Omarchy ?
  a: 'L''**ESP** (EFI System Partition) est une petite partition FAT32 où l''UEFI cherche les chargeurs de démarrage. Avec une installation complète sur le T7, Omarchy a **sa propre ESP sur le T7**, avec **Limine** dedans : le disque Windows n''est pas touché.'
- q: Pourquoi l'heure de Windows est-elle fausse après un passage sous Linux ?
  a: 'L''horloge matérielle (**RTC**) est lue en **heure locale** par Windows et en **UTC** par Linux. Linux y écrit l''UTC, Windows la lit comme locale : décalage d''1 ou 2 h. Solution propre : dire à Windows que la RTC est en UTC (clé de registre **RealTimeIsUniversal**), ou laisser Windows resynchroniser l''heure par Internet.'
- q: Pourquoi Omarchy demande-t-il de désactiver Secure Boot, et quel lien avec Valorant ?
  a: 'Omarchy démarre avec **Limine**, qui n''est pas signé par Microsoft : avec **Secure Boot** actif, l''UEFI refuse de le lancer. Or **Vanguard** (l''anti-cheat de Valorant) exige Secure Boot actif sous Windows 11 (erreur **VAN 9003**). Solution simple : activer Secure Boot pour jouer, le couper pour Omarchy.'
- q: Pourquoi désactiver le démarrage rapide de Windows ?
  a: 'Le **démarrage rapide** (Fast Startup) met Windows en hibernation partielle au lieu de l''éteindre : ses partitions NTFS restent « verrouillées », l''horloge et certains périphériques restent dans l''état de Windows. Le couper évite les surprises quand tu démarres un autre système.'
- q: Comment vérifier que le T7 tourne à pleine vitesse ?
  a: Branche-le sur un **port USB arrière** de la carte mère (USB 3.2 Gen 2, 10 Gb/s, souvent rouge ou marqué 10 Gbps). `lsusb -t` doit montrer **Driver=uas** et **10000M**. `omarchy disk speedtest` mesure le débit réel (le T7 vise environ 1 000 Mo/s).
- q: Que protège le chiffrement LUKS sur un disque externe ?
  a: 'Tout le contenu du T7. Un disque externe se perd ou se vole plus facilement qu''un disque interne : sans le mot de passe, les données sont illisibles. Le mot de passe est demandé à chaque démarrage, avant le chargement du système.'
quiz:
- q: Après une soirée sous Omarchy, tu rallumes Windows et l'horloge a 2 h de retard. Que fais-tu ?
  options:
  - Tu réinstalles Windows
  - Tu règles Windows pour lire l'horloge matérielle en UTC (ou tu le laisses resynchroniser l'heure en ligne)
  - Tu changes la pile de la carte mère
  - Tu désactives le Wi-Fi
  answer: 1
  explain: Linux écrit l'UTC dans l'horloge matérielle, Windows la lit en heure locale. La clé de registre RealTimeIsUniversal règle le problème durablement.
- q: Valorant refuse de se lancer sous Windows avec l'erreur VAN 9003, depuis que tu as installé Omarchy. Cause probable ?
  options:
  - Le T7 est trop lent
  - Secure Boot est resté désactivé dans l'UEFI
  - Omarchy a supprimé Vanguard
  - Le pare-feu d'Omarchy bloque Riot
  answer: 1
  explain: Vanguard exige Secure Boot sous Windows 11. Réactive-le pour jouer, coupe-le pour démarrer Omarchy (ou explore plus tard la signature de Limine avec tes propres clés, une piste avancée).
- q: Le T7 est branché en façade et `lsusb -t` affiche 480M. Que se passe-t-il ?
  options:
  - Tout va bien
  - 'Il fonctionne en USB 2 : branche-le sur un port USB 3.2 arrière, avec le câble d''origine'
  - Il faut formater le disque
  - LUKS ralentit le disque
  answer: 1
  explain: 480M, c'est l'USB 2 (environ 40 Mo/s réels). Un port USB 3.2 Gen 2 et un bon câble rendent le système nettement plus réactif.
- q: Tu réinstalles Omarchy sur le T7. Quelle précaution évite de toucher au disque Windows ?
  options:
  - Aucune, l'installateur devine
  - Choisir avec soin le T7 comme disque cible (et, le plus sûr, débrancher le disque Windows pendant l'installation)
  - Désactiver le Wi-Fi
  - Installer depuis Windows
  answer: 1
  explain: Une installation complète efface le disque choisi. Sur un PC fixe, débrancher temporairement le disque Windows supprime tout risque d'erreur.
---

Omarchy est installé sur ton **Samsung T7** (SSD externe USB), et tu démarres dessus quand tu en as besoin, Windows restant ton système principal. Ce montage a de vrais avantages (Windows intact, système transportable, chiffré), mais il crée quelques pièges propres au double démarrage. Le manuel officiel d'Omarchy couvre le double démarrage sur un même disque, pas le cas d'un disque externe : ce qui suit vient du fonctionnement général de Linux et de l'UEFI, et c'est signalé comme tel.

> **Les outils cités dans cette fiche.**
> - **UEFI** : le micrologiciel de la carte mère (successeur du BIOS) qui démarre le PC et choisit sur quel disque lancer un système.
> - **ESP** (EFI System Partition) : une petite partition FAT32 où l'UEFI trouve les chargeurs de démarrage de chaque système.
> - **Limine** : le chargeur de démarrage d'Omarchy ; il affiche un menu au démarrage, dont les snapshots pour revenir en arrière.
> - **Secure Boot** : une option de l'UEFI qui ne lance que des chargeurs signés par une clé reconnue (par défaut celle de Microsoft).
> - **TPM** : une puce de sécurité de la carte mère qui stocke des clés ; Windows 11 l'exige, Omarchy demande de la couper à l'installation.
> - **LUKS** : le système de chiffrement de disque standard de Linux ; Omarchy l'active par défaut.
> - **RTC** (Real-Time Clock) : l'horloge matérielle de la carte mère, alimentée par une pile, qui garde l'heure PC éteint.
> - **UTC** : le temps universel de référence, sans fuseau horaire ni heure d'été.
> - **UAS** (USB Attached SCSI) : le mode de transfert rapide des disques USB, qui remplace l'ancien mode « stockage de masse ».
> - **TRIM** : une commande qui signale au SSD les blocs libérés, pour qu'il garde ses performances dans le temps ; `fstrim` l'envoie.
> - **Vanguard** : l'anti-cheat de Riot (Valorant), qui tourne au niveau du noyau de Windows.
> - **BitLocker** : le chiffrement de disque de Windows.

## Comprendre : qui démarre quoi

Quand tu allumes le PC, l'**UEFI** parcourt ses disques dans l'ordre de démarrage et lance le premier chargeur qu'il trouve dans une **ESP**. Avec une installation complète d'Omarchy sur le T7, chaque disque a la sienne :

<!-- schema:demarrage -->
<figure class="diagram"><svg viewBox="0 0 680 330" role="img" aria-label="Deux disques, deux chargeurs" style="--minw:560px"><defs><marker id="g2-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g2-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g2-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g2-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="220" y="14" width="240" height="50" rx="9"/></g><text x="340.0" y="36.0" class="dg-t" text-anchor="middle" style="--d:0">UEFI</text><text x="340.0" y="54.0" class="dg-s" text-anchor="middle" style="--d:0">ordre de démarrage ou F8 / F11 / F12</text><rect x="14" y="100" width="300" height="210" rx="12" class="dg-zone "/><text x="26" y="118" class="dg-zl" text-anchor="start">disque interne</text><rect x="366" y="100" width="300" height="210" rx="12" class="dg-zone dg-zc"/><text x="378" y="118" class="dg-zl" text-anchor="start">Samsung T7 (USB 3.2)</text><g class="dg-box dg-pop" style="--d:1"><rect x="34" y="132" width="260" height="44" rx="9"/></g><text x="164.0" y="151.0" class="dg-t" text-anchor="middle" style="--d:1">ESP Windows</text><text x="164.0" y="169.0" class="dg-s" text-anchor="middle" style="--d:1">Windows Boot Manager</text><g class="dg-box dg-pop" style="--d:2"><rect x="34" y="200" width="260" height="44" rx="9"/></g><text x="164.0" y="219.0" class="dg-t" text-anchor="middle" style="--d:2">Windows</text><text x="164.0" y="237.0" class="dg-s" text-anchor="middle" style="--d:2">BitLocker, Vanguard, Secure Boot</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="386" y="132" width="260" height="44" rx="9"/></g><text x="516.0" y="151.0" class="dg-t" text-anchor="middle" style="--d:1">ESP Omarchy</text><text x="516.0" y="169.0" class="dg-s" text-anchor="middle" style="--d:1">Limine (menu des snapshots)</text><g class="dg-box dg-a dg-pop" style="--d:2"><rect x="386" y="200" width="260" height="44" rx="9"/></g><text x="516.0" y="219.0" class="dg-t" text-anchor="middle" style="--d:2">partition LUKS</text><text x="516.0" y="237.0" class="dg-s" text-anchor="middle" style="--d:2">mot de passe au démarrage</text><g class="dg-box dg-ok dg-pop" style="--d:3"><rect x="386" y="258" width="260" height="40" rx="9"/></g><text x="516.0" y="283.0" class="dg-s" text-anchor="middle" style="--d:3">Omarchy (Btrfs)</text><path d="M220 39 L164 39 L164 130" class="dg-l" marker-end="url(#g2-n)"/><path d="M460 39 L516 39 L516 130" class="dg-l c" marker-end="url(#g2-c)"/><text x="176" y="84" class="dg-s" text-anchor="start">T7 débranché</text><text x="504" y="84" class="dg-s" text-anchor="end">T7 branché, en premier</text><path d="M164 176 L164 198" class="dg-l" marker-end="url(#g2-n)"/><path d="M516 176 L516 198" class="dg-l c" marker-end="url(#g2-c)"/><path d="M516 244 L516 256" class="dg-l c" marker-end="url(#g2-c)"/></svg><figcaption>Chaque disque a sa propre partition de démarrage : Omarchy n&#x27;écrit rien sur le disque Windows.</figcaption></figure>
<!-- /schema:demarrage -->

- le disque interne : ESP Windows, avec le **Windows Boot Manager** ;
- le T7 : ESP Omarchy, avec **Limine**, puis la partition chiffrée par **LUKS** qui contient le système.

Les deux systèmes ne se marchent donc pas dessus : Windows ne sait pas qu'Omarchy existe, et Omarchy n'a rien écrit sur le disque Windows. C'est la configuration la plus sûre possible pour essayer Linux.

## Démarrer sur le T7

Deux façons de faire :

| Méthode | Comment | Pour qui |
| --- | --- | --- |
| **Menu de démarrage** ponctuel | au démarrage, touche F8 (ASUS), F11 (MSI), F12 (Gigabyte, la plupart des autres) ; choisir le T7 | tu démarres Omarchy de temps en temps |
| **Ordre de démarrage** permanent | dans l'UEFI (touche Suppr ou F2), mettre le T7 en premier | le PC démarre Omarchy si le T7 est branché, sinon Windows |

La seconde est la plus confortable : T7 branché, Omarchy ; T7 débranché, Windows, sans rien toucher. Certaines cartes mères « oublient » un disque USB absent et le retirent de l'ordre de démarrage : si c'est ton cas, reste sur le menu ponctuel.

Une fois le T7 choisi, Omarchy demande le **mot de passe de chiffrement** (LUKS), puis démarre. Le menu **Limine** n'apparaît pas forcément : il sert surtout à démarrer un **snapshot** en cas de problème (fiche 7).

Le manuel officiel propose aussi `limine-scan`, qui ajoute Windows au menu Limine. C'est utile quand les deux systèmes sont sur le même disque ; avec ton T7, le menu de l'UEFI fait le travail sans rien modifier.

## Les quatre pièges du double démarrage

### 1. L'horloge décalée

L'horloge matérielle (RTC) ne connaît pas les fuseaux horaires. **Linux** y écrit l'heure **UTC**, **Windows** la lit comme une heure **locale**. Après un passage sous Omarchy, Windows affiche 1 h (hiver) ou 2 h (été) de retard en France, jusqu'à sa prochaine synchronisation.

La solution propre consiste à dire à Windows que la RTC est en UTC, avec une clé de registre (dans une invite de commandes administrateur sous Windows) :

```
reg add "HKLM\SYSTEM\CurrentControlSet\Control\TimeZoneInformation" /v RealTimeIsUniversal /t REG_DWORD /d 1 /f
```

L'inverse existe côté Linux (`timedatectl set-local-rtc 1`), mais le wiki Arch le déconseille : l'heure locale dans la RTC pose des problèmes au changement d'heure. Si tu ne veux toucher à rien, la synchronisation automatique de Windows corrige l'heure en quelques minutes.

### 2. Secure Boot et Valorant

Omarchy demande de **désactiver Secure Boot et le TPM** à l'installation : Limine n'est pas signé par Microsoft, donc un UEFI en Secure Boot refuse de le lancer. Le problème : **Vanguard**, l'anti-cheat de Valorant, exige Secure Boot actif sous Windows 11 et affiche sinon l'erreur **VAN 9003**. Et Windows 11 a besoin du TPM.

En pratique, garde le **TPM activé** (il gêne l'installation, pas le démarrage d'Omarchy), et pour Secure Boot :

- **la solution simple** : l'activer pour jouer, le désactiver avant de démarrer Omarchy ;
- **la piste avancée** (hors manuel Omarchy) : signer Limine avec tes propres clés grâce à `sbctl`, en gardant celles de Microsoft pour Windows. Elle permet de laisser Secure Boot allumé en permanence, mais une erreur peut rendre un système non démarrable : à réserver pour quand tu seras à l'aise.

### 3. Le démarrage rapide de Windows

Le **démarrage rapide** (Panneau de configuration, Options d'alimentation, « Choisir l'action des boutons d'alimentation ») ne ferme pas vraiment Windows : il l'hiberne en partie. Désactive-le : les deux systèmes partent d'un matériel « propre », et tu ne risques pas d'abîmer une partition Windows si tu l'ouvres un jour depuis Linux.

### 4. BitLocker

Si le disque Windows est chiffré par BitLocker, un changement dans l'UEFI (Secure Boot, ordre de démarrage) peut déclencher une demande de **clé de récupération** BitLocker. Note-la avant de jouer avec ces réglages (elle est dans ton compte Microsoft). Le manuel Omarchy précise que BitLocker est incompatible avec une installation sur le **même disque** que Windows ; ton T7 séparé évite ce cas.

## Tirer le meilleur du T7

| Point | Pourquoi | Comment vérifier |
| --- | --- | --- |
| **Port USB 3.2 Gen 2 arrière** | les ports en façade passent par un câble interne, parfois en USB 2 ou instable | `lsusb -t` : `Driver=uas`, `10000M` |
| **Câble d'origine** | un câble USB 2 bride tout à 40 Mo/s | même commande |
| **Mode UAS** | plus rapide et moins gourmand en processeur que l'ancien mode | `Driver=uas` (et pas `usb-storage`) |
| **TRIM** | garde les performances du SSD dans le temps | `lsblk --discard` (DISC-GRAN non nul), `systemctl status fstrim.timer` |
| **Débit réel** | savoir si tout va bien | `omarchy disk speedtest` (ou *Trigger > Speed Test > Disk*) |

Le T7 annonce environ 1 000 Mo/s : en USB 3.2 Gen 2, Omarchy y tourne presque comme sur un disque interne. En USB 2, tout devient lent, et c'est la cause numéro un d'un « Linux qui rame » sur disque externe.

### Les règles de vie

- **Ne débranche jamais le T7 système en marche**, même une seconde : c'est l'équivalent d'arracher le disque interne d'un PC allumé. Éteins avec **Super+Échap** (menu Système).
- **Évite les hubs USB et les rallonges** pour le disque système.
- **La veille** fonctionne, mais certaines cartes mères coupent l'alimentation USB en veille : si Omarchy plante au réveil, désactive l'option d'économie d'énergie USB dans l'UEFI, ou préfère l'extinction.
- **L'hibernation** (fiche 16) écrit la mémoire sur le T7 : il faut un espace égal à ta RAM, et le T7 doit être branché au réveil.

## Et sur un autre PC ?

Le T7 est transportable : Arch embarque des pilotes génériques, et Omarchy démarre souvent sur une autre machine (Secure Boot coupé, menu de démarrage). Mais ce n'est pas garanti : carte graphique différente (surtout NVIDIA, qui demande ses propres pilotes), écrans à reconfigurer (fiche 9). Considère-le comme un bonus, pas comme une fonction.

## Si tu réinstalles un jour

- Choisis **Full disk install** sur le **T7** ; l'installateur efface le disque choisi.
- Le plus sûr sur un PC fixe : **débranche le disque Windows** pendant l'installation, puis rebranche-le.
- Garde le **chiffrement** (proposé par défaut) : sur un disque externe, c'est ta protection en cas de perte.
- Clavier **filaire** ou sans fil **2,4 GHz** pour l'installation (le Bluetooth n'est pas encore actif à ce moment-là).

> **À retenir.** Avec Omarchy sur le T7, chaque disque a son propre chargeur : Windows reste intact, et l'UEFI choisit qui démarre. Les pièges sont connus : horloge décalée (RealTimeIsUniversal côté Windows), Secure Boot à rallumer pour Valorant, démarrage rapide de Windows à couper. Branche le T7 sur un port USB 3.2 arrière et ne le débranche jamais en marche.
