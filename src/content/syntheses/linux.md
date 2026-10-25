---
title: Synthèse Linux
description: "Fichiers, droits, processus, systemd, disques, réseau et logs : les commandes et les réflexes essentiels."
---

## L'arborescence

| Dossier | Contenu |
| --- | --- |
| `/etc` | Configuration |
| `/var` | Données variables : logs (`/var/log`), caches, bases |
| `/usr` | Programmes et bibliothèques installés |
| `/opt` | Logiciels tiers |
| `/home`, `/root` | Dossiers des utilisateurs |
| `/tmp` | Temporaire, souvent vidé au démarrage |
| `/proc`, `/sys` | Vues du noyau (processus, matériel) |
| `/dev` | Périphériques |

## Les droits

```
-rwxr-x---  1 api  api  /opt/api/bin/api
 │  │  └── autres : aucun droit
 │  └───── groupe : lecture, exécution
 └──────── propriétaire : lecture, écriture, exécution
```

| Droit | Fichier | Dossier |
| --- | --- | --- |
| r (4) | lire | lister |
| w (2) | modifier | créer, supprimer dedans |
| x (1) | exécuter | traverser |

```bash
chmod 750 script.sh         # rwx r-x ---
chmod u+x,go-w fichier
chown -R api:api /var/lib/api
umask                       # droits retirés par défaut à la création
getfacl / setfacl -m u:fares:rx /data   # ACL
```

Bits spéciaux : **setuid** (s'exécute avec les droits du propriétaire), **setgid** sur dossier (héritage du groupe), **sticky bit** sur `/tmp` (seul le propriétaire supprime).

## Processus et signaux

```bash
ps aux --sort=-%mem | head
pgrep -a nginx
top / htop                  # charge, CPU, mémoire
kill -15 PID                # SIGTERM : arrêt propre
kill -9 PID                 # SIGKILL : arrêt forcé, en dernier recours
nohup cmd &   /   jobs, fg, bg
lsof -p PID                 # fichiers ouverts par un processus
ss -tlpn                    # ports en écoute et processus associés
```

**Load average** : nombre moyen de processus qui tournent ou attendent. À comparer au nombre de cœurs (`nproc`).

## systemd

```bash
systemctl status api
systemctl enable --now api      # au démarrage + maintenant
systemctl restart / reload api
systemctl daemon-reload         # après modification d'une unité
systemctl edit api              # surcharge sans copier l'unité
systemctl list-units --failed
systemctl list-timers
journalctl -u api -b -f         # logs du service depuis le démarrage, en continu
journalctl -p err --since "1 hour ago"
systemd-analyze blame
```

## Disques et systèmes de fichiers

```bash
lsblk -f                # disques, partitions, FS, montages
df -hT  /  df -i        # espace / inodes
du -xh /var --max-depth=1 | sort -h
findmnt
mount -a                # tester /etc/fstab avant de redémarrer
lsof +L1                # fichiers supprimés encore ouverts
pvs; vgs; lvs           # LVM
lvextend -r -L +20G /dev/vg/lv
```

Agrandir un disque : volume → partition (`growpart`) → PV (`pvresize`) → LV → système de fichiers (`-r`).

## Réseau

```bash
ip -br a                 # adresses
ip r                     # routes
ss -tunap                # connexions
ping / mtr host          # joignabilité, chemin
dig +short api.exemple.com    /   resolvectl status
curl -v https://host     # TLS, en-têtes, codes HTTP
nc -zv host 5432         # port ouvert ?
tcpdump -i any port 443 -nn
```

## Le texte et les logs

```bash
grep -rn "erreur" /var/log/app/
grep -E "5[0-9]{2} " access.log | wc -l
awk '{print $9}' access.log | sort | uniq -c | sort -rn | head
sed -i 's/ancien/nouveau/g' fichier
tail -f /var/log/syslog
cut -d: -f1 /etc/passwd
jq '.items[].metadata.name' fichier.json
find / -xdev -size +500M -type f 2>/dev/null
xargs, tee, sort -u, wc -l
```

## Chercher et archiver

```bash
find /var -type f -size +100M -mtime -7      # -print d'abord, -exec … {} + ensuite
find /usr -perm -4000 -type f                # binaires SUID
tar czf site.tar.gz /srv/site                # c créer, x extraire, t lister ; z gzip, J xz
tar tzf site.tar.gz  /  tar xzf site.tar.gz -C /tmp/restau
openssl req -x509 -newkey rsa:4096 -nodes -days 365 -keyout cle.pem -out cert.pem -subj "/CN=shop.local"
openssl req -new -newkey rsa:2048 -nodes -keyout api.key -out api.csr -subj "/CN=api.shop.fr"
```

## Paquets, cron et noyau

| Besoin | Debian / Ubuntu | Red Hat |
| --- | --- | --- |
| rafraîchir puis installer | `apt update && apt install nginx` | `dnf install nginx` |
| à qui est ce fichier | `dpkg -S /usr/sbin/nginx` | `rpm -qf /usr/sbin/nginx` |
| bloquer une version | `apt-mark hold kubelet` | `dnf versionlock add kubelet` |

- crontab : `min heure jour mois jour-semaine commande` ; dans `/etc/cron.d/`, un champ **utilisateur** en plus. Environnement minimal : chemins absolus.
- `at 23:00` pour une seule exécution.
- `sysctl -w` est perdu au redémarrage : écrire dans `/etc/sysctl.d/*.conf` puis `sysctl --system`.

## Configurer le réseau, l'heure et SSH

```bash
netplan try                                   # Ubuntu, /etc/netplan/*.yaml ; revient seul sans confirmation
nmcli con mod eth0 ipv4.method manual ipv4.addresses 10.0.0.5/24 ipv4.gateway 10.0.0.1   # Red Hat
hostnamectl set-hostname web-01
timedatectl set-ntp true && chronyc tracking
ssh-keygen -t ed25519 && ssh-copy-id alice@serveur
sshd -t && systemctl reload ssh               # garder une session ouverte pendant le test
nginx -t && systemctl reload nginx            # proxy_pass + en-têtes X-Forwarded-* ; 502 = appli injoignable
```

## RAID, NFS, swap et quotas

- RAID 1 et 5 survivent à un disque, RAID 0 à aucun ; `cat /proc/mdstat` (`[U_]` = un disque manque). Un RAID n'est pas une sauvegarde.
- NFS : `/etc/exports` puis `exportfs -ra` ; `root_squash` par défaut ; côté client `_netdev,nofail` dans fstab.
- Swap : `fallocate`, `chmod 600`, `mkswap`, `swapon`, ligne dans fstab.
- Quotas : option `usrquota`, `quotacheck -cum`, `quotaon`, `setquota -u alice 5G 6G 0 0 /home`.

## Utilisateurs et sudo

```bash
id fares
useradd -m -s /bin/bash -G sudo fares
passwd fares
usermod -aG docker fares         # -a : ajouter sans retirer les autres groupes
visudo                           # éditer sudoers en toute sécurité
sudo -l                          # ce que j'ai le droit de faire
```

## PAM, limites et comptes système

- PAM : un fichier par programme dans `/etc/pam.d/`, types `auth`, `account`, `password`, `session`. Garder une session root ouverte avant d'y toucher.
- Limites : `/etc/security/limits.d/` (`alice soft nofile 4096`), `ulimit -a`. Pour un service systemd : `LimitNOFILE=` dans l'unité.
- Compte de service : `useradd --system --no-create-home --shell /usr/sbin/nologin appli`.

## SELinux et AppArmor

| | SELinux (Red Hat) | AppArmor (Debian, Ubuntu) |
| --- | --- | --- |
| état | `getenforce`, `setenforce 0` (temporaire) | `aa-status` |
| voir | `ls -Z`, `ps -eZ` | profils dans `/etc/apparmor.d/` |
| refus | `ausearch -m avc -ts recent` | `journalctl -k \| grep DENIED` |
| corriger | `semanage fcontext` + `restorecon`, `setsebool -P`, `semanage port` | `aa-complain` pour diagnostiquer, puis `aa-enforce` |

## Conteneurs et machines virtuelles

```bash
podman run -d --name web -p 8080:80 -v /srv/site:/usr/share/nginx/html:ro nginx:1.27
podman ps -a; podman logs -f web; podman exec -it web sh
virsh list --all; virsh start vm; virsh shutdown vm   # destroy = coupure, undefine = suppression
```

## Serveur lent : la méthode USE

Pour chaque ressource, vérifier **Utilisation, Saturation, Erreurs** :

| Ressource | Commandes |
| --- | --- |
| CPU | `uptime`, `top`, `mpstat -P ALL 1` |
| Mémoire | `free -h`, `vmstat 1` (si/so = swap) |
| Disque | `iostat -xz 1` (%util, await), `df -h` |
| Réseau | `ss -s`, `sar -n DEV 1`, erreurs dans `ip -s link` |

## Bash robuste

```bash
#!/usr/bin/env bash
set -euo pipefail          # stoppe sur erreur, variable non définie, erreur dans un pipe
trap 'echo "échec ligne $LINENO"' ERR
readonly DIR="$(cd "$(dirname "$0")" && pwd)"
[[ -f "$1" ]] || { echo "usage: $0 fichier" >&2; exit 1; }
```

Toujours mettre les variables entre guillemets : `"$var"`. Tester avec `shellcheck`.
