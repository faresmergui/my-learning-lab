---
title: Chercher, archiver et créer un certificat
chapter: 1
order: 3
duration: 10
tags:
- LFCS
- find
- tar
- openssl
cards:
- q: Comment trouver les fichiers de plus de 100 Mo modifiés il y a moins de 7 jours sous `/var` ?
  a: '`find /var -type f -size +100M -mtime -7`. `-mtime -7` = moins de 7 jours, `+7` = plus de 7 jours.'
- q: Comment agir sur chaque fichier trouvé par find ?
  a: '`-exec commande {} \;` (une fois par fichier) ou `-exec commande {} +` (en regroupant, plus rapide). Exemple : `find /tmp -name ''*.log'' -mtime +30 -exec rm {} +`.'
- q: Quelles sont les options de tar pour créer, lister et extraire une archive compressée en gzip ?
  a: 'Créer : `tar czf archive.tar.gz dossier/`. Lister : `tar tzf archive.tar.gz`. Extraire : `tar xzf archive.tar.gz -C /destination`. `j` pour bzip2, `J` pour xz, `--zstd` pour zstd.'
- q: Différence entre gzip et tar ?
  a: '**tar** rassemble plusieurs fichiers en un seul (sans compresser) ; **gzip** compresse un seul fichier. `tar czf` fait les deux d''un coup.'
- q: Comment créer en une commande une clé et un certificat autosigné valable un an ?
  a: '`openssl req -x509 -newkey rsa:4096 -nodes -keyout cle.pem -out cert.pem -days 365 -subj "/CN=shop.local"` (ajouter `-addext "subjectAltName=DNS:shop.local"` pour les navigateurs).'
- q: Comment préparer une demande de certificat pour une autorité ?
  a: '`openssl req -new -newkey rsa:2048 -nodes -keyout cle.pem -out demande.csr -subj "/CN=api.shop.fr"`. On envoie le `.csr` (jamais la clé) à l''autorité, qui renvoie le certificat signé.'
quiz:
- q: Quelle commande trouve les fichiers avec le bit SUID sous `/usr` ?
  options:
  - '`find /usr -perm -4000 -type f`'
  - '`find /usr -suid`'
  - '`ls -R /usr | grep s`'
  - '`locate suid`'
  answer: 0
  explain: '`-perm -4000` = « au moins ce bit ». C''est un contrôle classique d''audit : un binaire SUID inattendu est suspect.'
- q: Tu veux extraire seulement `etc/nginx/nginx.conf` d'une archive `sauvegarde.tar.gz`. Commande ?
  options:
  - '`tar xzf sauvegarde.tar.gz etc/nginx/nginx.conf`'
  - '`gunzip nginx.conf`'
  - '`tar czf …`'
  - Impossible sans tout extraire
  answer: 0
  explain: On donne le chemin tel qu'il apparaît dans `tar tzf`. Sans `-C`, il est extrait dans le dossier courant.
- q: Comment vérifier qu'un certificat et une clé vont ensemble ?
  options:
  - Comparer leurs dates
  - Comparer `openssl x509 -noout -pubkey -in cert.pem` et `openssl pkey -pubout -in cle.pem`
  - Les ouvrir dans un éditeur
  - Regarder la taille des fichiers
  answer: 1
  explain: Les deux doivent afficher la même clé publique. Sinon nginx refuse de démarrer avec « key values mismatch ».
level: intermédiaire
---

Trois gestes du quotidien que l'examen LFCS demande à coup sûr : retrouver des fichiers selon leurs propriétés, archiver et compresser un dossier, et fabriquer un certificat TLS pour un test ou pour une autorité de certification.

> **Les outils cités dans cette fiche.**
> - **find** : parcourt une arborescence et sélectionne les fichiers selon leur nom, type, taille, date, droits ou propriétaire, puis peut agir dessus.
> - **locate** : cherche un nom dans une base d'index mise à jour régulièrement (`updatedb`) ; très rapide mais pas à jour à la seconde.
> - **tar** : rassemble des fichiers et dossiers en une seule archive, en gardant droits et arborescence.
> - **gzip**, **bzip2**, **xz** et **zstd** : des outils de compression ; xz compresse plus, zstd est le plus rapide à niveau équivalent.
> - **openssl** : la boîte à outils en ligne de commande pour créer des clés, des demandes de certificat (CSR) et des certificats, et les inspecter.
> - **CSR** (Certificate Signing Request) : une demande de certificat qui contient ta clé publique et ton nom de domaine, à faire signer par une autorité.
> - **TLS** : le protocole qui chiffre une connexion et prouve l'identité du serveur par un certificat.
> - **PKI** : l'infrastructure de gestion des certificats : autorités qui les signent, émission, révocation.

## Chercher avec find

La forme générale : `find <où> <critères> <action>`.

```bash
find /etc -name "*.conf"                     # par nom (-iname : sans la casse)
find /var/log -type f -size +100M            # fichiers de plus de 100 Mo
find /home -mtime -2                         # modifiés il y a moins de 2 jours
find /srv -user www-data -perm -o+w          # appartenant à www-data et écrivables par tous
find /usr -perm -4000 -type f                # binaires SUID (audit)
find / -xdev -type f -nouser                 # fichiers sans propriétaire connu
```

| Critère | Signification |
| --- | --- |
| `-type f` / `d` / `l` | fichier, dossier, lien |
| `-size +10M` / `-1k` | plus de 10 Mo / moins de 1 Ko |
| `-mtime -7` / `+30` | modifié il y a moins de 7 / plus de 30 jours |
| `-perm 644` / `-perm -u+x` | droits exacts / au moins ce droit |
| `-maxdepth 2` | ne pas descendre plus loin |
| `-xdev` | rester sur le même système de fichiers |

Pour agir :

```bash
find /tmp -name "*.log" -mtime +30 -print            # toujours regarder d'abord
find /tmp -name "*.log" -mtime +30 -exec rm {} +     # puis agir
find . -name "*.sh" -exec chmod +x {} \;
```

Lance toujours la commande avec `-print` avant d'ajouter `-delete` ou `-exec rm` : une faute dans les critères peut supprimer bien plus que prévu.

## Archiver et compresser avec tar

**tar** met plusieurs fichiers dans une seule archive ; la compression est une option.

```bash
tar czf site.tar.gz /srv/site                 # c = créer, z = gzip, f = fichier
tar tzf site.tar.gz | head                    # t = lister le contenu
tar xzf site.tar.gz -C /tmp/restauration      # x = extraire, -C = où
tar cJf logs.tar.xz --exclude='*.tmp' /var/log/api   # J = xz, avec exclusion
tar --zstd -cf base.tar.zst /var/backups/db
```

Un moyen mnémotechnique : **c**réer, e**x**traire, lis**t**er, puis la lettre de compression (`z` gzip, `j` bzip2, `J` xz), et toujours `f` suivi du nom du fichier.

Sans tar, pour un seul fichier :

```bash
gzip gros.log          # remplace par gros.log.gz
gunzip gros.log.gz     # (ou gzip -d)
zcat gros.log.gz | grep ERROR    # lire sans décompresser sur disque
```

tar garde les chemins **relatifs** tels qu'ils ont été donnés : si tu archives `/srv/site`, l'archive contient `srv/site/…` (le `/` initial est retiré). Vérifie avec `tar tzf` avant d'extraire au mauvais endroit.

## Créer un certificat avec openssl

La fiche Réseaux sur TLS explique ce qu'est un certificat. Voici comment en fabriquer un.

### Un certificat autosigné, pour un test

```bash
openssl req -x509 -newkey rsa:4096 -nodes -days 365 \
  -keyout cle.pem -out cert.pem \
  -subj "/CN=shop.local" -addext "subjectAltName=DNS:shop.local"
```

- `-x509` : produit directement un certificat (autosigné) et non une demande ;
- `-nodes` : la clé privée n'est pas protégée par une phrase de passe (nécessaire pour qu'un service démarre seul) ;
- `subjectAltName` : les navigateurs ne regardent que ce champ pour vérifier le nom.

Un navigateur affichera un avertissement, car aucune autorité reconnue ne l'a signé : c'est fait pour un environnement de test.

### Une demande pour une vraie autorité

```bash
openssl req -new -newkey rsa:2048 -nodes \
  -keyout api.key -out api.csr -subj "/CN=api.shop.fr"
openssl req -in api.csr -noout -text         # relire la demande
```

On envoie le `.csr` à l'autorité (ou à la PKI interne de l'entreprise). La clé `.key` ne quitte jamais le serveur : `chmod 600 api.key`.

### Inspecter et vérifier

```bash
openssl x509 -in cert.pem -noout -subject -issuer -dates -ext subjectAltName
# La clé et le certificat vont-ils ensemble ? Les deux sorties doivent être identiques
openssl x509 -in cert.pem -noout -pubkey | sha256sum
openssl pkey -in cle.pem -pubout | sha256sum
```

> **À retenir.** `find <où> <critères> -print` d'abord, `-exec … {} +` ensuite. `tar czf` crée, `tar tzf` liste, `tar xzf … -C` extrait. `openssl req -x509 … -nodes` fabrique un certificat de test ; `openssl req -new` fabrique une demande à faire signer, et la clé reste sur le serveur.
