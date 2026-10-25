---
title: Configurer le réseau, l'heure et SSH
chapter: 5
order: 2
duration: 11
tags:
- LFCS
- netplan
- chrony
- SSH
cards:
- q: Où configure-t-on une adresse IP fixe sur Ubuntu ?
  a: Dans un fichier YAML de `/etc/netplan/` (adresses, routes, DNS), puis `netplan try` (annule tout seul au bout de 120 s si tu ne confirmes pas) ou `netplan apply`.
- q: Quel est l'équivalent sur Red Hat ?
  a: '**NetworkManager** avec `nmcli` : `nmcli con mod eth0 ipv4.addresses 10.0.0.5/24 ipv4.gateway 10.0.0.1 ipv4.dns 1.1.1.1 ipv4.method manual`, puis `nmcli con up eth0`.'
- q: Pourquoi l'heure doit-elle être synchronisée sur un serveur ?
  a: Les certificats TLS, les jetons (Kerberos, JWT), les logs corrélés entre machines et etcd dépendent de l'heure. Un décalage de quelques minutes suffit à casser des connexions.
- q: Comment vérifier que chrony est bien synchronisé ?
  a: '`chronyc tracking` (décalage actuel) et `chronyc sources -v` (serveurs utilisés, `^*` = celui retenu). `timedatectl` affiche aussi `System clock synchronized: yes`.'
- q: Comment se connecter à un serveur par clé SSH ?
  a: '`ssh-keygen -t ed25519` crée la paire de clés, `ssh-copy-id alice@serveur` copie la clé publique dans `~/.ssh/authorized_keys` sur le serveur. La clé privée ne quitte jamais ton poste.'
- q: Que vérifier avant de recharger sshd après une modification ?
  a: '`sshd -t` (syntaxe), et garder une session ouverte pendant que tu testes la nouvelle configuration dans un **autre** terminal.'
quiz:
- q: Tu changes l'IP d'un serveur distant avec netplan. Quelle commande limite le risque de perdre l'accès ?
  options:
  - '`netplan apply`'
  - '`netplan try`'
  - '`reboot`'
  - '`ip addr flush`'
  answer: 1
  explain: '`netplan try` applique la configuration et revient à l''ancienne si tu ne confirmes pas dans le délai : si tu perds la connexion, elle revient toute seule.'
- q: SSH affiche « REMOTE HOST IDENTIFICATION HAS CHANGED ». Que fais-tu ?
  options:
  - Supprimer `~/.ssh/known_hosts` entier
  - Vérifier pourquoi la clé du serveur a changé (réinstallation ?) avant `ssh-keygen -R serveur`
  - Ajouter `StrictHostKeyChecking no`
  - Changer de clé privée
  answer: 1
  explain: Ce message protège contre l'usurpation d'un serveur. S'il y a une raison connue (serveur réinstallé), on retire seulement l'ancienne entrée.
level: intermédiaire
---

La fiche précédente apprenait à **diagnostiquer** le réseau. Celle-ci apprend à le **configurer**, avec deux voisins que l'examen LFCS associe : la synchronisation de l'heure et SSH, la porte d'entrée de tout serveur.

> **Les outils cités dans cette fiche.**
> - **netplan** : l'outil d'Ubuntu qui lit une configuration réseau en YAML et la transmet au programme qui gère vraiment le réseau (systemd-networkd ou NetworkManager).
> - **NetworkManager** et **nmcli** : le gestionnaire réseau de Red Hat (et des postes de travail) et sa commande.
> - **hostnamectl** : affiche et change le nom de la machine.
> - **NTP** (Network Time Protocol) : le protocole qui synchronise les horloges sur des serveurs de temps.
> - **chrony** : le client NTP standard des distributions récentes ; **chronyc** est sa commande. **systemd-timesyncd** est une version plus simple.
> - **timedatectl** : affiche et règle l'heure, le fuseau horaire et la synchronisation.
> - **SSH** : le protocole de connexion à distance chiffrée ; **sshd** est le serveur, **ssh** le client.
> - **certificat** : un fichier signé par une autorité qui lie une clé publique à un nom (un site, un service).
> - **TLS** : le protocole qui chiffre une connexion et prouve l'identité du serveur par un certificat.
> - **jeton** : une chaîne secrète qui prouve qu'on est authentifié, à durée limitée.

## Configurer une interface

### Ubuntu : netplan

```yaml
# /etc/netplan/50-static.yaml
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: false
      addresses: [10.0.0.5/24]
      routes:
        - to: default
          via: 10.0.0.1
      nameservers:
        addresses: [1.1.1.1, 9.9.9.9]
        search: [shop.local]
```

```bash
chmod 600 /etc/netplan/50-static.yaml   # netplan se plaint si le fichier est lisible par tous
netplan try                              # applique, et revient en arrière sans confirmation
netplan apply
ip -br addr && ip route
```

### Red Hat : nmcli

```bash
nmcli con show
nmcli con mod eth0 ipv4.method manual ipv4.addresses 10.0.0.5/24 \
  ipv4.gateway 10.0.0.1 ipv4.dns "1.1.1.1 9.9.9.9"
nmcli con up eth0
```

Dans les deux cas, une commande `ip addr add` faite à la main fonctionne tout de suite mais **disparaît au redémarrage** : elle sert à tester, pas à configurer.

### Le nom de la machine

```bash
hostnamectl set-hostname web-01
# et dans /etc/hosts, pour que la machine résolve son propre nom :
# 127.0.1.1   web-01
```

## Synchroniser l'heure

L'heure d'un serveur dérive de quelques secondes par jour. Or beaucoup de choses en dépendent : un certificat TLS « pas encore valide », un jeton refusé, des logs impossibles à recouper entre machines.

```bash
timedatectl                                  # heure, fuseau, synchronisation
timedatectl set-timezone Europe/Paris
timedatectl set-ntp true                     # active le client NTP

chronyc sources -v                           # serveurs de temps utilisés
chronyc tracking                             # décalage actuel
```

```
# /etc/chrony/chrony.conf (ou /etc/chrony.conf)
pool 2.fr.pool.ntp.org iburst
makestep 1.0 3        # corrige d'un coup un gros écart au démarrage
```

Sur les serveurs, on garde en général le fuseau **UTC** : les logs de toutes les machines se comparent sans conversion.

## SSH côté client

```bash
ssh-keygen -t ed25519 -C "fares@mac"        # crée ~/.ssh/id_ed25519 et .pub
ssh-copy-id alice@10.0.0.5                  # ajoute la clé publique sur le serveur
```

```
# ~/.ssh/config : des raccourcis
Host web
  HostName 10.0.0.5
  User alice
  IdentityFile ~/.ssh/id_ed25519
Host app-*
  ProxyJump bastion          # passer par un bastion
```

Avec ce fichier, `ssh web` suffit. Le fichier `~/.ssh/known_hosts` garde l'empreinte de chaque serveur : si elle change, SSH refuse et prévient, car quelqu'un pourrait se faire passer pour le serveur.

Côté serveur, les droits comptent : `~/.ssh` en `700` et `authorized_keys` en `600`, sinon sshd ignore la clé.

## SSH côté serveur

Les réglages de durcissement (pas de root, clés uniquement, liste d'utilisateurs autorisés) sont détaillés dans la fiche Sécurité sur le durcissement Linux. Le geste à retenir ici est la méthode :

```bash
vim /etc/ssh/sshd_config.d/10-local.conf    # modifier dans un fichier à part
sshd -t                                      # tester la syntaxe
systemctl reload ssh                         # (sshd sur Red Hat)
# garder la session actuelle ouverte, tester dans un autre terminal
```

> **À retenir.** Une IP se configure dans netplan (Ubuntu) ou nmcli (Red Hat), jamais seulement avec `ip addr add`. `netplan try` évite de se couper l'accès. L'heure se synchronise avec chrony (`timedatectl set-ntp true`, `chronyc tracking`). Pour SSH : clé ed25519, `ssh-copy-id`, `~/.ssh/config`, et `sshd -t` avant tout rechargement.
