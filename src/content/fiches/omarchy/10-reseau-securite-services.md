---
title: Réseau, sécurité et services
chapter: 10
order: 1
duration: 14
level: Intermédiaire
tags:
- NetworkManager
- pare-feu
- UFW
- LUKS
- sudo
- SSH
- Tailscale
- systemd
cards:
- q: Comment Omarchy gère-t-il le réseau ?
  a: Avec **NetworkManager**. L'Ethernet marche sans réglage ; le Wi-Fi se gère dans le panneau **Super+Ctrl+N**, avec `nmtui` (interface texte) ou `omarchy network`. Le DNS vient du routeur (DHCP) par défaut ; *Setup > Network > DNS* ou `omarchy dns` le change (Cloudflare par exemple).
- q: Que bloque le pare-feu par défaut ?
  a: '**Tout le trafic entrant**, sauf le port **53317** (LocalSend, le partage de fichiers en réseau local). Le trafic sortant est libre. Docker est verrouillé avec **ufw-docker** pour que tes conteneurs ne soient pas exposés par accident.'
- q: Pourquoi deux mots de passe, et où les changer ?
  a: Un pour **déverrouiller le disque** (LUKS, au démarrage), un pour la **session et sudo**. À l'installation, ils sont identiques. *Update > Password > Drive Encryption* change le premier, *Update > Password > User* le second.
- q: Que fait `omarchy-sudo-passwordless 30`, et quel est le risque ?
  a: 'Il autorise `sudo` **sans mot de passe pendant 30 minutes** (de 1 à 1440, ou `permanent`). Une icône rouge le signale dans la barre. Risque : pendant ce temps, **n''importe quel programme** lancé sous ton compte peut tout faire en root. À réserver à une session de maintenance.'
- q: Le serveur SSH est-il actif ?
  a: Non, **désactivé par défaut**. *Setup > Security > SSHD* l'active, ouvre le port 22 et limite les tentatives de connexion (contre la force brute). Ne l'active que si tu dois te connecter à ce PC depuis un autre.
- q: À quoi servent `systemctl` et `journalctl` ?
  a: '`systemctl` pilote les **services** systemd : `status`, `start`, `stop`, `enable` (au démarrage). `journalctl` lit leurs **journaux** : `journalctl -u NetworkManager` pour un service, `-b` pour le démarrage en cours, `-p err` pour les erreurs.'
- q: Qu'apporte Tailscale, proposé dans Install > Service ?
  a: Un **réseau privé chiffré** entre tes appareils (PC, téléphone, serveur), sans ouvrir de port. Pratique pour joindre ton PC Omarchy depuis ailleurs ou envoyer des fichiers (`omarchy tailscale send`). C'est un **VPN maillé** basé sur WireGuard.
quiz:
- q: Tu lances un conteneur avec `-p 8080:80` et tu veux savoir s'il est visible depuis Internet. Qu'en dit la configuration d'Omarchy ?
  options:
  - Il est exposé, Docker contourne toujours le pare-feu
  - ufw-docker est configuré pour éviter que les conteneurs soient exposés par accident
  - Docker n'existe pas sous Omarchy
  - Il faut désactiver le pare-feu pour que ça marche
  answer: 1
  explain: Sans précaution, Docker écrit ses propres règles et passe outre UFW ; Omarchy installe ufw-docker pour corriger ce comportement.
- q: Tu dois installer une dizaine de paquets et lancer plusieurs commandes root pendant une heure. Option raisonnable ?
  options:
  - '`omarchy-sudo-passwordless permanent`'
  - '`omarchy-sudo-passwordless 60`, et l''arrêter dès que tu as fini'
  - Te connecter en root sur la session graphique
  - Désactiver LUKS
  answer: 1
  explain: Une durée limitée réduit la fenêtre de risque ; un redémarrage la termine aussi. Le mode permanent est déconseillé.
- q: Le Wi-Fi est connecté mais aucun site ne s'ouvre, alors que `ping 1.1.1.1` répond. Piste principale ?
  options:
  - La carte Wi-Fi est en panne
  - 'Le DNS : essaie `omarchy dns` pour passer sur Cloudflare'
  - Le pare-feu bloque le trafic sortant
  - Le noyau est trop ancien
  answer: 1
  explain: Si une adresse IP répond mais pas les noms de domaine, c'est la résolution DNS. Le pare-feu d'Omarchy ne bloque que l'entrant.
- q: Tu veux recevoir sur ton PC un fichier envoyé depuis ton téléphone sur le même Wi-Fi, sans câble ni cloud. Outil prévu ?
  options:
  - LocalSend, dont le port 53317 est ouvert dans le pare-feu
  - SSH
  - Un serveur FTP
  - Bluetooth uniquement
  answer: 0
  explain: LocalSend est l'exception prévue dans le pare-feu justement pour ce cas.
---

Tu es moins à l'aise en réseau et en sécurité : cette fiche part des bases et explique ce qu'Omarchy règle pour toi (connexion, pare-feu, chiffrement, droits administrateur), ce que tu peux activer, et les deux commandes qui permettent de comprendre n'importe quel service Linux. D'après le manuel Omarchy 4.

> **Les outils cités dans cette fiche.**
> - **NetworkManager** : le service qui gère les connexions réseau (Ethernet, Wi-Fi, VPN) ; `nmtui` en est l'interface texte.
> - **DHCP** : le protocole par lequel ta box donne automatiquement une adresse IP et un serveur DNS à chaque appareil.
> - **DNS** : l'annuaire d'Internet, qui traduit un nom (github.com) en adresse IP.
> - **pare-feu** : le filtre qui décide quelles connexions réseau sont acceptées ; **UFW** (Uncomplicated Firewall) en est une interface simple sous Linux.
> - **port** : un numéro qui identifie un service sur une machine (22 pour SSH, 443 pour le web chiffré).
> - **LocalSend** : une appli libre pour envoyer des fichiers entre appareils d'un même réseau local.
> - **ufw-docker** : un complément qui empêche Docker de contourner les règles du pare-feu.
> - **LUKS** : le chiffrement de disque de Linux, activé à l'installation.
> - **sudo** : la commande qui exécute une action avec les droits administrateur (root) après ton mot de passe.
> - **SSH** / **sshd** : le protocole de connexion à distance sécurisée, et le serveur qui l'accepte.
> - **systemd** : le gestionnaire de démarrage et de services ; **systemctl** le pilote, **journalctl** lit ses journaux.
> - **Tailscale** : un service de VPN maillé basé sur **WireGuard** qui relie tes appareils dans un réseau privé chiffré.
> - **VPN** : un tunnel chiffré entre des appareils, à travers un réseau non sûr comme Internet.

## Comprendre : ce qui entre, ce qui sort

<!-- schema:parefeu -->
<figure class="diagram"><svg viewBox="0 0 680 260" role="img" aria-label="Ce qui entre, ce qui sort" style="--minw:560px"><defs><marker id="g6-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g6-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g6-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g6-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="250" y="90" width="180" height="80" rx="9"/></g><text x="340.0" y="127.0" class="dg-t" text-anchor="middle" style="--d:0">ton PC Omarchy</text><text x="340.0" y="145.0" class="dg-s" text-anchor="middle" style="--d:0">pare-feu UFW</text><g class="dg-box dg-pop" style="--d:1"><rect x="14" y="20" width="180" height="50" rx="9"/></g><text x="104.0" y="50.0" class="dg-t" text-anchor="middle" style="--d:1">Internet</text><g class="dg-box dg-pop" style="--d:1"><rect x="14" y="190" width="180" height="50" rx="9"/></g><text x="104.0" y="212.0" class="dg-t" text-anchor="middle" style="--d:1">réseau local</text><text x="104.0" y="230.0" class="dg-s" text-anchor="middle" style="--d:1">téléphone, autre PC</text><g class="dg-box dg-ok dg-pop" style="--d:2"><rect x="486" y="20" width="180" height="50" rx="9"/></g><text x="576.0" y="42.0" class="dg-t" text-anchor="middle" style="--d:2">sortant</text><text x="576.0" y="60.0" class="dg-s" text-anchor="middle" style="--d:2">web, mises à jour, jeux</text><g class="dg-box dg-ghost dg-pop" style="--d:3"><rect x="486" y="190" width="180" height="50" rx="9"/></g><text x="576.0" y="212.0" class="dg-t" text-anchor="middle" style="--d:3">Tailscale</text><text x="576.0" y="230.0" class="dg-s" text-anchor="middle" style="--d:3">réseau privé, aucun port ouvert</text><path d="M194 45 L248 110" class="dg-l a" marker-end="url(#g6-a)"/><path d="M194 215 L248 150" class="dg-l ok" marker-end="url(#g6-ok)"/><text x="206" y="104" class="dg-at" text-anchor="end">entrant : bloqué</text><text x="206" y="166" class="dg-okt" text-anchor="end">53317 : LocalSend</text><path d="M432 110 L484 45" class="dg-l ok" marker-end="url(#g6-ok)"/><path d="M432 150 L484 215" class="dg-l c" marker-end="url(#g6-c)" marker-start="url(#g6-c)"/></svg><figcaption>Tout l&#x27;entrant est bloqué sauf LocalSend ; le sortant est libre ; SSH reste éteint tant que tu ne l&#x27;actives pas.</figcaption></figure>
<!-- /schema:parefeu -->

Un poste de travail **sort** beaucoup (navigateur, mises à jour, jeux) et n'a presque jamais besoin d'accepter des connexions **entrantes**. Omarchy applique donc la règle la plus sûre : **tout ce qui entre est bloqué**, sauf une exception utile (LocalSend). Tout ce qui sort est autorisé. Même si un service s'ouvre par erreur sur ta machine, personne ne peut s'y connecter de l'extérieur.

## Se connecter

| Besoin | Moyen |
| --- | --- |
| Ethernet | rien à faire |
| Wi-Fi | panneau **Super+Ctrl+N**, `nmtui`, ou `omarchy network` |
| Partager un Wi-Fi par QR code | *Setup > Network > QR Code* |
| Forcer la bande 5 GHz | `omarchy network band 5` |
| Tester le débit | `omarchy network speedtest` |
| Changer de DNS | *Setup > Network > DNS*, ou `omarchy dns` (Cloudflare…) |

Un diagnostic simple quand « Internet ne marche pas » :

1. `ping 1.1.1.1` ne répond pas : problème de **connexion** (câble, Wi-Fi, box) ;
2. `ping 1.1.1.1` répond mais `ping github.com` non : problème de **DNS** ;
3. les deux répondent mais un site ne s'ouvre pas : problème côté site ou navigateur.

## Le pare-feu

| Règle | Pourquoi |
| --- | --- |
| entrant **bloqué** | un poste n'a pas à accepter de connexions |
| port **53317** ouvert | LocalSend, pour le partage de fichiers en réseau local |
| sortant **libre** | navigation, mises à jour, jeux |
| **ufw-docker** | Docker écrit ses propres règles réseau et contourne UFW ; ce complément l'en empêche |

Si un jour tu as besoin d'ouvrir un port (un serveur de développement à montrer à un autre PC de la maison, par exemple), ouvre-le explicitement, uniquement pour le réseau local, et referme-le après. Mieux encore : passe par Tailscale, qui n'ouvre aucun port.

## Le chiffrement et les mots de passe

Le disque est chiffré avec **LUKS** : sans le mot de passe, le contenu du T7 est illisible, ce qui compte double pour un disque qu'on transporte. Il y a **deux mots de passe**, identiques après l'installation :

| Mot de passe | Sert à | Où le changer |
| --- | --- | --- |
| Chiffrement du disque | déverrouiller le T7 au démarrage | *Update > Password > Drive Encryption* |
| Utilisateur | ouvrir la session, `sudo` | *Update > Password > User* |

Si un changement de mot de passe de disque est interrompu, relance *Drive Encryption* : il demande le mot de passe qui fonctionne actuellement et termine l'opération.

## sudo et le mode sans mot de passe

`sudo` demande ton mot de passe avant chaque action administrateur : c'est un garde-fou contre les erreurs et les programmes malveillants. Omarchy permet de le suspendre temporairement :

```bash
omarchy-sudo-passwordless 30          # 30 minutes (de 1 à 1440)
omarchy-sudo-passwordless permanent   # déconseillé
```

Une **icône rouge** dans la barre rappelle que le mode est actif ; clique dessus pour l'arrêter. Il s'arrête aussi au redémarrage. Pendant ce temps, **n'importe quel programme lancé sous ton compte peut tout faire en root**, y compris un script téléchargé ou un agent IA en mode automatique (fiche 16). Utilise-le pour une session de maintenance, pas au quotidien.

## Les services : SSH et les autres

| Service | État par défaut | Activation |
| --- | --- | --- |
| Serveur SSH | **désactivé** | *Setup > Security > SSHD* (port 22, tentatives limitées) |
| Tailscale | non installé | *Install > Service* |
| Docker | installable | verrouillé par ufw-docker |

**Tailscale** mérite le détour : il crée un réseau privé chiffré entre tes appareils, sans ouvrir aucun port sur la box. Ton PC Omarchy, ton téléphone et un serveur se voient comme s'ils étaient sur le même réseau local. `omarchy tailscale send` envoie un fichier à un autre appareil du réseau.

## Comprendre n'importe quel service : systemctl et journalctl

Sous Linux, presque tout ce qui tourne en arrière-plan (réseau, son, Bluetooth, SSH) est un **service systemd**. Deux commandes suffisent pour enquêter :

```bash
systemctl status NetworkManager          # actif ? depuis quand ? dernières lignes de journal
sudo systemctl restart NetworkManager    # redémarrer le service
systemctl --failed                       # les services en échec
journalctl -u NetworkManager -b          # son journal depuis le démarrage
journalctl -b -p err                     # toutes les erreurs du démarrage en cours
journalctl -f                            # suivre les journaux en direct
```

Tu retrouves la logique de `kubectl describe` et `kubectl logs` : d'abord l'état, puis les journaux.

## Les bons réflexes

- **Mets à jour souvent** : sur une rolling release, les correctifs de sécurité arrivent vite, encore faut-il les installer.
- **N'ajoute pas l'AUR sans réfléchir** (fiche 6) : c'est la principale porte d'entrée pour du code non vérifié.
- **N'ouvre pas de port** sans raison ; préfère Tailscale.
- **Garde le chiffrement**, surtout sur un disque externe.
- Si tu vérifies une image d'installation : la clé publique d'Omarchy a pour empreinte `40DFB630FF42BCFFB047046CF0134EE680CAC571`, et la signature d'une ISO s'obtient en ajoutant `.sig` à son adresse.

> **À retenir.** Omarchy bloque tout l'entrant (sauf LocalSend), chiffre le disque avec LUKS et laisse SSH éteint : la base est sûre. NetworkManager gère le réseau (Super+Ctrl+N, `nmtui`), `ping` sur une IP puis sur un nom distingue un problème de connexion d'un problème de DNS. Le sudo sans mot de passe se limite dans le temps, et `systemctl status` plus `journalctl -u` expliquent n'importe quel service.
