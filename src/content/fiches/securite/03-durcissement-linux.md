---
title: Durcir un serveur Linux
chapter: 3
order: 1
duration: 10
level: intermédiaire
tags:
- CIS
cards:
- q: Quels réglages SSH de base pour un serveur exposé ?
  a: '`PermitRootLogin no`, `PasswordAuthentication no` (clés uniquement), `AllowUsers` ou `AllowGroups`, et idéalement un bastion ou un VPN devant.'
- q: Pourquoi appliquer les mises à jour de sécurité automatiquement ?
  a: La plupart des compromissions exploitent des failles **déjà corrigées**. `unattended-upgrades` (Debian/Ubuntu) ou `dnf-automatic` (RHEL) réduisent cette fenêtre.
- q: À quoi servent SELinux et AppArmor ?
  a: 'Ils ajoutent un contrôle d''accès **obligatoire** : même root ne peut faire que ce que la politique du processus autorise. Une appli compromise reste confinée.'
- q: Comment voir les ports ouverts et les services inutiles ?
  a: '`ss -tulpn` pour les ports, `systemctl list-unit-files --state=enabled` pour les services. Tout ce qui n''est pas nécessaire est désactivé.'
- q: Qu'est-ce que le CIS Benchmark ?
  a: Un référentiel de **bonnes pratiques de configuration**, par système (Ubuntu, RHEL, Kubernetes…). Des outils comme Lynis ou OpenSCAP vérifient l'écart.
- q: À quoi sert auditd ?
  a: 'À **journaliser** les actions sensibles au niveau du noyau : modification de `/etc/passwd`, usage de `sudo`, exécution de certains binaires. Utile pour l''enquête après incident.'
- q: Pourquoi une clé SSH est-elle plus sûre qu'un mot de passe ?
  a: 'La clé privée ne quitte jamais ton poste : le serveur te lance un défi qu''elle signe. Rien ne se devine par force brute et le serveur ne stocke que la clé publique.'
- q: Qu'apportent SELinux et AppArmor par rapport aux droits Unix ?
  a: 'Un contrôle d''accès **obligatoire** : même en root, un processus confiné ne peut accéder qu''à ce que sa politique autorise.'
- q: Pourquoi envoyer les logs hors de la machine ?
  a: Un attaquant qui devient root peut effacer les journaux locaux. Des logs centralisés au fil de l'eau restent intacts.
- q: Pourquoi `PermitRootLogin no` améliore-t-il la traçabilité ?
  a: Chacun se connecte avec son propre compte puis utilise `sudo`, qui journalise qui a fait quoi. Avec root direct, toutes les actions sont anonymes.
quiz:
- q: Un serveur exposé sur Internet accepte SSH par mot de passe. Quelle mesure en premier ?
  options:
  - Changer le port SSH
  - Passer en authentification par clé uniquement (`PasswordAuthentication no`)
  - Installer un antivirus
  - Désactiver IPv6
  answer: 1
  explain: Changer le port réduit le bruit dans les logs, mais n'arrête pas une attaque ciblée. Les clés suppriment le risque de mot de passe deviné. fail2ban vient en complément.
- q: Ton appli doit écouter sur le port 443 sans tourner en root. Quelle solution ?
  options:
  - chmod 777 sur le binaire
  - Lui donner la capability `CAP_NET_BIND_SERVICE` (par exemple `AmbientCapabilities` dans systemd)
  - Lancer avec sudo
  - Désactiver SELinux
  answer: 1
  explain: On donne le privilège précis dont l'appli a besoin, pas tous les droits de root.
- q: Après avoir appliqué un script de durcissement, les conteneurs Docker n'ont plus accès à Internet. Cause probable ?
  options:
  - SELinux bloque Docker
  - '`net.ipv4.ip_forward` a été mis à 0'
  - SSH est désactivé
  - auditd ralentit le réseau
  answer: 1
  explain: Docker route le trafic des conteneurs via l'hôte, ce qui exige `ip_forward = 1`.
- q: nginx renvoie 403 sur un nouveau répertoire alors que les droits Unix sont corrects, sur une machine RHEL. Premier réflexe ?
  options:
  - '`setenforce 0` définitivement'
  - Regarder les refus SELinux (`ausearch -m avc`) et corriger le contexte du répertoire
  - Passer nginx en root
  - Mettre le répertoire en 777
  answer: 1
  explain: Le répertoire n'a probablement pas le bon contexte SELinux (`restorecon`, `semanage fcontext`). Désactiver SELinux retire une couche de défense.
- q: Un serveur a toutes ses mises à jour installées automatiquement depuis 3 mois mais n'a jamais redémarré. Est-il à jour ?
  options:
  - Oui, entièrement
  - 'Non : les correctifs du noyau et des bibliothèques chargées ne s''appliquent qu''après redémarrage'
  - Oui, sauf pour SSH
  - Cela dépend de SELinux
  answer: 1
  explain: Le noyau en mémoire et les processus qui utilisent l'ancienne libc restent vulnérables jusqu'au redémarrage.
---

**Durcir** un serveur, c'est réduire sa **surface d'attaque** : moins de portes ouvertes, moins de droits, et plus de traces quand quelque chose se passe. Un serveur fraîchement installé est conçu pour être pratique, pas pour être exposé. Cette fiche passe en revue les mesures, en expliquant chaque fois ce qu'elles empêchent.


> **Les termes et outils cités dans cette fiche.**
> - **SSH** : le protocole de connexion à distance chiffrée à une machine, en ligne de commande.
> - **MFA** : l'authentification à plusieurs facteurs : mot de passe plus un code ou une clé physique.
> - **CVE** : l'identifiant public d'une vulnérabilité connue (CVE-2024-3094).
> - **pare-feu** : un filtre qui autorise ou bloque le trafic réseau selon des règles.
> - **noyau** : le cœur du système d'exploitation (le kernel Linux), qui gère processus, mémoire, disques et réseau.
> - **AWS** : Amazon Web Services, le cloud public d'Amazon.
> - **RHEL** : Red Hat Enterprise Linux, la distribution Linux d'entreprise de Red Hat.
> - **SIEM** : un outil qui centralise les logs de sécurité et détecte les attaques.

## Le raisonnement

Pour chaque mesure, pose-toi trois questions :

1. **Qu'est-ce qui est joignable ?** Chaque port ouvert est une porte. Ce qui n'écoute pas ne peut pas être attaqué.
2. **Avec quels droits ?** Si un service est compromis, l'attaquant hérite de ses droits. Un service qui tourne en root lui donne la machine entière.
3. **Le verrait-on ?** Sans journaux, une intrusion peut durer des mois.

## La check-list de base

| Domaine | Mesures | Ce que ça empêche |
| --- | --- | --- |
| Accès | SSH par clé, pas de root direct, bastion ou VPN, MFA si possible | le vol de mot de passe et la force brute |
| Mises à jour | correctifs de sécurité automatiques, redémarrage planifié | l'exploitation de CVE connues |
| Services | désactiver tout ce qui n'est pas utilisé | des portes ouvertes oubliées |
| Réseau | pare-feu local en refus par défaut (nftables, ufw, firewalld) | l'exposition accidentelle d'un service |
| Droits | sudo limité, pas de compte partagé | l'escalade et l'anonymat des actions |
| Confinement | SELinux ou AppArmor en mode enforcing | qu'un service compromis lise ou écrive partout |
| Traces | auditd, logs envoyés hors de la machine | qu'un attaquant efface ses traces |
| Noyau | réglages `sysctl` | certaines attaques réseau |

## SSH : la porte principale

SSH est presque toujours la seule porte d'administration. Sur Internet, elle reçoit des milliers de tentatives par jour.

**Pourquoi les clés plutôt que les mots de passe ?** Une clé SSH est une paire asymétrique : la clé privée reste sur ton poste, la clé publique est déposée dans `~/.ssh/authorized_keys` du serveur. Le serveur te lance un défi que seule la clé privée peut signer. Rien de secret ne transite, rien ne peut être deviné par force brute, et une clé volée sur un serveur ne sert à rien (le serveur ne stocke que la publique).

```
# /etc/ssh/sshd_config.d/hardening.conf
PermitRootLogin no               # on se connecte avec son compte, puis sudo : chaque action est attribuée
PasswordAuthentication no        # clés uniquement
KbdInteractiveAuthentication no  # ferme l'autre chemin vers les mots de passe
AllowGroups ssh-users            # seuls les membres de ce groupe peuvent entrer
MaxAuthTries 3
```

```bash
sshd -t && systemctl reload sshd     # tester la syntaxe avant de recharger
```

Protège aussi ta clé privée avec une phrase de passe (ou une clé matérielle type YubiKey), et utilise `ssh-agent` pour ne pas la retaper.

Pour aller plus loin : ne pas exposer SSH du tout, et passer par un **bastion** (une seule machine exposée, très surveillée), un **VPN**, ou les accès sans port ouvert des clouds (AWS SSM Session Manager).

## Les mises à jour

La majorité des compromissions de serveurs exploitent des vulnérabilités **déjà corrigées** dont le correctif n'a pas été appliqué. Les mises à jour automatiques de sécurité (`unattended-upgrades` sur Debian/Ubuntu, `dnf-automatic` sur RHEL) ferment cette porte. Un correctif du noyau ou de la libc n'est actif qu'**après redémarrage** : `needrestart` ou le fichier `/var/run/reboot-required` le signalent.

## Les droits : sudo et le confinement

`sudo` permet d'exécuter une commande avec d'autres droits, et journalise **qui** l'a fait. On limite qui peut l'utiliser, et si possible quelles commandes.

**SELinux et AppArmor** ajoutent une couche que les droits Unix classiques n'ont pas : le **contrôle d'accès obligatoire** (MAC). Même en root, un processus confiné ne peut toucher que ce que sa politique autorise. Par exemple, nginx ne pourra lire que ses fichiers de configuration et ses répertoires web, même si un attaquant en prend le contrôle. Le réflexe à éviter : désactiver SELinux à la première erreur. Regarde plutôt ce qui est refusé (`ausearch -m avc`, `journalctl -t setroubleshoot`) et ajuste.

## Les traces

Un attaquant qui obtient root peut effacer les journaux **locaux**. D'où la règle : envoyer les logs **hors de la machine** (vers un serveur central, Loki, un SIEM), au fil de l'eau. `auditd` enregistre en plus des événements précis : modifications de `/etc/passwd`, utilisation de `sudo`, exécution de certains binaires.

## Le noyau : quelques sysctl

```
# /etc/sysctl.d/90-hardening.conf
net.ipv4.ip_forward = 0                 # ne pas router (sauf routeur, hôte Docker ou nœud k8s !)
net.ipv4.conf.all.accept_redirects = 0  # ignorer les redirections ICMP
net.ipv4.conf.all.rp_filter = 1         # rejeter les paquets à IP source usurpée
kernel.kptr_restrict = 2                # masquer les adresses du noyau
```

Attention : Docker et Kubernetes ont **besoin** de `ip_forward = 1`. Un durcissement copié-collé peut casser le réseau des conteneurs.

## Vérifier

```bash
ss -tulpn                           # qu'est-ce qui écoute, et sur quelle adresse ?
systemctl list-unit-files --state=enabled   # qu'est-ce qui démarre au boot ?
getenforce                          # SELinux
aa-status                           # AppArmor
lynis audit system                  # rapport de durcissement avec des suggestions
```

> **Piège classique.** Modifier la config SSH et fermer sa session avant d'avoir testé une nouvelle connexion. Garde toujours une session ouverte pendant que tu testes depuis un second terminal.

> **À retenir.** Moins de ports, moins de droits, plus de traces. SSH par clé sans root, correctifs automatiques, pare-feu en refus par défaut, SELinux ou AppArmor actifs, et des logs envoyés hors de la machine couvrent l'essentiel.
