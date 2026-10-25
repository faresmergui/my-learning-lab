---
title: Un reverse proxy avec nginx
chapter: 5
order: 3
duration: 10
tags:
- LFCS
- nginx
- reverse proxy
cards:
- q: Qu'est-ce qu'un reverse proxy ?
  a: 'Un serveur placé **devant** une ou plusieurs applications : il reçoit les requêtes des clients et les transmet à la bonne appli. Il peut aussi gérer TLS, répartir la charge et mettre en cache.'
- q: Quelle directive nginx transmet une requête à une appli ?
  a: '`proxy_pass`, dans un bloc `location`. Exemple : `location / { proxy_pass http://127.0.0.1:3000; }`.'
- q: Pourquoi ajouter `proxy_set_header X-Forwarded-For` ?
  a: Sinon l'appli voit toutes les requêtes venir de l'IP du proxy. Les en-têtes `X-Real-IP`, `X-Forwarded-For` et `X-Forwarded-Proto` lui transmettent l'IP du client et le protocole d'origine.
- q: Comment répartir la charge entre deux instances d'une appli ?
  a: Un bloc `upstream api { server 10.0.0.11:8080; server 10.0.0.12:8080; }` puis `proxy_pass http://api;`. Par défaut, nginx alterne (round robin).
- q: Que vérifier avant de recharger nginx ?
  a: '`nginx -t` teste la configuration. Ensuite `systemctl reload nginx` applique sans couper les connexions en cours.'
- q: Que signifie une erreur 502 renvoyée par nginx ?
  a: '**Bad Gateway** : nginx n''a pas pu joindre l''appli derrière lui (arrêtée, mauvais port, refus SELinux). Une 504 veut dire qu''elle n''a pas répondu à temps.'
quiz:
- q: Le site renvoie 502 juste après ta configuration. L'appli tourne bien sur le port 3000. La machine est en Rocky Linux. Que regardes-tu ?
  options:
  - Le DNS
  - '`getsebool httpd_can_network_connect` et le journal d''erreurs de nginx'
  - Les cookies du navigateur
  - Le certificat TLS
  answer: 1
  explain: Par défaut, SELinux interdit à nginx d'ouvrir des connexions réseau vers un port quelconque. `setsebool -P httpd_can_network_connect on` règle ce cas.
- q: Sur Debian, tu as écrit `/etc/nginx/sites-available/shop` mais nginx l'ignore. Pourquoi ?
  options:
  - Il faut un lien dans `sites-enabled`
  - Le fichier doit finir par `.yaml`
  - Il faut redémarrer la machine
  - nginx ne lit que `nginx.conf`
  answer: 0
  explain: '`ln -s /etc/nginx/sites-available/shop /etc/nginx/sites-enabled/`, puis `nginx -t` et `systemctl reload nginx`.'
level: intermédiaire
---

La fiche Réseaux sur le load balancing explique **pourquoi** on met un proxy devant ses applications. L'examen LFCS demande de savoir en monter un simple avec **nginx** : recevoir le trafic sur le port 80 ou 443 et le transmettre à une appli qui écoute sur un autre port.

> **Les outils cités dans cette fiche.**
> - **nginx** : un serveur web très répandu, souvent utilisé comme reverse proxy et répartiteur de charge.
> - **reverse proxy** : un serveur qui reçoit les requêtes des clients à la place des applications et les leur transmet.
> - **upstream** : dans nginx, un groupe de serveurs vers lesquels on envoie les requêtes.
> - **en-têtes X-Forwarded-*** : des en-têtes HTTP que le proxy ajoute pour dire à l'appli qui était le vrai client et en quel protocole il est arrivé.
> - **TLS** : le protocole qui chiffre une connexion et prouve l'identité du serveur par un certificat.
> - **certificat** : un fichier signé par une autorité qui lie une clé publique à un nom (un site, un service).

## Comprendre : ce que fait le proxy

```
client ──HTTPS:443──► nginx ──HTTP:3000──► appli (127.0.0.1)
                      │
                      ├─ termine TLS (certificat)
                      ├─ choisit l'appli selon le nom ou le chemin
                      └─ ajoute X-Forwarded-For
```

L'appli n'est plus exposée directement : elle n'écoute que sur `127.0.0.1` ou un réseau privé, et c'est nginx qui fait face à Internet.

## Où sont les fichiers

| Distribution | Sites | Activation |
| --- | --- | --- |
| Debian / Ubuntu | `/etc/nginx/sites-available/` | lien dans `sites-enabled/` |
| Red Hat | `/etc/nginx/conf.d/*.conf` | tout fichier `.conf` est lu |

Les logs sont dans `/var/log/nginx/access.log` et `error.log`.

## Une configuration minimale

```nginx
# /etc/nginx/sites-available/shop
server {
    listen 80;
    server_name shop.local;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        root /srv/shop;           # fichiers servis directement par nginx
    }
}
```

```bash
ln -s /etc/nginx/sites-available/shop /etc/nginx/sites-enabled/
nginx -t                     # tester
systemctl reload nginx       # appliquer sans couper les connexions
curl -H "Host: shop.local" http://127.0.0.1/
```

## Répartir la charge

```nginx
upstream api {
    server 10.0.0.11:8080;
    server 10.0.0.12:8080;
    # least_conn;  pour choisir le serveur le moins chargé
}

server {
    listen 80;
    server_name api.shop.local;
    location / { proxy_pass http://api; }
}
```

Si un serveur ne répond plus, nginx l'écarte temporairement et envoie les requêtes à l'autre.

## Ajouter TLS

```nginx
server {
    listen 443 ssl;
    server_name shop.local;
    ssl_certificate     /etc/ssl/shop/fullchain.pem;
    ssl_certificate_key /etc/ssl/shop/privkey.pem;
    location / { proxy_pass http://127.0.0.1:3000; }
}
server {
    listen 80;
    server_name shop.local;
    return 301 https://$host$request_uri;    # tout le HTTP vers HTTPS
}
```

Pour un test, la fiche « Chercher, archiver et créer un certificat » montre comment fabriquer un certificat autosigné avec openssl.

## Diagnostiquer

| Code | Signification | Piste |
| --- | --- | --- |
| 502 | nginx n'a pas joint l'appli | l'appli tourne-t-elle ? bon port ? SELinux (`httpd_can_network_connect`) ? |
| 504 | l'appli n'a pas répondu à temps | appli lente, `proxy_read_timeout` |
| 404 | aucun `location` ne correspond, ou fichier absent | `root` et chemins |
| ignoré | le mauvais bloc `server` répond | `server_name`, site activé ? |

`tail -f /var/log/nginx/error.log` donne presque toujours la réponse.

> **À retenir.** Un reverse proxy nginx, c'est un bloc `server` avec `proxy_pass` et les en-têtes `X-Forwarded-*`. `upstream` répartit la charge, `listen 443 ssl` termine TLS. Toujours `nginx -t` puis `systemctl reload nginx`, et une 502 se cherche dans `error.log`.
