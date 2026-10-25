---
title: 'Grafana : tableaux de bord et alertes'
chapter: 6
order: 1
duration: 11
tags:
- Observabilité
- Grafana
cards:
- q: Qu'est-ce que Grafana ?
  a: Une interface de **visualisation** qui interroge de nombreuses sources de données (Prometheus, Loki, Tempo, Elasticsearch, InfluxDB, PostgreSQL, CloudWatch, Datadog…) et affiche des **tableaux de bord**. Elle ne stocke pas les données elle-même. Elle gère aussi des alertes, des annotations et l'exploration (Explore).
- q: À quoi servent les variables d'un tableau de bord ?
  a: 'À rendre un tableau de bord **réutilisable** : une liste déroulante (cluster, namespace, service, instance) remplie par une requête (`label_values(up, cluster)`) et utilisée dans les requêtes des panneaux (`{cluster="$cluster"}`). Un seul tableau de bord sert alors tous les services.'
- q: Comment gérer les tableaux de bord « as code » ?
  a: Les exporter en **JSON** et les versionner dans Git, puis les déployer par **provisioning** (fichiers lus au démarrage), par le **provider Terraform Grafana**, par des ConfigMaps détectées par le sidecar du chart Helm, ou par l'opérateur Grafana. On les génère parfois avec Jsonnet (grafonnet) ou le SDK Foundation.
- q: Qu'est-ce qu'Explore dans Grafana ?
  a: 'Le mode d''**exploration** ad hoc : on écrit une requête PromQL, LogQL ou TraceQL sans créer de tableau de bord, on compare deux requêtes côte à côte, et on **saute** d''une métrique aux logs puis à la trace correspondante (liens entre sources).'
- q: Qu'est-ce qu'un bon tableau de bord ?
  a: 'Un tableau de bord qui répond à **une question** pour **un public** : en haut l''état vu par l''utilisateur (RED ou signaux dorés, SLO), puis le détail par composant, puis les ressources (USE). Peu de panneaux, des unités et des seuils clairs, les déploiements en annotations, et des liens vers les runbooks et les logs.'
quiz:
- q: Un collègue a modifié à la main le tableau de bord de production dans l'interface et tout a été perdu au redéploiement. Quelle pratique l'évite ?
  options:
  - Interdire Grafana
  - Versionner les tableaux de bord dans Git et les déployer par provisioning ou Terraform ; les modifications passent par une MR
  - Faire des captures d'écran
  - Désactiver les mises à jour
  answer: 1
  explain: Comme l'infrastructure, les tableaux de bord se gèrent en code, revus et déployés automatiquement.
- q: Un tableau de bord de 60 panneaux met 40 secondes à charger. Que fais-tu ?
  options:
  - Acheter un plus gros serveur Grafana
  - Réduire et organiser (une question par tableau de bord, rangées repliées), utiliser des recording rules pour les requêtes lourdes, adapter l'intervalle de temps par défaut
  - Augmenter la résolution
  - Ajouter des panneaux
  answer: 1
  explain: La lenteur vient presque toujours des requêtes à la source, pas de Grafana.
level: intermédiaire
---

**Grafana** est l'interface que tout le monde regarde : tableaux de bord sur les écrans de l'équipe, exploration pendant un incident, alertes. Sa force est de **ne rien stocker** et de parler à presque toutes les sources : Prometheus, Loki et Tempo, mais aussi Elasticsearch, des bases SQL, CloudWatch ou Datadog. Bien l'utiliser, c'est surtout savoir construire des tableaux de bord utiles et les gérer comme du code.

> **Les outils cités dans cette fiche.**
> - **Grafana** : l'outil open source de visualisation et d'alerte de Grafana Labs.
> - **source de données** (data source) : un système que Grafana interroge (Prometheus, Loki, Elasticsearch…).
> - **LogQL** et **TraceQL** : les langages de requête de Loki (logs) et de Tempo (traces).
> - **provisioning** : la configuration de Grafana par fichiers (sources, tableaux de bord, alertes) lus au démarrage.
> - **Jsonnet** et **grafonnet** : un langage de génération de JSON et sa bibliothèque pour les tableaux de bord Grafana.

## Le vocabulaire en clair

| Terme | Ce que ça veut dire |
| --- | --- |
| **panneau** (panel) | un graphique, une jauge, un chiffre ou un tableau dans un tableau de bord ; chaque panneau a sa ou ses requêtes |
| **source de données** (data source) | la connexion de Grafana à un système de stockage (une URL et des identifiants) |
| **requête** | la question posée à la source (en PromQL, LogQL, SQL…) pour obtenir les données d'un panneau |
| **variable** | une liste déroulante en haut du tableau de bord dont la valeur est réutilisée dans toutes les requêtes |
| **annotation** | un repère vertical sur les graphiques (un déploiement, un incident) pour relier un changement à une courbe |
| **exemplar** | un point sur un graphique de métrique qui renvoie vers une trace réelle |
| **intervalle de temps** | la période affichée (dernière heure, derniers 7 jours) ; plus elle est longue, plus la requête est lourde |
| **provisioning** | la configuration de Grafana par fichiers au démarrage, au lieu de clics dans l'interface |
| **ConfigMap** | un objet Kubernetes qui contient des fichiers de configuration (ici, le JSON d'un tableau de bord) |
| **SSO** (Single Sign-On) | la connexion avec le compte de l'entreprise, via **OIDC**, **SAML** ou **LDAP** |
| **point de contact** | dans les alertes Grafana, la destination d'une notification (comme un receiver d'Alertmanager) |

## Comment ça marche : l'affichage d'un panneau

1. Tu ouvres un tableau de bord. Grafana lit sa définition (un fichier JSON) : liste des panneaux, de leurs requêtes et de leurs réglages.
2. Il remplace les **variables** (`$service = commandes`) et l'**intervalle de temps** dans chaque requête.
3. Il envoie chaque requête à la **source de données** concernée : PromQL à Prometheus, LogQL à Loki, SQL à PostgreSQL. C'est la source qui fait le calcul.
4. Il reçoit les résultats (des séries de points ou des lignes) et les dessine selon le type de panneau, avec les unités et les seuils de couleur.
5. Toutes les 30 secondes ou à chaque minute (rafraîchissement automatique), il recommence.

Grafana ne garde donc **aucune donnée** : si Prometheus est arrêté, les panneaux qui l'utilisent sont vides. Un tableau de bord lent vient presque toujours d'une requête trop lourde côté source.

## Comprendre : Grafana au centre

<!-- schema:centre -->
<figure class="diagram"><svg viewBox="0 0 680 250" role="img" aria-label="Grafana au centre" style="--minw:560px"><defs><marker id="g3-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g3-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g3-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g3-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-c dg-pop" style="--d:0"><rect x="190" y="14" width="300" height="64" rx="9"/></g><text x="340.0" y="36.0" class="dg-t" text-anchor="middle" style="--d:0">Grafana</text><text x="340.0" y="54.0" class="dg-s" text-anchor="middle" style="--d:0"><tspan x="340.0" dy="0">tableaux de bord, Explore,</tspan><tspan x="340.0" dy="14">alertes, annotations</tspan></text><path d="M340 78 L340 118" class="dg-l c"/><path d="M89 118 L593 118" class="dg-l c"/><g class="dg-box dg-pop" style="--d:1"><rect x="14" y="170" width="150" height="56" rx="9"/></g><text x="89.0" y="195.0" class="dg-t" text-anchor="middle" style="--d:1">Prometheus · Mimir</text><text x="89.0" y="213.0" class="dg-s" text-anchor="middle" style="--d:1">métriques</text><path d="M89 118 L89 168" class="dg-l c" marker-end="url(#g3-c)"/><text x="97" y="150" class="dg-s" text-anchor="start">PromQL</text><g class="dg-box dg-pop" style="--d:2"><rect x="182" y="170" width="150" height="56" rx="9"/></g><text x="257.0" y="195.0" class="dg-t" text-anchor="middle" style="--d:2">Loki</text><text x="257.0" y="213.0" class="dg-s" text-anchor="middle" style="--d:2">logs</text><path d="M257 118 L257 168" class="dg-l c" marker-end="url(#g3-c)"/><text x="265" y="150" class="dg-s" text-anchor="start">LogQL</text><g class="dg-box dg-pop" style="--d:3"><rect x="350" y="170" width="150" height="56" rx="9"/></g><text x="425.0" y="195.0" class="dg-t" text-anchor="middle" style="--d:3">Tempo</text><text x="425.0" y="213.0" class="dg-s" text-anchor="middle" style="--d:3">traces</text><path d="M425 118 L425 168" class="dg-l c" marker-end="url(#g3-c)"/><text x="433" y="150" class="dg-s" text-anchor="start">TraceQL</text><g class="dg-box dg-pop" style="--d:4"><rect x="518" y="170" width="150" height="56" rx="9"/></g><text x="593.0" y="195.0" class="dg-t" text-anchor="middle" style="--d:4">Elasticsearch, SQL…</text><text x="593.0" y="213.0" class="dg-s" text-anchor="middle" style="--d:4">et bien d&#x27;autres</text><path d="M593 118 L593 168" class="dg-l c" marker-end="url(#g3-c)"/><text x="601" y="150" class="dg-s" text-anchor="start">SQL…</text></svg><figcaption>Grafana ne stocke rien : il interroge chaque source dans son propre langage.</figcaption></figure>
<!-- /schema:centre -->

Les **liens entre sources** font la différence pendant un incident : depuis un pic de latence, ouvrir les logs du même service sur la même période, puis la trace d'une requête lente (exemplars, champs `trace_id` dans les logs).

## Construire un bon tableau de bord

```
┌──────────────────────────────────────────────────────────────┐
│ Service « commandes »   [cluster ▾] [namespace ▾]  dernière 1 h │
├───────────────┬───────────────┬───────────────┬──────────────┤
│ débit (req/s) │ erreurs (%)   │ p99 latence   │ SLO 30 j     │  ← vu par l'utilisateur
├───────────────┴───────────────┴───────────────┴──────────────┤
│ latence par route · erreurs par code · déploiements (annotations) │  ← détail
├──────────────────────────────────────────────────────────────┤
│ CPU / mémoire des pods · connexions base · file RabbitMQ        │  ← ressources
└──────────────────────────────────────────────────────────────┘
```

- **Une question, un public** : « le service va-t-il bien ? » pour l'astreinte, « où partent les ressources ? » pour la capacité.
- **Variables** (`$cluster`, `$namespace`, `$service`) pour un seul tableau de bord réutilisable.
- **Unités et seuils** sur chaque panneau (ms, %, octets ; vert, orange, rouge).
- **Annotations** des déploiements et incidents : la majorité des problèmes suivent un changement.
- **Liens** vers le runbook, les logs, le tableau de bord du composant suivant.
- **Peu de panneaux** : au-delà d'une vingtaine, découper.

## Les tableaux de bord en code

```yaml
# provisioning/dashboards/plateforme.yaml
apiVersion: 1
providers:
  - name: plateforme
    folder: Plateforme
    type: file
    options: { path: /var/lib/grafana/dashboards/plateforme }
```

```hcl
resource "grafana_dashboard" "commandes" {
  folder      = grafana_folder.plateforme.id
  config_json = file("${path.module}/dashboards/commandes.json")
}
```

Sur Kubernetes, le chart `kube-prometheus-stack` fournit un **sidecar** qui charge tout ConfigMap portant l'étiquette `grafana_dashboard: "1"` : les tableaux de bord voyagent avec l'application, dans son dépôt, via ArgoCD. Les tableaux de bord communautaires (Grafana.com, par identifiant) sont un bon point de départ, à adapter.

## Les alertes Grafana

Grafana sait aussi évaluer des **règles d'alerte** sur n'importe quelle source (pas seulement Prometheus), avec des points de contact (Slack, e-mail, PagerDuty, webhook), des politiques de notification et des silences, sur le modèle d'Alertmanager. Choisir **un seul endroit** pour les règles d'une même source évite les doublons : souvent les règles Prometheus restent dans Prometheus/Mimir (versionnées avec l'application), et Grafana sert pour les sources qui n'ont pas d'alerte propre (SQL, Elasticsearch, CloudWatch).

## Exploiter Grafana

- **Authentification** : SSO (OIDC, SAML, LDAP), équipes et dossiers avec permissions.
- **Base de données** : SQLite par défaut ; PostgreSQL ou MySQL pour la haute disponibilité (plusieurs instances).
- **Plugins** : sources et visualisations supplémentaires, à épingler en version.
- **Sauvegarde** : la base (utilisateurs, préférences) ; les tableaux de bord sont déjà dans Git.

> **À retenir.** Grafana visualise sans stocker et interroge presque toutes les sources ; Explore et les liens entre métriques, logs et traces accélèrent les incidents. Un bon tableau de bord répond à une question pour un public : état vu par l'utilisateur en haut, détail, puis ressources, avec variables, unités, seuils, annotations de déploiement et liens. Les tableaux de bord se gèrent en code (JSON dans Git, provisioning, Terraform, ConfigMaps). Les alertes Grafana couvrent toutes les sources ; garder un seul endroit par source.
