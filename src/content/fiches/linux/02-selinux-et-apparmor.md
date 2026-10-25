---
title: SELinux et AppArmor
chapter: 2
order: 4
duration: 11
tags:
- LFCS
- CKS
- SELinux
- AppArmor
cards:
- q: Qu'ajoutent SELinux et AppArmor aux droits Unix ?
  a: 'Le **contrôle d''accès obligatoire** (MAC) : une politique du système décide ce que chaque programme peut faire, même s''il tourne en root, et le propriétaire d''un fichier ne peut pas la contourner.'
- q: Quels sont les trois modes de SELinux ?
  a: '`enforcing` (bloque et journalise), `permissive` (journalise sans bloquer, utile pour diagnostiquer), `disabled`. `getenforce` affiche le mode, `setenforce 0` passe en permissive jusqu''au redémarrage.'
- q: Comment donner durablement le bon contexte SELinux à un dossier ?
  a: '`semanage fcontext -a -t httpd_sys_content_t "/srv/web(/.*)?"` enregistre la règle, puis `restorecon -Rv /srv/web` l''applique. `chcon` seul serait perdu au prochain réétiquetage.'
- q: Comment trouver la cause d'un refus SELinux ?
  a: '`ausearch -m avc -ts recent` liste les refus (les messages AVC) ; `sealert -a /var/log/audit/audit.log` propose souvent la correction.'
- q: À quoi servent les booléens SELinux ?
  a: Ce sont des interrupteurs prévus dans la politique pour les cas fréquents. `setsebool -P httpd_can_network_connect on` permet par exemple au serveur web d'ouvrir des connexions réseau (`-P` rend le réglage permanent).
- q: Quels sont les deux modes d'un profil AppArmor et comment passer de l'un à l'autre ?
  a: '`enforce` (bloque) et `complain` (journalise seulement). `aa-complain /etc/apparmor.d/<profil>` et `aa-enforce …` ; `aa-status` liste les profils et leur mode.'
quiz:
- q: nginx renvoie 403 sur des fichiers déplacés dans `/srv/web` alors que les droits Unix sont bons. La machine est en Rocky Linux. Que fais-tu ?
  options:
  - '`setenforce 0` définitivement'
  - '`ls -Z /srv/web`, puis `semanage fcontext` et `restorecon`'
  - '`chmod 777 /srv/web`'
  - Réinstaller nginx
  answer: 1
  explain: Les fichiers ont gardé le contexte de leur ancien emplacement. On corrige le contexte au lieu de désactiver une couche de sécurité.
- q: Ton service web doit écouter sur le port 8081 et SELinux le bloque. Quelle commande ?
  options:
  - '`setsebool -P httpd_port 8081`'
  - '`semanage port -a -t http_port_t -p tcp 8081`'
  - '`restorecon -p 8081`'
  - '`firewall-cmd --add-port=8081/tcp`'
  answer: 1
  explain: SELinux étiquette aussi les ports. Le pare-feu est une autre couche, à ouvrir en plus si besoin.
level: intermédiaire
---

Les droits Unix (propriétaire, groupe, `rwx`) ont une faiblesse : root peut tout faire, et un service compromis peut faire tout ce que son compte peut faire. **SELinux** et **AppArmor** ajoutent une seconde couche, décidée par le système et non par les propriétaires des fichiers. L'examen LFCS demande de diagnostiquer un refus et de le corriger proprement ; la CKS demande d'utiliser AppArmor dans les pods.

> **Les outils cités dans cette fiche.**
> - **SELinux** (Security-Enhanced Linux) : le système de contrôle d'accès obligatoire de Red Hat, Fedora, Rocky et Alma. Il colle une **étiquette** (contexte) sur chaque fichier, processus et port.
> - **AppArmor** : l'équivalent sur Debian, Ubuntu et SUSE. Il décrit, programme par programme, les **chemins** de fichiers autorisés.
> - **semanage**, **restorecon**, **getsebool** et **setsebool** : les commandes qui gèrent les règles d'étiquetage et les options de SELinux.
> - **ausearch** et **sealert** : lisent le journal d'audit (`/var/log/audit/audit.log`) et expliquent les refus.
> - **aa-status**, **aa-complain** et **aa-enforce** : listent les profils AppArmor et changent leur mode.
> - **pod** : la plus petite unité de Kubernetes : un ou plusieurs conteneurs qui partagent réseau et volumes.
> - **conteneur** : un processus isolé qui embarque son application et ses dépendances, lancé à partir d'une image (voir le module Docker).

## Comprendre : DAC et MAC

| | Droits Unix (DAC) | SELinux / AppArmor (MAC) |
| --- | --- | --- |
| qui décide | le propriétaire du fichier | la politique du système |
| root | peut tout | limité comme les autres |
| question posée | « cet utilisateur a-t-il le droit ? » | « ce programme a-t-il le droit de faire ça ? » |

Les deux couches s'additionnent : une action doit passer **les deux**. Si un nginx compromis tente de lire `/etc/shadow`, les droits Unix peuvent le laisser faire s'il tourne en root, mais la politique MAC dit que nginx ne lit que les fichiers web.

## SELinux : tout est étiqueté

```bash
getenforce                       # Enforcing, Permissive ou Disabled
ls -Z /var/www/html              # contexte des fichiers
ps -eZ | grep nginx              # contexte des processus
# system_u:object_r:httpd_sys_content_t:s0  index.html
#                   └── le type : c'est lui qui compte au quotidien
```

La règle de base : un processus de type `httpd_t` peut lire les fichiers de type `httpd_sys_content_t`. Rien d'autre, sauf règle explicite.

### Les trois corrections courantes

```bash
# 1. Un fichier ou dossier a le mauvais contexte (souvent après un mv)
semanage fcontext -a -t httpd_sys_content_t "/srv/web(/.*)?"
restorecon -Rv /srv/web

# 2. Une option prévue par la politique : un booléen
getsebool -a | grep httpd
setsebool -P httpd_can_network_connect on

# 3. Un port non standard
semanage port -a -t http_port_t -p tcp 8081
```

`mv` garde le contexte d'origine du fichier, `cp` prend celui du dossier de destination : c'est la cause numéro un des « 403 inexpliqués ».

### Diagnostiquer

```bash
ausearch -m avc -ts recent       # les refus récents
sealert -a /var/log/audit/audit.log
setenforce 0                     # permissive le temps de vérifier, puis setenforce 1
```

Le mode permissive sert à **confirmer** que SELinux est en cause, pas à régler le problème. Le désactiver dans `/etc/selinux/config` retire une couche de défense pour toute la machine.

## AppArmor : des profils par programme

AppArmor ne colle pas d'étiquettes : il décrit, pour un programme donné, les chemins qu'il peut lire, écrire ou exécuter.

```
# /etc/apparmor.d/usr.sbin.nginx (extrait)
/usr/sbin/nginx {
  #include <abstractions/base>
  /etc/nginx/** r,
  /var/www/** r,
  /var/log/nginx/*.log w,
  network inet tcp,
}
```

```bash
aa-status                                   # profils chargés et leur mode
aa-complain /etc/apparmor.d/usr.sbin.nginx  # journalise sans bloquer
aa-enforce  /etc/apparmor.d/usr.sbin.nginx  # bloque
apparmor_parser -r /etc/apparmor.d/usr.sbin.nginx   # recharger après modification
journalctl -k | grep 'apparmor="DENIED"'    # les refus
```

## Lequel choisir ?

On ne choisit pas vraiment : on garde celui de sa distribution. SELinux est plus fin (il protège aussi les ports et les processus entre eux) mais plus difficile à lire ; AppArmor est plus simple à écrire car il raisonne en chemins. Docker et Kubernetes savent appliquer l'un ou l'autre aux conteneurs.

> **À retenir.** Un refus MAC se reconnaît à des droits Unix corrects et un « permission denied » quand même. En SELinux : `ls -Z`, `ausearch -m avc`, puis `semanage fcontext` + `restorecon`, un booléen ou `semanage port`. En AppArmor : `aa-status`, le mode `complain` pour diagnostiquer, `aa-enforce` ensuite. On corrige la règle, on ne désactive pas la couche.
