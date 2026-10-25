---
title: 'Prometheus : architecture et collecte'
chapter: 3
order: 1
duration: 12
tags:
- Observabilité
- Prometheus
cards:
- q: Quels sont les composants d'une installation Prometheus ?
  a: Le **serveur Prometheus** (scrape, stocke dans sa TSDB locale, évalue les règles), les **exporters** qui exposent les métriques de systèmes tiers, **Alertmanager** (regroupe et envoie les alertes), éventuellement la **Pushgateway** (tâches batch) et **Grafana** pour les tableaux de bord.
- q: Qu'est-ce qu'un exporter ?
  a: 'Un petit programme qui lit les statistiques d''un système qui ne parle pas Prometheus (Linux, MySQL, RabbitMQ, un équipement SNMP…) et les expose au format Prometheus sur une URL `/metrics`. Exemples : **node_exporter**, **mysqld_exporter**, **blackbox_exporter**, **snmp_exporter**.'
- q: Comment Prometheus trouve-t-il ses cibles ?
  a: 'Par une liste statique dans `scrape_configs`, ou par **découverte de services** : Kubernetes (pods, services, endpoints), Consul, EC2, OpenStack, DNS, fichiers. Les **relabel_configs** filtrent les cibles et transforment leurs étiquettes avant le scrape.'
- q: Que veut dire la métrique `up` ?
  a: 'Prometheus crée pour chaque cible une série `up` qui vaut **1** si le dernier scrape a réussi et **0** sinon. `up == 0` est l''alerte de base : la cible ne répond plus (service arrêté, réseau, mauvais port).'
- q: Quelles sont les limites d'un serveur Prometheus seul ?
  a: Stockage **local** (rétention de quelques semaines en pratique), pas de **haute disponibilité** native (on lance deux serveurs identiques), mémoire proportionnelle au nombre de séries actives, et vision limitée à ce qu'il scrape. D'où Thanos, Mimir ou VictoriaMetrics pour le long terme et la vue globale.
- q: À quoi sert le blackbox_exporter ?
  a: 'À la supervision **boîte noire** : Prometheus lui demande de sonder une cible (HTTP, HTTPS avec date d''expiration du certificat, TCP, ICMP, DNS) et récupère le résultat (`probe_success`, `probe_duration_seconds`, `probe_ssl_earliest_cert_expiry`).'
quiz:
- q: Un pod expose bien `/metrics`, mais n'apparaît pas dans les cibles de Prometheus sur Kubernetes. Que vérifies-tu ?
  options:
  - Le CPU du nœud
  - 'La découverte : le ServiceMonitor ou PodMonitor (avec l''opérateur) sélectionne-t-il bien ses labels et son namespace, le port est-il nommé comme attendu, et les relabel_configs ne l''excluent-ils pas'
  - Le DNS public
  - La version de Grafana
  answer: 1
  explain: La page Status > Targets (et Service Discovery) de Prometheus montre les cibles découvertes et celles écartées par le relabeling.
- q: Comment rendre Prometheus hautement disponible le plus simplement ?
  options:
  - Un cluster Prometheus natif
  - Deux serveurs identiques qui scrapent les mêmes cibles, Alertmanager en cluster qui déduplique les alertes, et Thanos ou Mimir pour fusionner les données à la lecture
  - Un seul serveur avec un gros disque
  - Un NFS partagé entre deux serveurs
  answer: 1
  explain: Prometheus n'a pas de réplication ; on double les serveurs, et la couche au-dessus déduplique.
level: intermédiaire
---

**Prometheus** est devenu le standard des métriques dans le monde cloud native : Kubernetes, la plupart des logiciels modernes et des centaines d'exporters parlent son format. Comprendre son architecture et sa façon de collecter, c'est comprendre la base de la majorité des stacks d'observabilité actuelles, y compris celles qui stockent ailleurs (Mimir, VictoriaMetrics, Datadog sait aussi lire ce format).

> **Les outils cités dans cette fiche.**
> - **Prometheus** : le système de supervision par métriques de la CNCF, qui collecte en pull et stocke en local.
> - **exporter** : un programme qui expose les métriques d'un système tiers au format Prometheus.
> - **Alertmanager** : le composant qui regroupe, déduplique et envoie les alertes.
> - **Pushgateway** : un intermédiaire où les tâches courtes déposent leurs métriques.
> - **Prometheus Operator** : l'opérateur Kubernetes qui gère Prometheus par des ressources (`ServiceMonitor`, `PodMonitor`, `PrometheusRule`).
> - **CNCF** (Cloud Native Computing Foundation) : la fondation qui héberge Kubernetes, Prometheus, OpenTelemetry…

## Le vocabulaire en clair

| Terme | Ce que ça veut dire |
| --- | --- |
| **cible** (target) | une adresse que Prometheus interroge, par exemple `srv1:9100/metrics` |
| **job** | un groupe de cibles du même type (« tous les node_exporter », « tous les pods de l'API ») ; il devient l'étiquette `job` |
| **instance** | une cible précise (`srv1:9100`) ; elle devient l'étiquette `instance` |
| **/metrics** | l'URL où un service publie ses métriques en texte, au format Prometheus |
| **port** | chaque exporter écoute sur un port habituel : 9100 pour node_exporter, 9115 pour blackbox, 9090 pour Prometheus lui-même, 9093 pour Alertmanager |
| **découverte de services** | Prometheus demande à Kubernetes, à OpenStack ou à Consul la liste à jour des machines et des pods, au lieu d'une liste écrite à la main |
| **relabeling** | des règles qui filtrent les cibles découvertes et renomment ou ajoutent des étiquettes avant la collecte |
| **TSDB** | la base de séries temporelles intégrée à Prometheus, qui écrit sur le disque local |
| **bloc** | un morceau de la base couvrant 2 heures de données ; les blocs anciens sont fusionnés (**compaction**) pour prendre moins de place |
| **ServiceMonitor** | un objet Kubernetes (créé par le Prometheus Operator) qui dit « collecte les métriques des services portant tel label » |
| **sidecar** | un conteneur ajouté à côté d'un autre dans le même pod pour lui rendre un service |

## Comment ça marche : un cycle de collecte

1. **Découvrir** : au démarrage puis en continu, Prometheus construit la liste des cibles (fichier de configuration, ou API Kubernetes qui annonce chaque nouveau pod).
2. **Filtrer** : les règles de relabeling gardent seulement les cibles voulues et préparent leurs étiquettes (namespace, nom du pod, application).
3. **Interroger** : toutes les 30 secondes (par exemple), Prometheus envoie une requête HTTP `GET /metrics` à chaque cible. La cible répond par une page de texte avec toutes ses mesures.
4. **Enregistrer** : chaque ligne devient un point dans la série correspondante, avec l'horodatage de la lecture. Prometheus ajoute la série `up` (1 si la lecture a réussi, 0 sinon).
5. **Évaluer** : toutes les 30 secondes aussi, il calcule les règles (pré-calculs et alertes) et transmet les alertes actives à Alertmanager.
6. **Répondre** : quand Grafana lui envoie une requête PromQL, il lit les séries sur la période demandée et renvoie le résultat.

C'est le modèle **pull** : c'est toujours Prometheus qui va chercher. Une cible qui ne répond plus se voit donc immédiatement.

## Comprendre : l'architecture

<!-- schema:archi -->
<figure class="diagram"><svg viewBox="0 0 680 330" role="img" aria-label="L&#x27;architecture de Prometheus" style="--minw:560px"><defs><marker id="g1-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g1-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g1-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g1-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><text x="14" y="40" class="dg-zl" text-anchor="start">cibles</text><g class="dg-box dg-pop" style="--d:0"><rect x="14" y="52" width="176" height="44" rx="9"/></g><text x="102.0" y="71.0" class="dg-t" text-anchor="middle" style="--d:0">app</text><text x="102.0" y="89.0" class="dg-s" text-anchor="middle" style="--d:0">bibliothèque client</text><path d="M190 74 L222 74 L222 185 L246 185" class="dg-l c" marker-end="url(#g1-c)"/><g class="dg-box dg-pop" style="--d:1"><rect x="14" y="106" width="176" height="44" rx="9"/></g><text x="102.0" y="125.0" class="dg-t" text-anchor="middle" style="--d:1">node_exporter</text><text x="102.0" y="143.0" class="dg-s" text-anchor="middle" style="--d:1">la machine</text><path d="M190 128 L222 128 L222 185 L246 185" class="dg-l c" marker-end="url(#g1-c)"/><g class="dg-box dg-pop" style="--d:2"><rect x="14" y="160" width="176" height="44" rx="9"/></g><text x="102.0" y="179.0" class="dg-t" text-anchor="middle" style="--d:2">mysqld_exporter</text><text x="102.0" y="197.0" class="dg-s" text-anchor="middle" style="--d:2">une base</text><path d="M190 182 L222 182 L222 185 L246 185" class="dg-l c" marker-end="url(#g1-c)"/><g class="dg-box dg-pop" style="--d:3"><rect x="14" y="214" width="176" height="44" rx="9"/></g><text x="102.0" y="233.0" class="dg-t" text-anchor="middle" style="--d:3">blackbox_exporter</text><text x="102.0" y="251.0" class="dg-s" text-anchor="middle" style="--d:3">sondes HTTP, ICMP</text><path d="M190 236 L222 236 L222 185 L246 185" class="dg-l c" marker-end="url(#g1-c)"/><g class="dg-box dg-pop" style="--d:4"><rect x="14" y="268" width="176" height="44" rx="9"/></g><text x="102.0" y="287.0" class="dg-t" text-anchor="middle" style="--d:4">pushgateway</text><text x="102.0" y="305.0" class="dg-s" text-anchor="middle" style="--d:4">jobs batch</text><path d="M190 290 L222 290 L222 185 L246 185" class="dg-l c" marker-end="url(#g1-c)"/><g class="dg-box dg-ghost dg-pop" style="--d:0"><rect x="230" y="14" width="250" height="36" rx="9"/></g><text x="355.0" y="37.0" class="dg-s" text-anchor="middle" style="--d:0">découverte de services</text><path d="M355 50 L355 128" class="dg-l dash" marker-end="url(#g1-n)"/><text x="365" y="96" class="dg-s" text-anchor="start">liste des cibles</text><g class="dg-box dg-c dg-pop" style="--d:5"><rect x="248" y="130" width="210" height="112" rx="9"/></g><text x="353.0" y="169.0" class="dg-t" text-anchor="middle" style="--d:5">Prometheus</text><text x="353.0" y="187.0" class="dg-s" text-anchor="middle" style="--d:5"><tspan x="353.0" dy="0">lit /metrics toutes les 15-30 s</tspan><tspan x="353.0" dy="14">TSDB locale</tspan><tspan x="353.0" dy="14">règles : recording, alerting</tspan></text><g class="dg-box dg-a dg-pop" style="--d:6"><rect x="520" y="96" width="146" height="52" rx="9"/></g><text x="593.0" y="119.0" class="dg-t" text-anchor="middle" style="--d:6">Alertmanager</text><text x="593.0" y="137.0" class="dg-s" text-anchor="middle" style="--d:6">Slack, PagerDuty…</text><path d="M458 185 L490 185 L490 122 L518 122" class="dg-l a" marker-end="url(#g1-a)"/><g class="dg-box dg-pop" style="--d:7"><rect x="520" y="166" width="146" height="52" rx="9"/></g><text x="593.0" y="189.0" class="dg-t" text-anchor="middle" style="--d:7">Grafana</text><text x="593.0" y="207.0" class="dg-s" text-anchor="middle" style="--d:7">requêtes PromQL</text><path d="M458 185 L490 185 L490 192 L518 192" class="dg-l c" marker-end="url(#g1-c)" marker-start="url(#g1-c)"/><g class="dg-box dg-pop" style="--d:8"><rect x="520" y="236" width="146" height="52" rx="9"/></g><text x="593.0" y="252.0" class="dg-t" text-anchor="middle" style="--d:8">long terme</text><text x="593.0" y="270.0" class="dg-s" text-anchor="middle" style="--d:8"><tspan x="593.0" dy="0">Thanos, Mimir,</tspan><tspan x="593.0" dy="14">VictoriaMetrics</tspan></text><path d="M458 185 L490 185 L490 262 L518 262" class="dg-l c" marker-end="url(#g1-c)"/><text x="593" y="306" class="dg-s" text-anchor="middle">via remote_write</text></svg><figcaption>Prometheus va chercher les métriques (pull) ; il garde peu d&#x27;historique et délègue les notifications à Alertmanager.</figcaption></figure>
<!-- /schema:archi -->

## Le format exposé

```text
# HELP http_requests_total Nombre de requêtes HTTP.
# TYPE http_requests_total counter
http_requests_total{method="GET",code="200"} 15342
http_requests_total{method="GET",code="500"} 12
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.1"} 14200
http_request_duration_seconds_bucket{le="0.5"} 15300
http_request_duration_seconds_bucket{le="+Inf"} 15354
http_request_duration_seconds_sum 1230.5
http_request_duration_seconds_count 15354
```

Une application s'instrumente avec une **bibliothèque client** (Go, Java, Python…) ou avec **OpenTelemetry**, qui peut exporter dans ce format.

## La configuration

```yaml
global:
  scrape_interval: 30s
  evaluation_interval: 30s
rule_files: [ "rules/*.yml" ]
alerting:
  alertmanagers: [ { static_configs: [ { targets: ["alertmanager:9093"] } ] } ]
scrape_configs:
  - job_name: node
    static_configs: [ { targets: ["srv1:9100", "srv2:9100"] } ]
  - job_name: kubernetes-pods
    kubernetes_sd_configs: [ { role: pod } ]
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: "true"
  - job_name: blackbox-https
    metrics_path: /probe
    params: { module: [http_2xx] }
    static_configs: [ { targets: ["https://api.example.com/health"] } ]
    relabel_configs:
      - { source_labels: [__address__], target_label: __param_target }
      - { source_labels: [__param_target], target_label: instance }
      - { target_label: __address__, replacement: "blackbox:9115" }
```

Sur Kubernetes, on n'écrit presque jamais cette configuration à la main : le **Prometheus Operator** (installé par le chart `kube-prometheus-stack`) la génère à partir de `ServiceMonitor` et `PodMonitor`.

## Les exporters à connaître

| Exporter | Ce qu'il expose |
| --- | --- |
| node_exporter | CPU, mémoire, disques, réseau, systèmes de fichiers d'un hôte Linux |
| blackbox_exporter | sondes HTTP, TCP, ICMP, DNS, expiration des certificats |
| snmp_exporter | équipements réseau (commutateurs, routeurs, onduleurs) |
| mysqld, postgres, redis, rabbitmq… | métriques des bases et des files |
| kube-state-metrics | état des objets Kubernetes (déploiements, pods, jobs) |
| cAdvisor (dans le kubelet) | consommation des conteneurs |
| openstack-exporter | état des services et quotas OpenStack |

## Exploiter Prometheus

- **Status > Targets** : chaque cible, son état, la dernière erreur de scrape.
- **Status > TSDB Status** : les métriques et étiquettes qui ont le plus de séries (chasse à la cardinalité).
- **Mémoire** : proportionnelle aux séries actives (compter quelques kilo-octets par série) ; surveiller `prometheus_tsdb_head_series`.
- **Rétention** : `--storage.tsdb.retention.time=15d` ou `.size=` ; au-delà, un stockage long terme.
- **Haute disponibilité** : deux serveurs identiques ; Alertmanager en cluster déduplique ; Thanos ou Mimir fusionnent à la lecture.

> **À retenir.** Prometheus scrape en pull des cibles qui exposent `/metrics`, trouvées par configuration statique ou découverte de services, filtrées par relabeling. Il stocke en local, évalue des règles et envoie les alertes à Alertmanager. Les exporters (node, blackbox, snmp, bases, kube-state-metrics) couvrent ce qui ne parle pas Prometheus. `up == 0` signale une cible perdue. Sur Kubernetes, l'opérateur gère tout par ServiceMonitor et PrometheusRule. Limites : stockage local et pas de HA native, d'où Thanos, Mimir ou VictoriaMetrics.
