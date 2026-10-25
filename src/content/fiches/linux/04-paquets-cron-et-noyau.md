---
title: Paquets, tâches planifiées et paramètres du noyau
chapter: 4
order: 2
duration: 11
tags:
- LFCS
- apt
- cron
- sysctl
cards:
- q: Différence entre `apt update` et `apt upgrade` ?
  a: '`apt update` **télécharge la liste** des paquets disponibles depuis les dépôts, sans rien installer. `apt upgrade` installe les nouvelles versions des paquets déjà présents.'
- q: Comment savoir à quel paquet appartient un fichier, et quels fichiers un paquet installe ?
  a: '`dpkg -S /chemin/du/fichier` donne le paquet ; `dpkg -L <paquet>` liste ses fichiers. Sur Red Hat : `rpm -qf` et `rpm -ql`.'
- q: Comment empêcher la mise à jour d'un paquet ?
  a: '`apt-mark hold <paquet>` (et `apt-mark unhold` pour lever). Sur Red Hat : le plugin `versionlock` de dnf.'
- q: Que signifient les cinq champs d'une ligne crontab ?
  a: Minute, heure, jour du mois, mois, jour de la semaine. `30 2 * * 1-5 /opt/backup.sh` lance le script à 2 h 30 du lundi au vendredi.
- q: Pourquoi un script marche à la main mais pas dans cron ?
  a: 'cron lance les commandes avec un **environnement minimal** : `PATH` réduit, pas de variables de ton shell, répertoire courant différent. On utilise des chemins absolus et on redirige la sortie vers un fichier pour voir l''erreur.'
- q: Comment modifier un paramètre du noyau de façon permanente ?
  a: L'écrire dans un fichier de `/etc/sysctl.d/` (par exemple `99-reseau.conf` avec `net.ipv4.ip_forward = 1`), puis `sysctl --system` pour l'appliquer sans redémarrer. `sysctl -w` seul est perdu au redémarrage.
quiz:
- q: Tu installes un paquet et apt répond qu'il est introuvable alors qu'il existe. Que fais-tu d'abord ?
  options:
  - '`apt upgrade`'
  - '`apt update`'
  - '`dpkg -i`'
  - Redémarrer
  answer: 1
  explain: La liste locale des paquets est sans doute ancienne. `apt update` la rafraîchit.
- q: Quelle ligne de `/etc/cron.d/backup` est correcte ?
  options:
  - '`0 3 * * * /opt/backup.sh`'
  - '`0 3 * * * root /opt/backup.sh`'
  - '`root 0 3 * * * /opt/backup.sh`'
  - '`@daily backup.sh root`'
  answer: 1
  explain: 'Dans `/etc/crontab` et `/etc/cron.d/`, il y a un sixième champ : l''utilisateur qui lance la commande. Dans `crontab -e`, il n''y en a pas.'
- q: Après `sysctl -w vm.swappiness=10`, la valeur revient à 60 au redémarrage. Pourquoi ?
  options:
  - Le noyau l'a refusée
  - '`sysctl -w` ne modifie que la valeur en mémoire'
  - Il fallait `apt install`
  - Il faut être root
  answer: 1
  explain: Pour la garder, on l'écrit dans `/etc/sysctl.d/` puis `sysctl --system`.
level: intermédiaire
---

Trois tâches d'administration reviennent sans cesse, et l'examen LFCS (Linux Foundation Certified System Administrator) les demande toutes : installer et mettre à jour des logiciels, lancer des tâches à heure fixe, et régler le comportement du noyau. Cette fiche prend les outils de Debian et Ubuntu comme référence et donne l'équivalent Red Hat.

> **Les outils cités dans cette fiche.**
> - **apt** : le gestionnaire de paquets de Debian et Ubuntu. Il télécharge les paquets depuis des **dépôts** et gère leurs dépendances.
> - **dpkg** : l'outil de bas niveau sous apt, qui installe un fichier `.deb` et sait quel paquet possède quel fichier.
> - **dnf** et **rpm** : les équivalents d'apt et dpkg sur Red Hat, Fedora, Rocky et Alma.
> - **cron** : le service qui lance des commandes à heure fixe ; **crontab** est le fichier (et la commande) qui décrit ces tâches.
> - **at** : lance une commande **une seule fois** à une heure donnée.
> - **sysctl** : lit et modifie les paramètres du noyau en marche (réseau, mémoire, sécurité).
> - **modprobe** et **lsmod** : chargent et listent les modules du noyau (des pilotes et fonctions chargés à la demande).
> - **swap** : un espace disque utilisé comme mémoire de secours quand la RAM est pleine.

## Comprendre : paquets et dépôts

Un **paquet** est une archive qui contient un logiciel, la liste de ses dépendances et des scripts d'installation. Un **dépôt** est un serveur qui publie des milliers de paquets signés. apt garde en local une **liste** de ce que proposent les dépôts configurés dans `/etc/apt/sources.list.d/` : cette liste vieillit, d'où `apt update` avant toute installation.

| Action | Debian / Ubuntu | Red Hat |
| --- | --- | --- |
| rafraîchir la liste | `apt update` | (automatique) `dnf check-update` |
| installer | `apt install nginx` | `dnf install nginx` |
| mettre à jour tout | `apt upgrade` | `dnf upgrade` |
| supprimer (config gardée) | `apt remove nginx` | `dnf remove nginx` |
| supprimer avec la config | `apt purge nginx` | (pas d'équivalent direct) |
| chercher | `apt search nginx` | `dnf search nginx` |
| infos et version | `apt show nginx`, `apt-cache policy nginx` | `dnf info nginx` |
| à qui est ce fichier | `dpkg -S /usr/sbin/nginx` | `rpm -qf /usr/sbin/nginx` |
| fichiers d'un paquet | `dpkg -L nginx` | `rpm -ql nginx` |
| bloquer une version | `apt-mark hold kubelet` | `dnf versionlock add kubelet` |

```bash
apt list --installed | grep nginx
apt autoremove                  # retire les dépendances devenues inutiles
```

## Les tâches planifiées avec cron

```bash
crontab -e            # éditer les tâches de l'utilisateur courant
crontab -l            # les lister
crontab -u alice -l   # celles d'un autre utilisateur (en root)
```

```
# ┌ minute (0-59)
# │ ┌ heure (0-23)
# │ │ ┌ jour du mois (1-31)
# │ │ │ ┌ mois (1-12)
# │ │ │ │ ┌ jour de la semaine (0-7, 0 et 7 = dimanche)
  30 2 * * 1-5  /opt/backup.sh >> /var/log/backup.log 2>&1
  */15 * * * *  /usr/local/bin/check.sh
  @reboot       /opt/start-tunnel.sh
```

Il y a deux familles de fichiers :

- `crontab -e` : cinq champs puis la commande, lancée sous ton compte ;
- `/etc/crontab` et `/etc/cron.d/*` : **un sixième champ** avec l'utilisateur, avant la commande.

Les dossiers `/etc/cron.daily/`, `cron.weekly/`… lancent simplement tous les scripts qu'ils contiennent à la fréquence indiquée.

Pour **une seule exécution**, `at` suffit :

```bash
echo "/opt/migration.sh" | at 23:00
atq        # tâches en attente
atrm 3     # en supprimer une
```

Sur une distribution récente, les **timers systemd** (fiche précédente) remplacent souvent cron : ils ont des logs dans journald et rattrapent une exécution manquée si la machine était éteinte. L'examen accepte les deux.

## Les paramètres du noyau avec sysctl

Le noyau expose des centaines de réglages sous `/proc/sys/`. `sysctl` les lit et les modifie avec des noms à points.

```bash
sysctl net.ipv4.ip_forward               # lire
sysctl -w net.ipv4.ip_forward=1          # modifier en mémoire (perdu au redémarrage)

# Rendre permanent
echo "net.ipv4.ip_forward = 1" > /etc/sysctl.d/99-routage.conf
sysctl --system                          # recharger tous les fichiers
```

| Paramètre | Effet |
| --- | --- |
| `net.ipv4.ip_forward` | laisser la machine router des paquets (nécessaire pour Docker et Kubernetes) |
| `vm.swappiness` | tendance à utiliser le swap (0 à 100, 60 par défaut) |
| `fs.file-max` | nombre maximal de fichiers ouverts sur tout le système |
| `kernel.pid_max` | nombre maximal de processus |

Certains réglages dépendent d'un **module** du noyau : `lsmod` liste ceux qui sont chargés, `modprobe br_netfilter` en charge un, et un fichier dans `/etc/modules-load.d/` le charge à chaque démarrage.

> **À retenir.** `apt update` rafraîchit la liste, `apt upgrade` installe ; `dpkg -S` trouve le paquet d'un fichier. Dans cron, `/etc/cron.d/` a un champ utilisateur en plus, et l'environnement est minimal. Un réglage du noyau se rend permanent dans `/etc/sysctl.d/` puis `sysctl --system`.
