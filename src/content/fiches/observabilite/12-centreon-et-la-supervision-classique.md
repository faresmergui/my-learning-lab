---
title: Centreon et la supervision classique
chapter: 12
order: 1
duration: 12
tags:
- Observabilité
- Centreon
- Nagios
- Zabbix
- SNMP
cards:
- q: D'où vient Centreon ?
  a: Centreon est né comme une interface web au-dessus de **Nagios**, la référence historique de la supervision. Il a ensuite développé son propre moteur (**Centreon Engine**, compatible avec les plugins Nagios) et son courtier de données (**Centreon Broker**). Il reste très répandu en France, dans les entreprises et les administrations.
- q: Comment Centreon modélise-t-il ce qu'il surveille ?
  a: 'En **hôtes** (un serveur, un équipement réseau, un hyperviseur) qui portent des **services** (un contrôle : CPU, disque `/var`, HTTP, une interface réseau). Chaque service a des **seuils** warning et critical, une **commande** de contrôle, une fréquence, et des **modèles** (templates) qui factorisent la configuration.'
- q: Que renvoie un plugin de supervision de type Nagios ?
  a: Un **code de retour** (0 = OK, 1 = WARNING, 2 = CRITICAL, 3 = UNKNOWN), une **ligne de texte** lisible, et après un `|` des **données de performance** (`'used'=72%;80;90;0;100`) que Centreon stocke pour les graphiques.
- q: Qu'est-ce qu'un poller Centreon ?
  a: Un **collecteur** (Centreon Engine) installé près des équipements supervisés (un datacenter, un site distant, une DMZ). Il exécute les contrôles et renvoie les résultats au serveur **central** via Centreon Broker. On répartit ainsi la charge et on évite d'ouvrir les flux depuis le central vers tous les réseaux.
- q: Qu'est-ce que SNMP ?
  a: 'Le **Simple Network Management Protocol** : le protocole standard de supervision des équipements réseau (commutateurs, routeurs, pare-feu, onduleurs, baies de stockage). Le superviseur interroge des **OID** (identifiants dans une arborescence, la MIB) ; l''équipement peut aussi envoyer des **traps** (alertes spontanées). Préférer **SNMPv3**, chiffré et authentifié, à v2c (communauté en clair).'
- q: Différence entre downtime et acquittement ?
  a: 'Un **downtime** (temps d''arrêt planifié) est posé **à l''avance** pour une maintenance : pas d''alerte pendant la période. Un **acquittement** (acknowledgement) se fait **pendant** un problème : « je m''en occupe », ce qui arrête les notifications répétées tant que l''état ne change pas.'
quiz:
- q: Un contrôle de disque passe en UNKNOWN sur tous les serveurs d'un site distant en même temps. Piste la plus probable ?
  options:
  - Tous les disques sont pleins
  - 'Un problème de collecte : poller du site arrêté, réseau entre poller et serveurs, ou identifiants SNMP/agent changés'
  - Une mise à jour de Centreon Web
  - Les seuils sont trop bas
  answer: 1
  explain: UNKNOWN signifie que le contrôle n'a pas pu s'exécuter, pas que la ressource va mal.
- q: Le routeur principal tombe et 300 alertes « hôte injoignable » arrivent pour les serveurs derrière. Quel réglage l'évite ?
  options:
  - Augmenter les seuils
  - 'Déclarer les dépendances parent/enfant : les hôtes derrière le routeur deviennent UNREACHABLE et ne notifient pas, seule l''alerte du routeur part'
  - Supprimer les hôtes
  - Désactiver le poller
  answer: 1
  explain: Les relations parent-enfant distinguent DOWN (l'hôte est en panne) d'UNREACHABLE (on ne peut pas le joindre à cause d'un parent).
level: intermédiaire
---

Avant Prometheus et les SaaS, la supervision d'entreprise s'est construite autour de **Nagios** et de ses descendants : **Centreon**, **Icinga**, **Shinken**, puis **Zabbix** et **PRTG** dans des styles voisins. Ces outils sont toujours très présents, surtout pour l'**infrastructure** : serveurs physiques, réseau, stockage, applications métiers anciennes, et en France particulièrement Centreon. Un DevOps les croise souvent à côté d'une stack Prometheus.

> **Les outils cités dans cette fiche.**
> - **Nagios** : l'outil historique de supervision par contrôles et plugins.
> - **Centreon** : la solution de supervision française issue de Nagios (Centreon Web, Engine, Broker, MAP, BAM).
> - **Icinga** et **Zabbix** : d'autres solutions de supervision d'infrastructure, très répandues.
> - **plugin** (sonde) : un petit programme qui teste une chose et renvoie un état ; les **Plugin Packs** de Centreon les fournissent prêts à l'emploi.
> - **SNMP** : le protocole standard de supervision des équipements réseau ; **OID** et **MIB** : ses identifiants et leur dictionnaire.
> - **poller** : un collecteur distant qui exécute les contrôles.
> - **BAM** (Business Activity Monitoring) : la vue des services métier construite à partir de plusieurs indicateurs.

## Le vocabulaire en clair

| Terme | Ce que ça veut dire |
| --- | --- |
| **hôte** | une machine ou un équipement supervisé (serveur, routeur, imprimante, VM) |
| **service** (au sens Centreon) | un contrôle précis sur un hôte : « Disque /var », « Ping », « HTTP site public » |
| **contrôle** (check) | l'exécution d'un plugin pour vérifier un hôte ou un service |
| **plugin** (sonde) | le petit programme qui fait le contrôle et renvoie un état |
| **seuils warning / critical** | les deux limites qui font passer un service en WARNING puis en CRITICAL |
| **données de performance** | les valeurs chiffrées renvoyées par le plugin, utilisées pour les graphiques |
| **Centreon Engine** | le moteur qui planifie et exécute les contrôles (le cœur hérité de Nagios) |
| **Centreon Broker** | le composant qui transporte les résultats des pollers vers le central et les bases |
| **central** | le serveur principal : interface web, configuration, bases de données |
| **poller** | un serveur de collecte placé près des équipements, qui exécute les contrôles pour le central |
| **agent** (NRPE, NSClient++, Centreon Monitoring Agent) | un programme installé sur le serveur supervisé pour répondre aux contrôles locaux (disques, services) |
| **SOFT / HARD** | un état SOFT est un problème pas encore confirmé ; il devient HARD après plusieurs contrôles en échec, et c'est alors qu'on prévient |
| **modèle** (template) | un ensemble de réglages réutilisable pour créer des hôtes ou services identiques |
| **ACL** | les règles de droits : qui voit et modifie quels hôtes |
| **RRD** | le format de fichiers où Centreon garde l'historique des graphiques |

## Comment ça marche : un contrôle, du plugin à la notification

1. Le **moteur** (Centreon Engine, sur un poller) planifie le contrôle « Disque /var » de l'hôte `srv-db1` toutes les 5 minutes.
2. À l'heure prévue, il exécute le **plugin** avec les bons paramètres. Le plugin interroge le serveur, par SNMP ou par l'agent installé dessus, et lit l'occupation du disque : 92 %.
3. Le plugin compare aux seuils (warning 80, critical 90), affiche `CRITICAL: /var 92 %` avec les données de performance, et se termine avec le code **2**.
4. Le moteur note l'état **CRITICAL SOFT 1/3** et refait le contrôle plus souvent (toutes les minutes) pour confirmer.
5. Après trois échecs consécutifs, l'état passe en **CRITICAL HARD** : la notification part (e-mail, SMS, outil d'astreinte), sauf si un **downtime** est en cours ou si l'hôte parent est en panne.
6. Le **Broker** transmet résultats et données de performance au **central**, qui met à jour l'interface et les graphiques.
7. Un opérateur **acquitte** le problème (« je m'en occupe ») : les rappels s'arrêtent. Quand le disque redescend sous les seuils, le service repasse **OK** et une notification de rétablissement part.

## Comprendre : contrôles, états, notifications

```
          Centreon central (Web, base de configuration, Broker, base temps réel, RRD)
             ▲ résultats (Broker)          │ configuration exportée
             │                             ▼
    poller site A (Engine)        poller site B / DMZ (Engine)
     │ toutes les 5 min : exécute les plugins
     ├─ SNMP → commutateur, onduleur
     ├─ agent (NRPE, NSClient++, Centreon Monitoring Agent) → disque, services Windows/Linux
     ├─ HTTP / TCP / DNS → sites, API
     └─ API → VMware, AWS, Kubernetes, bases de données
```

Chaque contrôle donne un **état** :

| Code | État service | Sens |
| --- | --- | --- |
| 0 | OK | sous les seuils |
| 1 | WARNING | seuil d'avertissement dépassé |
| 2 | CRITICAL | seuil critique dépassé ou service en panne |
| 3 | UNKNOWN | le contrôle n'a pas pu s'exécuter |

Les hôtes sont **UP**, **DOWN** ou **UNREACHABLE** (injoignable à cause d'un équipement parent). Un état passe d'abord en **SOFT**, recontrôlé plusieurs fois, puis en **HARD** : c'est alors seulement que la notification part, ce qui évite les fausses alertes.

## Un plugin, de l'intérieur

```bash
/usr/lib/centreon/plugins/centreon_linux_snmp.pl --plugin=os::linux::snmp::plugin \
  --mode=storage --hostname=10.0.0.12 --snmp-version=3 --snmp-username=supervision \
  --authprotocol=SHA --authpassphrase='…' --privprotocol=AES --privpassphrase='…' \
  --storage='^/var$' --name --warning-usage=80 --critical-usage=90
# OK: Storage '/var' Usage Total: 20.00 GB Used: 14.40 GB (72.00%) | 'used_/var'=15461882265B;…
echo $?   # 0
```

Le texte après le `|` (données de performance) alimente les **graphiques** ; le code de retour décide de l'état. N'importe quel script qui respecte ce contrat devient un contrôle.

## Bien organiser Centreon

- **Modèles** d'hôtes et de services (« Linux SNMP », « Windows », « Commutateur Cisco ») : on applique un modèle, les contrôles suivent.
- **Plugin Packs** : des modèles prêts pour des centaines d'équipements et d'applications.
- **Découverte automatique** (Auto Discovery) des hôtes d'un réseau, d'un vCenter, d'un compte cloud.
- **Groupes** et **catégories** pour les vues, les droits (ACL) et les rapports.
- **Dépendances** parent/enfant pour ne pas recevoir 300 alertes quand un routeur tombe.
- **Downtimes** pour les maintenances, **acquittements** pendant les incidents, **escalades** quand personne ne répond.
- **BAM** et **MAP** pour une vue métier (« la chaîne de paiement est dégradée ») et des cartes.
- Configuration par l'interface, ou automatisée par l'API et **CLAPI** (utile avec Ansible).

## Centreon, Zabbix, Prometheus

| | Centreon / Nagios | Zabbix | Prometheus |
| --- | --- | --- | --- |
| modèle | contrôles et états (OK/WARN/CRIT) | items, triggers, agents | métriques et requêtes |
| point fort | infrastructure, réseau, applications métiers, vue métier | tout-en-un, agents, découverte | cloud native, Kubernetes, requêtes puissantes |
| environnements dynamiques | moins adapté (hôtes déclarés) | moyen | excellent (découverte de services) |
| alerte | seuils par service | expressions de triggers | PromQL |

Les deux mondes cohabitent souvent : Centreon pour le parc et le réseau, Prometheus pour les clusters et les applications. Centreon sait aussi superviser Kubernetes et lire des métriques Prometheus via des plugins, et inversement l'exporter SNMP amène le réseau dans Prometheus.

> **À retenir.** Centreon, héritier de Nagios, supervise des hôtes et des services par des plugins qui renvoient un code (OK, WARNING, CRITICAL, UNKNOWN), un texte et des données de performance. Des pollers exécutent les contrôles près des équipements et remontent au central. États SOFT puis HARD avant notification, dépendances parent/enfant, downtimes, acquittements et escalades. SNMPv3 pour le réseau, agents pour les systèmes. Fort sur l'infrastructure et la vue métier, il cohabite souvent avec Prometheus pour le cloud native.
