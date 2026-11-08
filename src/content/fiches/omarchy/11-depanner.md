---
title: Dépanner Omarchy, de la panne bénigne au système qui ne démarre plus
chapter: 11
order: 1
duration: 14
level: Intermédiaire
tags:
- dépannage
- TTY
- journalctl
- faillock
- omarchy-debug
- arch-chroot
cards:
- q: Quelle est la première question à se poser face à une panne ?
  a: '**Qu''est-ce qui a changé ?** Une mise à jour (snapshot), un réglage à toi (git, `.bak`), un matériel branché, un paquet AUR. Ensuite : **à quelle couche** appartient le problème (Hyprland, shell, service, noyau, matériel).'
- q: Qu'est-ce qu'une console TTY, et comment y accéder ?
  a: 'Une **console en mode texte**, indépendante de l''interface graphique. **Ctrl+Alt+F2** en ouvre une (F3, F4… d''autres) : tu te connectes avec ton nom et ton mot de passe, et tu peux corriger un fichier, lire des journaux ou mettre à jour même si Hyprland est cassé.'
- q: Ton compte est bloqué après plusieurs mauvais mots de passe. Que faire ?
  a: C'est **faillock**, qui verrouille temporairement un compte après des échecs répétés. Dans une console (**Ctrl+Alt+F2**), connecte-toi en root puis `faillock --reset --user <ton_nom>`. Attendre quelques minutes suffit aussi souvent.
- q: Le Wi-Fi, le Bluetooth ou le son ne répondent plus. Premier geste ?
  a: '*Update > Hardware* (ou **Super+Ctrl+H**) : il **recharge le sous-système** concerné sans redémarrer. Pour le son, vérifie aussi la **sortie choisie** en cliquant sur l''icône du haut-parleur (écran HDMI, casque, enceintes).'
- q: Que fait `omarchy-debug` ?
  a: Il rassemble les informations utiles au diagnostic (versions, matériel, journaux) pour les partager quand tu demandes de l'aide, par exemple sur le canal **#omarchy-help** du Discord d'Omarchy.
- q: Dans quel ordre essayer les solutions de retour en arrière ?
  a: 1. annuler **ton dernier changement** (git, `.bak`) ; 2. démarrer le **snapshot** d'avant la mise à jour ; 3. `omarchy reinstall configs` ; 4. `omarchy reinstall` ; 5. réinstallation complète. Du plus léger au plus lourd.
- q: Que faire si le système ne démarre plus du tout, même avec un snapshot ?
  a: Démarrer sur la **clé d'installation** Omarchy (ou une ISO Arch), ouvrir le disque chiffré avec `cryptsetup open`, le monter, puis entrer dedans avec **`arch-chroot`** pour réparer (réinstaller un paquet, corriger un fichier). C'est la méthode générale d'Arch, hors manuel Omarchy.
quiz:
- q: Après avoir modifié bindings.lua, l'écran reste noir à l'ouverture de session. Que fais-tu d'abord ?
  options:
  - Tu réinstalles Omarchy
  - Ctrl+Alt+F2, tu te connectes, tu annules ta modification (git checkout ou éditeur), puis tu reviens sur la session
  - Tu restaures un snapshot
  - Tu formates le T7
  answer: 1
  explain: Le problème vient de ton fichier, que les snapshots ne couvrent pas. Une console texte suffit pour le corriger.
- q: Plus de son depuis que tu as branché l'écran en HDMI. Cause la plus probable ?
  options:
  - Le noyau est cassé
  - 'La sortie audio est passée sur l''écran : clique sur l''icône du haut-parleur et choisis la bonne sortie'
  - Le pare-feu bloque le son
  - Il faut réinstaller PipeWire
  answer: 1
  explain: Un écran HDMI ou DisplayPort est aussi une sortie audio. Shift+Muet passe aussi à la sortie suivante.
- q: Une appli précise plante au lancement. Où trouver la cause ?
  options:
  - La lancer depuis un terminal pour lire ses messages d'erreur, puis `journalctl -b -p err`
  - Redémarrer jusqu'à ce que ça marche
  - Changer de thème
  - Passer sur le canal edge
  answer: 0
  explain: Lancée depuis un terminal, une appli affiche ses erreurs. Les journaux systemd complètent le tableau.
- q: Tu demandes de l'aide sur Discord. Que fournir en priorité ?
  options:
  - Une capture floue de l'écran
  - La sortie de `omarchy-debug`, ce que tu as changé récemment et le message d'erreur exact
  - Ton mot de passe
  - Rien, décrire le problème suffit
  answer: 1
  explain: Les versions, le matériel, le dernier changement et l'erreur exacte permettent une réponse rapide. Ne partage jamais un mot de passe.
---

Sur Arch, on finit toujours par casser quelque chose, souvent en le personnalisant. Ce n'est pas grave si on a une méthode : savoir ce qui a changé, savoir où regarder, et connaître les retours en arrière du plus léger au plus lourd. Les solutions spécifiques viennent du manuel Omarchy 4 ; la réparation depuis une clé USB est la méthode générale d'Arch.

> **Les outils cités dans cette fiche.**
> - **TTY** (console virtuelle) : une session en mode texte, accessible avec Ctrl+Alt+F2 à F6, qui ne dépend pas de l'interface graphique.
> - **journalctl** : l'outil qui lit les journaux de systemd (services, noyau, démarrage).
> - **hyprctl** : l'outil qui interroge Hyprland (écrans, fenêtres, version, erreurs de configuration).
> - **faillock** : le mécanisme qui bloque temporairement un compte après plusieurs mots de passe erronés.
> - **PipeWire** : le serveur audio et vidéo de Linux, qui gère les sorties et entrées son.
> - **omarchy-debug** : le script d'Omarchy qui rassemble les informations de diagnostic.
> - **systemd-coredump** : le service qui capture l'état d'un programme au moment où il plante.
> - **cryptsetup** : l'outil qui ouvre et gère les volumes chiffrés LUKS.
> - **arch-chroot** : une commande qui « entre » dans un système installé depuis un système de secours, pour le réparer comme s'il avait démarré.

## Comprendre : la méthode en trois questions

1. **Qu'est-ce qui a changé ?** Une mise à jour, un réglage, un paquet, un matériel. Neuf pannes sur dix suivent un changement.
2. **À quelle couche ?** Raccourci ou fenêtre : Hyprland. Barre ou menu : le shell. Wi-Fi, son : service ou matériel. Démarrage : chargeur, noyau, chiffrement.
3. **Quel est le retour en arrière le plus léger ?**

<!-- schema:depannage -->
<figure class="diagram"><svg viewBox="0 0 680 300" role="img" aria-label="Du retour en arrière le plus léger au plus lourd" style="--minw:560px"><defs><marker id="g7-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g7-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g7-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g7-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-ok dg-pop" style="--d:0"><rect x="14" y="14" width="300" height="46" rx="9"/></g><text x="164.0" y="34.0" class="dg-t" text-anchor="middle" style="--d:0">1 · annuler ton changement</text><text x="164.0" y="52.0" class="dg-s" text-anchor="middle" style="--d:0">git checkout, fichier .bak</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="14" y="70" width="370" height="46" rx="9"/></g><text x="199.0" y="90.0" class="dg-t" text-anchor="middle" style="--d:1">2 · snapshot d&#x27;avant</text><text x="199.0" y="108.0" class="dg-s" text-anchor="middle" style="--d:1">menu Limine</text><g class="dg-box dg-pop" style="--d:2"><rect x="14" y="126" width="440" height="46" rx="9"/></g><text x="234.0" y="146.0" class="dg-t" text-anchor="middle" style="--d:2">3 · omarchy reinstall configs</text><text x="234.0" y="164.0" class="dg-s" text-anchor="middle" style="--d:2">configurations par défaut</text><g class="dg-box dg-a dg-pop" style="--d:3"><rect x="14" y="182" width="510" height="46" rx="9"/></g><text x="269.0" y="202.0" class="dg-t" text-anchor="middle" style="--d:3">4 · omarchy reinstall</text><text x="269.0" y="220.0" class="dg-s" text-anchor="middle" style="--d:3">paquets + configs, canal stable</text><g class="dg-box dg-a dg-pop" style="--d:4"><rect x="14" y="238" width="580" height="46" rx="9"/></g><text x="304.0" y="258.0" class="dg-t" text-anchor="middle" style="--d:4">5 · réinstaller</text><text x="304.0" y="276.0" class="dg-s" text-anchor="middle" style="--d:4">efface tes données</text><text x="666" y="40" class="dg-s" text-anchor="end">léger</text><path d="M660 52 L660 250" class="dg-l a" marker-end="url(#g7-a)"/><text x="666" y="280" class="dg-at" text-anchor="end">lourd</text></svg><figcaption>Monte d&#x27;un barreau seulement si le précédent n&#x27;a pas suffi.</figcaption></figure>
<!-- /schema:depannage -->

## L'échelle des retours en arrière

| Niveau | Action | Quand |
| --- | --- | --- |
| 1 | annuler **ton dernier changement** (`git checkout`, fichier `.bak`) | après une modification de tes réglages |
| 2 | démarrer le **snapshot** d'avant la mise à jour (menu Limine) | après une mise à jour |
| 3 | `omarchy reinstall configs` | configuration irrécupérable |
| 4 | `omarchy reinstall` | paquets et configurations incohérents |
| 5 | réinstallation complète (ou *Setup > Reset Computer*) | plus rien ne marche ; **efface tes données** |

Monte d'un niveau seulement si le précédent n'a pas suffi.

## La console de secours

Si l'interface graphique est cassée (écran noir, Hyprland qui plante, session qui revient à l'écran de connexion), **Ctrl+Alt+F2** ouvre une console texte. Connecte-toi avec ton nom d'utilisateur et ton mot de passe, puis :

```bash
cd ~/dotfiles && git status          # qu'ai-je modifié ?
git checkout -- hypr                 # annuler les modifications de Hyprland
nvim ~/.config/hypr/bindings.lua     # ou corriger à la main
omarchy update                       # mettre à jour depuis la console si besoin
reboot
```

Depuis une session graphique qui fonctionne encore, `hyprctl configerrors` liste les erreurs de configuration de Hyprland.

## Les pannes courantes

| Symptôme | Solution |
| --- | --- |
| Wi-Fi, Bluetooth, son ou périphérique qui ne répond plus | *Update > Hardware* (ou **Super+Ctrl+H**) recharge le sous-système |
| Pas de son | clic sur l'icône du haut-parleur, choisir la bonne sortie (l'écran HDMI en est une) ; **Shift+Muet** passe à la suivante |
| Applis trop grandes ou floues | échelles de `monitors.lua` (fiche 9) |
| Compte bloqué après des erreurs de mot de passe | **Ctrl+Alt+F2**, connexion en root, `faillock --reset --user <ton_nom>` |
| Un réglage a disparu après une mise à jour | chercher le fichier `.bak` à côté |
| Problème apparu après une mise à jour | snapshot d'avant, depuis le menu Limine |
| Démarrage direct au déchiffrement, sans menu Limine | choisir Limine dans le menu de démarrage de la carte mère |
| Une appli plante au lancement | la lancer depuis un terminal pour lire l'erreur ; `journalctl -b -p err` |
| Le système rame sur le T7 | vérifier le port et le mode USB (fiche 2) |

## Lire les journaux

```bash
journalctl -b -p err            # erreurs du démarrage en cours
journalctl -b -1 -p err         # erreurs du démarrage précédent (utile après un plantage)
journalctl -u bluetooth -b      # journal d'un service
journalctl -k -b                # messages du noyau (pilotes, USB, disque)
systemctl --failed              # services en échec
coredumpctl list                # programmes qui ont planté récemment
```

`journalctl -k` est précieux avec un disque externe : un T7 mal alimenté ou un câble fatigué y laisse des traces (erreurs USB, réinitialisations du périphérique).

Omarchy capture les plantages via **systemd-coredump** et peut te les signaler ; `omarchy crash mute` coupe ces alertes si elles deviennent envahissantes.

## Demander de l'aide

1. Lance **`omarchy-debug`** : il rassemble versions, matériel et journaux.
2. Note **ce que tu as changé** juste avant la panne.
3. Copie le **message d'erreur exact** (la capture avec extraction de texte, Super+Ctrl+Impr écran, aide beaucoup).
4. Poste sur le canal **#omarchy-help** du Discord d'Omarchy, ou cherche dans le wiki Arch pour un problème système.

Ne partage jamais de mot de passe, de clé ou de jeton, même dans une capture.

## Quand plus rien ne démarre

Si même les snapshots ne démarrent pas (chargeur de démarrage abîmé, noyau manquant), la méthode générale d'Arch consiste à réparer depuis l'extérieur. Elle ne figure pas dans le manuel Omarchy ; à garder pour les cas extrêmes :

```bash
# démarré sur la clé d'installation (ou une ISO Arch)
lsblk                                         # repérer la partition chiffrée du T7
cryptsetup open /dev/sdX2 root                # la déverrouiller (adapter sdX2)
mount -o subvol=@ /dev/mapper/root /mnt       # monter le système (sous-volume Btrfs racine)
mount /dev/sdX1 /mnt/boot                     # monter l'ESP du T7
arch-chroot /mnt                              # entrer dans le système installé
```

Une fois dedans, tu peux réinstaller un paquet (`pacman -S linux-omarchy limine`), corriger un fichier ou lire les journaux. Les noms de partitions et de sous-volumes dépendent de l'installation : vérifie-les avec `lsblk -f` et `btrfs subvolume list /mnt` plutôt que de recopier ces commandes.

Avec Omarchy sur un disque externe, tu as un avantage : Windows reste démarrable sur le disque interne pendant que tu cherches une solution.

> **À retenir.** Face à une panne : qu'est-ce qui a changé, à quelle couche, et quel est le retour en arrière le plus léger (ton changement, puis le snapshot, puis la remise à zéro des configurations). Ctrl+Alt+F2 donne une console même quand Hyprland est cassé, *Update > Hardware* relance Wi-Fi, Bluetooth et son, `journalctl` dit ce qui s'est passé, et `omarchy-debug` prépare une demande d'aide.
