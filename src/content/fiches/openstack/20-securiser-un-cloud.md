---
title: Sécuriser un cloud
chapter: 20
order: 1
duration: 14
tags:
- OpenStack
- EX210
- Sécurité
- TLS
cards:
- q: Que veut dire « TLS partout » (TLS-e) dans un cloud OpenStack ?
  a: Chiffrer non seulement les **API publiques**, mais aussi les **API internes**, les connexions à **Galera** et **RabbitMQ**, les bases **OVN**, la console VNC et la migration libvirt. Les certificats sont émis par une AC interne (FreeIPA/IdM dans RHOSP, cert-manager dans RHOSO) et renouvelés automatiquement.
- q: Comment fonctionnent les politiques d'accès des services OpenStack ?
  a: Chaque service a un fichier **oslo.policy** (`policy.yaml`) qui associe chaque action d'API (`os_compute_api:servers:create`) à une règle (`role:member and project_id:%(project_id)s`). On peut surcharger une règle pour créer un **rôle personnalisé**, sans modifier le code.
- q: Que sont les rôles par défaut et les portées depuis les versions récentes ?
  a: 'Les rôles **reader**, **member**, **manager** et **admin**, combinés à la **portée** du jeton : projet, domaine ou système. Avec `enforce_scope` et `enforce_new_defaults`, un admin de projet n''est plus admin de tout le cloud, et un `reader` peut consulter sans rien changer.'
- q: Comment créer un rôle qui peut seulement redémarrer des instances ?
  a: Créer le rôle (`openstack role create redemarreur`), l'attribuer sur un projet, puis dans le `policy.yaml` de Nova ajouter `role:redemarreur` aux règles `os_compute_api:servers:reboot` (et `servers:index`/`show` pour voir), sans lui donner `member`.
- q: Qu'est-ce qu'AIDE et pourquoi l'utiliser sur les nœuds ?
  a: '**AIDE** (Advanced Intrusion Detection Environment) photographie les empreintes des fichiers sensibles (binaires, configuration) dans une base, puis signale toute modification lors des vérifications suivantes. Sur les computes et contrôleurs, il détecte un fichier modifié par un attaquant ou par une erreur.'
- q: Quelles sont les principales mesures d'isolation entre projets ?
  a: Réseaux Geneve séparés par projet, **groupes de sécurité** par défaut fermés en entrée, **port security** (anti-usurpation d'IP et de MAC), sVirt/SELinux qui isole chaque processus QEMU, quotas, et RBAC limité pour les réseaux et images partagés.
quiz:
- q: Un auditeur doit pouvoir lister toutes les ressources du cloud sans rien modifier. Quelle attribution ?
  options:
  - admin sur tous les projets
  - Le rôle reader en portée système (`openstack role add --system all --user auditeur reader`)
  - member partout
  - Un compte admin partagé
  answer: 1
  explain: Le reader système voit tout en lecture, à condition que les nouvelles politiques par défaut soient appliquées.
- q: AIDE signale que `/usr/libexec/qemu-kvm` a changé sur un compute alors qu'aucune mise à jour n'a eu lieu. Que fais-tu ?
  options:
  - Mettre à jour la base AIDE et oublier
  - 'Traiter comme un incident : isoler le nœud (disable, migration des VM), investiguer, réinstaller depuis une source sûre'
  - Redémarrer le compute
  - Rien
  answer: 1
  explain: Un binaire d'hyperviseur modifié sans mise à jour est un signal grave ; on ne régénère la base AIDE qu'après une modification connue et voulue.
level: intermédiaire
---

Un cloud mutualise des machines entre des projets qui ne se font pas confiance : la sécurité y est double. Il faut protéger **l'infrastructure** (API, bases, bus de messages, nœuds) et **isoler les utilisateurs** entre eux avec des droits précis. L'EX210 demande de sécuriser les services de bout en bout, d'utiliser AIDE, et de gérer les accès (rôles personnalisés, portées, domaines). Cette fiche reste du côté de la défense.

> **Les outils cités dans cette fiche.**
> - **TLS** : le chiffrement des connexions (voir la fiche TLS et PKI) ; **AC** : une autorité de certification.
> - **IdM** (Red Hat Identity Management, issu de **FreeIPA**) : annuaire, Kerberos et AC interne ; **cert-manager** : l'outil qui gère les certificats dans Kubernetes et OpenShift.
> - **oslo.policy** : la bibliothèque commune à tous les services qui applique les règles d'accès.
> - **AIDE** : un outil qui détecte les fichiers modifiés en comparant leurs empreintes à une base de référence.
> - **SELinux** et **sVirt** : le contrôle d'accès obligatoire de RHEL, qui isole chaque VM dans son propre contexte.
> - **port security** : la protection Neutron qui empêche une VM d'envoyer du trafic avec une autre adresse IP ou MAC que la sienne.
> - **API** : interface qui permet à un programme d'en piloter un autre par des requêtes (souvent HTTP).
> - **OVN** : Open Virtual Network : le moteur qui réalise les réseaux virtuels d'OpenStack (voir la fiche OVN).
> - **EDPM** : la partie de RHOSO qui configure les nœuds RHEL du data plane par Ansible.
> - **SSH** : le protocole de connexion à distance chiffrée à une machine, en ligne de commande.
> - **MFA** : l'authentification à plusieurs facteurs : mot de passe plus un code ou une clé physique.
> - **RBAC** : le contrôle d'accès par rôles : on donne des droits à des rôles, puis des rôles aux personnes ou programmes.
> - **LUKS** : le chiffrement de disque standard de Linux.

## Comprendre : les surfaces à protéger

```
Internet ─► API publiques (TLS, limitation de débit)  ─► Keystone (MFA, verrouillage, LDAP)
             │
   réseau de gestion : API internes · Galera · RabbitMQ · memcached · OVN NB/SB   ← TLS, mots de passe forts
             │
   computes : libvirt/QEMU (sVirt), migration chiffrée, console VNC/SPICE   ← TLS, SELinux enforcing
             │
   projets : réseaux séparés, groupes de sécurité, port security, quotas, RBAC   ← politique d'accès
```

## TLS de bout en bout

| Connexion | Comment la chiffrer |
| --- | --- |
| API publiques | certificat public sur HAProxy (ou la route OpenShift) |
| API internes | certificats de l'AC interne sur chaque endpoint `internal` |
| Galera, RabbitMQ, memcached | TLS activé dans l'outil de déploiement (`tls: true` dans les CR RHOSO, `kolla_enable_tls_backend`) |
| OVN NB/SB | `ssl:` au lieu de `tcp:` dans les connexions |
| libvirt (migration, VNC) | certificats libvirt et `live_migration_with_native_tls` |

Dans **RHOSO**, le TLS est activé par défaut sur les API et les services internes : cert-manager émet et renouvelle les certificats. Dans **RHOSP**, le « TLS everywhere » s'appuyait sur **IdM** comme autorité. Vérification simple : `openstack endpoint list` doit montrer `https://` partout, et `openssl s_client -connect <endpoint>:<port>` montre le certificat et sa date d'expiration.

## Les droits : rôles, portées, politiques

```bash
openstack role list                                       # reader, member, manager, admin…
openstack role add --project web --user alice member
openstack role add --system all --user auditeur reader    # lecture sur tout le cloud
openstack role add --domain client-acme --user bob manager
openstack role assignment list --user alice --names --effective
```

Un **rôle personnalisé** se construit en deux temps : créer le rôle dans Keystone, puis l'utiliser dans la politique du service.

```yaml
# /etc/nova/policy.yaml (surcharge ; l'outil de déploiement sait la poser)
"os_compute_api:servers:reboot": "role:member or role:redemarreur"
"os_compute_api:servers:index":  "role:reader or role:redemarreur"
"os_compute_api:servers:show":   "role:reader or role:redemarreur"
```

```bash
oslopolicy-sample-generator --namespace nova        # toutes les règles et leurs valeurs par défaut
oslopolicy-checker --policy /etc/nova/policy.yaml --access jeton.json   # tester ce qu'un jeton peut faire
```

Les **identifiants d'application** (`openstack application credential create --role reader --restricted`) donnent à un robot un accès limité à un projet et à certains rôles, voire à certaines routes d'API (`--access-rules`), sans partager un mot de passe.

## Durcir les nœuds

- **SELinux en mode enforcing** sur tous les nœuds : sVirt empêche une VM compromise de lire les disques des autres.
- **AIDE** pour détecter les modifications de fichiers sensibles :

```bash
aide --init && mv /var/lib/aide/aide.db.new.gz /var/lib/aide/aide.db.gz   # base de référence
aide --check                                     # comparer (tâche planifiée, résultat envoyé aux logs)
aide --update                                    # après une mise à jour voulue
```

  RHOSO fournit un rôle EDPM pour installer et planifier AIDE sur les nœuds du data plane ; ailleurs, un timer systemd ou un cron suffit. La base de référence doit être gardée hors du nœud, sinon un attaquant la régénère.
- **Mises à jour** régulières, SSH par clés, comptes nominatifs, journaux centralisés.
- **Keystone** : verrouillage après échecs (`lockout_failure_attempts`), expiration des mots de passe, MFA pour les comptes sensibles, fédération vers l'annuaire de l'entreprise.

## Isoler les projets

| Mesure | Ce qu'elle empêche |
| --- | --- |
| groupe de sécurité `default` fermé en entrée | l'exposition accidentelle d'une VM |
| port security et allowed address pairs contrôlés | l'usurpation d'IP ou de MAC, l'écoute du trafic des autres |
| réseaux Geneve par projet | que deux projets se voient au niveau 2 |
| RBAC ciblé sur les réseaux et images partagés | le partage à tous (`--share`, `--public`) par facilité |
| chiffrement des volumes (LUKS, clé dans Barbican) | la lecture des données sur le stockage |
| quotas | qu'un projet épuise le cloud |

> **À retenir.** TLS sur les API publiques et internes, Galera, RabbitMQ, OVN et libvirt, certificats gérés par IdM (RHOSP) ou cert-manager (RHOSO). Les droits combinent rôles (reader, member, manager, admin) et portées (projet, domaine, système) ; un rôle personnalisé se crée dans Keystone puis s'utilise dans le policy.yaml du service. Nœuds durcis : SELinux enforcing, AIDE avec une base gardée à l'extérieur, mises à jour. Projets isolés par réseaux, groupes de sécurité, port security, RBAC et quotas.
