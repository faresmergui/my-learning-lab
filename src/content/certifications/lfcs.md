---
title: LFCS
name: Linux Foundation Certified System Administrator
org: Linux Foundation
order: 4
color: "#f2c94c"
description: Administrer un serveur Linux en ligne de commande, en conditions réelles.
officialUrl: https://training.linuxfoundation.org/certification/linux-foundation-certified-sysadmin-lfcs/
checked: 22 octobre 2026
format:
  - { label: Type, value: "Examen pratique sur de vraies machines Linux (Ubuntu), dans un terminal distant" }
  - { label: Durée, value: "2 heures" }
  - { label: Score pour réussir, value: "67 %" }
  - { label: Documentation autorisée, value: "Les pages de manuel et la documentation installées sur la machine (man, --help), pas Internet" }
  - { label: Inclus, value: "Une seconde tentative gratuite et deux sessions de simulateur (killer.sh)" }
  - { label: Validité, value: "2 ans" }
domains:
  - name: Opérations et déploiement
    weight: 25
    fiches: [linux/04-systemd, linux/03-processus-et-signaux, linux/07-journald-et-logs, linux/09-serveur-lent, reseaux/07-reseau-des-conteneurs, linux/04-paquets-cron-et-noyau, linux/02-selinux-et-apparmor, linux/10-conteneurs-et-machines-virtuelles]
  - name: Réseau
    weight: 25
    fiches: [linux/05-diagnostiquer-le-reseau, reseaux/02-adressage-et-cidr, reseaux/02b-routage-passerelle-et-arp, reseaux/03-dns, reseaux/06-pare-feu-et-nat, reseaux/05-load-balancing-et-proxys, linux/05-configurer-reseau-heure-et-ssh, linux/05-reverse-proxy-nginx]
  - name: Stockage
    weight: 20
    fiches: [linux/06-disques-montages-lvm, linux/01-inodes-et-liens, linux/06-raid-nfs-swap-et-quotas]
  - name: Commandes essentielles
    weight: 20
    fiches: [linux/01-arborescence-fhs, linux/02-permissions, linux/08-outils-texte, linux/08-scripts-bash-robustes, devops/01-git-avance, reseaux/04b-tls-et-certificats, linux/01-chercher-archiver-et-creer-un-certificat]
  - name: Utilisateurs et groupes
    weight: 10
    fiches: [linux/02-utilisateurs-sudo-acl, linux/02-permissions, linux/02-pam-limites-et-comptes-systeme]
---

## Ce que l'examen vérifie vraiment

Comme la CKA, la LFCS est **pratique** : on te connecte à des machines Ubuntu et on te demande d'obtenir un résultat (« le service `web` doit démarrer au boot et redémarrer s'il plante », « crée un volume logique de 2 Go monté sur `/data` au démarrage »). Seul l'état final de la machine est noté. Et contrairement à la CKA, **pas de documentation web** : il faut savoir trouver dans `man` et `--help`.

## Les pièges

- **Ce qui ne survit pas au redémarrage.** Un montage fait à la main sans `/etc/fstab`, une règle de pare-feu non sauvegardée, un `sysctl` non écrit dans `/etc/sysctl.d/` : tout disparaît si la machine redémarre pour la correction. Rends chaque changement **persistant**.
- **Casser `/etc/fstab`.** Une erreur peut empêcher la machine de redémarrer. Teste toujours avec `mount -a` (fiche « Disques, montages et LVM »).
- **Oublier `daemon-reload` et `enable`.** Après avoir modifié une unité systemd : `systemctl daemon-reload`, puis `enable --now` si le service doit démarrer au boot.
- **Travailler sur la mauvaise machine.** Comme à la CKA, chaque tâche indique où se connecter.

## À connaître par cœur

```bash
man -k mot-clé            # chercher la bonne page de manuel
systemctl enable --now web ; systemctl status web ; journalctl -u web -n 50
ip -br a ; ip r ; ss -tlnp ; resolvectl status
lsblk -f ; pvcreate / vgcreate / lvcreate ; mkfs.ext4 ; blkid ; mount -a
useradd -m -s /bin/bash jane ; usermod -aG sudo jane ; passwd jane
chmod / chown / setfacl ; find / -perm -4000 -type f 2>/dev/null
tar czf archive.tgz dossier/ ; tar xzf archive.tgz -C /cible
```

## Stratégie le jour J

1. Lis chaque tâche jusqu'au bout : un détail (« au démarrage », « pour l'utilisateur `jane` seulement ») change la réponse.
2. Après chaque tâche, **vérifie** l'état final (`systemctl is-enabled`, `findmnt`, `id jane`).
3. Si tu as le temps à la fin, demande-toi pour chaque tâche : « est-ce que ça marche encore après un redémarrage ? »
