---
title: 'Optimiser : performances, veille, jeux et IA'
chapter: 16
order: 1
duration: 15
level: Avancé
tags:
- performances
- systemd-analyze
- hibernation
- Steam
- Proton
- agents IA
cards:
- q: Comment savoir ce qui ralentit le démarrage ?
  a: '`systemd-analyze` donne la durée totale (micrologiciel, chargeur, noyau, système), `systemd-analyze blame` classe les services par temps de démarrage, `systemd-analyze critical-chain` montre la chaîne qui retarde vraiment la session.'
- q: Quels réglages visuels allègent Hyprland ?
  a: Couper les **animations** et le **flou** dans `looknfeel.lua`, mettre les marges et bordures à 0 (ou **Super+Shift+Retour arrière** pour basculer). Sur une machine récente le gain est faible ; il compte surtout avec une carte graphique modeste.
- q: Comment vérifier quel pilote graphique est utilisé ?
  a: '`lspci -k | rg -A3 -i vga` montre la carte et le **pilote noyau en cours** (`amdgpu`, `i915`/`xe` pour Intel, `nvidia` pour le pilote propriétaire, `nouveau` pour le pilote libre NVIDIA, moins performant). Un mauvais pilote explique la plupart des saccades.'
- q: Quelles précautions pour l'hibernation sur le T7 ?
  a: '`omarchy hibernation setup` crée un espace d''échange (`/swap`) **de la taille de ta RAM** sur le T7 et demande Limine. Le T7 doit rester branché et l''UEFI doit redémarrer dessus au réveil, sinon la session hibernée est perdue. Sur un PC fixe, l''extinction est souvent plus simple.'
- q: Pourquoi Valorant ne tourne-t-il pas sous Omarchy ?
  a: Son anti-cheat **Vanguard** fonctionne dans le noyau Windows et refuse Linux. **Proton** ne peut rien y faire. Même chose pour Fortnite ou Rocket League en ligne. Pour Valorant, redémarre sur Windows (Secure Boot activé).
- q: Comment jouer à un jeu Windows sous Omarchy ?
  a: '*Install > Gaming > Steam* : **Proton** fait tourner la plupart des jeux Windows. Battle.net passe par **GE-Proton**, Lutris et Heroic couvrent les autres boutiques. Vérifie la compatibilité d''un jeu sur **ProtonDB** avant l''achat, surtout pour l''anti-cheat.'
- q: Comment fonctionnent les agents IA dans Omarchy ?
  a: 'Omarchy préconfigure des CLI d''agents (Claude, Codex, Gemini, Copilot, OpenCode…) sans en imposer : `omarchy default agent <nom>` choisit le tien, **Super+Shift+Ctrl+A** l''ouvre. Ils tournent en **mode auto-approbation** : ils exécutent des commandes sans demander, donc prudence. *Install > AI* propose LM Studio ou Ollama pour des modèles locaux.'
quiz:
- q: Ta session met 40 secondes à s'ouvrir après le mot de passe. Première commande ?
  options:
  - '`systemd-analyze blame`'
  - '`omarchy reinstall`'
  - '`pacman -Syu`'
  - '`rm -rf ~/.cache`'
  answer: 0
  explain: Elle classe les services par temps de démarrage ; souvent un seul (attente réseau, montage) explique tout.
- q: Tu veux jouer à Valorant ce soir et tu es sous Omarchy. Que fais-tu ?
  options:
  - Tu l'installes avec Proton
  - Tu redémarres sur Windows (avec Secure Boot activé)
  - Tu passes par l'AUR
  - Tu désactives le pare-feu
  answer: 1
  explain: Vanguard ne fonctionne que sous Windows avec Secure Boot. Le streaming depuis un autre PC Windows existe, mais ici Windows tourne sur la même machine.
- q: Tu lances un agent IA en mode automatique sur ton dossier de dotfiles. Quelle précaution prendre ?
  options:
  - Aucune
  - Commiter avant, garder sudo avec mot de passe, relire le `git diff` après, et le cantonner au bon dossier
  - Activer le sudo sans mot de passe pour qu'il aille plus vite
  - Lui donner tes mots de passe
  answer: 1
  explain: 'Un agent en auto-approbation exécute des commandes sans demander : git permet d''annuler, et un sudo protégé l''empêche de toucher au système.'
- q: Tu veux activer l'hibernation sur ton Omarchy installé sur le T7 avec 32 Go de RAM. À quoi faut-il penser ?
  options:
  - Rien de particulier
  - Il faut environ 32 Go libres sur le T7, et le PC doit redémarrer sur le T7 au réveil
  - L'hibernation efface le disque
  - Elle n'existe pas sous Linux
  answer: 1
  explain: L'image de la mémoire est écrite sur le disque, dans un espace de la taille de la RAM, et relue au démarrage suivant.
---

Dernière étape : rendre Omarchy plus rapide, choisir comment il s'endort, savoir ce qu'il peut faire en jeu et utiliser ses outils d'IA sans risque. Les éléments propres à Omarchy (hibernation, jeux, agents) viennent du manuel Omarchy 4 ; les outils de mesure sont du Linux général.

> **Les outils cités dans cette fiche.**
> - **systemd-analyze** : l'outil qui mesure et détaille le temps de démarrage.
> - **pilote graphique** : le code du noyau qui fait fonctionner la carte graphique (`amdgpu`, `i915`/`xe`, `nvidia`, `nouveau`).
> - **swap** : un espace disque utilisé comme mémoire de secours, et pour l'hibernation.
> - **hibernation** : sauvegarde de toute la mémoire sur le disque avant extinction, puis reprise exacte au démarrage suivant.
> - **Proton** : la couche de compatibilité de Valve (basée sur **Wine**) qui fait tourner des jeux Windows sous Linux ; **GE-Proton** en est une version communautaire.
> - **ProtonDB** : un site communautaire qui note la compatibilité des jeux avec Proton.
> - **Lutris** / **Heroic** : des lanceurs de jeux pour les boutiques autres que Steam (Epic, GOG, Battle.net…).
> - **Moonlight** / **Sunshine** : un client et un serveur de streaming de jeux en réseau local.
> - **agent IA en CLI** : un assistant qui travaille dans le terminal et peut lire, écrire et exécuter des commandes.
> - **LM Studio** / **Ollama** : des outils pour faire tourner des modèles d'IA en local, sur sa carte graphique.

## Comprendre : mesurer avant d'optimiser

Omarchy est déjà léger : pas de services inutiles, un shell en un seul processus, un terminal minimal. Les vrais gains viennent rarement de réglages « magiques », mais de trois sources : le **disque** (le T7 bien branché, fiche 2), le **pilote graphique**, et un **service qui traîne** au démarrage. On mesure d'abord, on corrige ensuite.

## Le démarrage

```bash
systemd-analyze                 # durée totale : micrologiciel, chargeur, noyau, système
systemd-analyze blame           # services classés par durée
systemd-analyze critical-chain  # ce qui retarde réellement l'arrivée de la session
```

Sur un PC fixe, l'étape « firmware » (l'UEFI) est souvent la plus longue : le démarrage rapide de la carte mère et la désactivation des contrôleurs inutilisés se règlent dans l'UEFI, pas dans Linux. Un service qui attend le réseau (`NetworkManager-wait-online`) peut aussi coûter plusieurs secondes.

## Le confort visuel

Dans `~/.config/hypr/looknfeel.lua`, en n'écrivant que ce que tu changes :

```lua
hl.config({
  animations = { enabled = false },   -- fenêtres instantanées
  decoration = { blur = { enabled = false } },
  general = { gaps_in = 0, gaps_out = 0, border_size = 0 },
})
```

Les noms de réglages sont ceux de Hyprland : vérifie-les dans les défauts d'Omarchy (`/usr/share/omarchy`) avant de les recopier. Sur une carte graphique récente, la différence de performances est faible ; c'est surtout une question de goût. **Super+Shift+Retour arrière** bascule marges et bordures sans toucher au fichier.

## La carte graphique

```bash
lspci -k | rg -A3 -i vga     # carte et pilote noyau en cours d'utilisation
```

| Pilote | Matériel | Remarque |
| --- | --- | --- |
| `amdgpu` | AMD Radeon | libre, intégré, excellent sous Wayland |
| `i915` / `xe` | Intel | libre, intégré |
| `nvidia` | NVIDIA | propriétaire, indispensable pour jouer |
| `nouveau` | NVIDIA | libre mais lent : à remplacer par `nvidia` |

Si tu vois `nouveau` sur une carte NVIDIA récente, c'est la première chose à corriger (la page NVIDIA du wiki Arch détaille la marche à suivre ; prends un snapshot avant). Pour un écran à haute fréquence, vérifie aussi la fréquence active avec `hyprctl monitors` (fiche 9).

## Veille et hibernation sur le T7

| Mode | Principe | Sur le T7 |
| --- | --- | --- |
| **Veille** (suspend) | la RAM reste alimentée, reprise en 1 à 2 s | dépend de l'alimentation USB en veille ; si le réveil plante, désactive l'économie d'énergie USB dans l'UEFI |
| **Hibernation** | la RAM est écrite sur le disque, PC éteint | il faut un espace de la taille de la RAM sur le T7, et redémarrer sur le T7 au réveil |
| **Extinction** | rien n'est gardé | le plus sûr, et Omarchy démarre vite |

Commandes du manuel :

```bash
omarchy hibernation setup     # crée /swap (taille de la RAM) ; Limine requis
omarchy hibernation remove    # le retire
omarchy toggle suspend        # autoriser ou interdire la veille
```

Avec 32 Go de RAM, l'hibernation réserve 32 Go sur le T7. Pour un système que tu démarres occasionnellement, l'extinction propre (**Super+Échap**) reste le meilleur choix.

## Les jeux

| Boutique | Moyen dans Omarchy |
| --- | --- |
| Steam | *Install > Gaming > Steam* (Proton intégré) |
| Battle.net | *Install > Gaming*, via GE-Proton |
| Epic, GOG, autres | Lutris, Heroic |
| Rétro | RetroArch (BIOS dans `~/Games/bios`, jeux dans `~/Games/roms`) |

**Proton** fait tourner une grande partie des jeux Windows sans effort. La limite, c'est l'**anti-cheat** : les jeux dont l'anti-cheat refuse Linux ne se lancent pas en ligne. Le manuel cite Fortnite et Rocket League ; **Valorant** est dans ce cas, car Vanguard s'exécute dans le noyau de Windows. Pour eux, la solution est de **redémarrer sur Windows** (avec Secure Boot activé, fiche 2). Le manuel propose aussi le **streaming** (Moonlight côté Omarchy, Sunshine côté Windows, ou le cloud gaming), mais il suppose un second PC sous Windows. Avant d'acheter un jeu pour Omarchy, consulte **ProtonDB**.

En jeu, passe le jeu en plein écran sur un espace dédié (**Super+F**) et libère au besoin les raccourcis qu'il utilise (`hl.unbind`, fiche 12).

## Les agents IA

Omarchy intègre des agents en ligne de commande, sans en imposer un :

| Action | Moyen |
| --- | --- |
| Choisir ton agent | `omarchy default agent <nom>` (Claude, Codex, Gemini, Copilot, OpenCode…) |
| L'ouvrir | **Super+Shift+Ctrl+A** ; ou dans la console quake (**Super+`**) |
| Modèles locaux | *Install > AI* : LM Studio, Ollama |

Le manuel insiste sur un point : ces agents sont réglés en **mode auto-approbation**, ils exécutent des commandes **sans te demander**. Les règles de prudence :

1. **commite** tes dotfiles avant de laisser un agent les modifier, et relis le `git diff` après ;
2. garde **sudo avec mot de passe** pendant qu'un agent travaille (jamais `omarchy-sudo-passwordless` en même temps) ;
3. lance-le **dans le bon dossier** et donne-lui une tâche précise ; pour un changement de configuration, demande-lui d'abord un plan avant de le laisser agir ;
4. ne lui donne **aucun secret** (jetons, mots de passe).

Bien utilisé, un agent est un excellent professeur pour Omarchy : « explique-moi ce que fait ce bloc de `looknfeel.lua` », « écris un hook `theme-set` qui recharge k9s ».

## Pour aller encore plus loin

- **Les notes de version** à chaque mise à jour majeure : elles annoncent les changements de fichiers.
- **Le manuel** (omarchy.org/manual) : chapitres sur les machines virtuelles Windows, les installations automatisées, les applis en terminal, l'historique du presse-papiers, les rappels.
- **Le wiki Arch** pour tout ce qui touche au système et au matériel.
- **La communauté** : le Discord d'Omarchy, les thèmes et plugins partagés.

> **À retenir.** Mesure avant d'optimiser : `systemd-analyze blame` pour le démarrage, `lspci -k` pour vérifier le pilote graphique, le port USB pour le T7. Sur un disque externe, préfère l'extinction à l'hibernation (qui réserve la taille de la RAM). Steam et Proton font tourner la plupart des jeux, mais pas Valorant : redémarre sur Windows. Les agents IA sont puissants et en auto-approbation : git, sudo protégé et tâche précise.
