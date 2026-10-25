---
title: Traces distribuées et OpenTelemetry
chapter: 11
order: 1
duration: 13
tags:
- Observabilité
- Traces
- OpenTelemetry
- Tempo
- Jaeger
cards:
- q: Qu'est-ce qu'une trace et un span ?
  a: 'Une **trace** est le parcours complet d''une requête à travers les services. Elle est faite de **spans** : chaque span représente une opération (appel HTTP, requête SQL, envoi dans une file) avec son début, sa durée, son service, ses attributs et son **parent**. Ensemble, ils forment un arbre qui montre où passe le temps.'
- q: Comment le contexte de trace passe-t-il d'un service à l'autre ?
  a: 'Par **propagation** : le service appelant ajoute l''identifiant de trace et de span dans les en-têtes de la requête (standard W3C **traceparent**), et le service appelé le lit pour rattacher ses spans à la même trace. Sans propagation (proxy qui supprime l''en-tête, file de messages non instrumentée), la trace est coupée.'
- q: Qu'est-ce qu'OpenTelemetry ?
  a: 'Le standard ouvert (CNCF) pour **produire et transporter** les traces, métriques et logs : des **API et SDK** par langage, l''**auto-instrumentation** (Java, Python, .NET, Node…), le protocole **OTLP** et le **Collector**. Il est neutre vis-à-vis du stockage : Tempo, Jaeger, Elastic, Datadog, Prometheus et la plupart des SaaS l''acceptent.'
- q: Que fait l'OpenTelemetry Collector ?
  a: 'Il **reçoit** (receivers : OTLP, Prometheus, Jaeger, logs de fichiers…), **traite** (processors : batch, filtrage, ajout d''attributs Kubernetes, masquage, échantillonnage) et **exporte** (exporters : Tempo, Loki, Prometheus/Mimir, Elastic, Datadog…). On le déploie en **agent** (DaemonSet, sidecar) et en **passerelle** centrale.'
- q: Différence entre échantillonnage head et tail ?
  a: '**Head sampling** : on décide au **début** de la requête de la garder ou non (par exemple 10 %), simple et peu coûteux, mais on perd des traces d''erreur. **Tail sampling** : le Collector garde les spans en mémoire et décide **à la fin**, selon le résultat (garder toutes les erreurs et les requêtes lentes, 5 % du reste). Plus utile, plus gourmand.'
- q: Qu'est-ce que Tempo et Jaeger ?
  a: Deux **stockages et interfaces de traces** open source. **Jaeger** (CNCF) est historique, avec sa propre interface. **Grafana Tempo** stocke les traces dans du stockage objet sans index coûteux, s'interroge en **TraceQL** et s'intègre à Grafana, Loki et Prometheus (liens trace ↔ logs ↔ métriques).
quiz:
- q: Dans Tempo, les traces s'arrêtent toujours au passage par RabbitMQ. Pourquoi ?
  options:
  - Tempo est plein
  - 'Le contexte de trace n''est pas propagé dans les messages : il faut l''injecter dans les en-têtes du message côté producteur et l''extraire côté consommateur (instrumentation de la bibliothèque de messagerie)'
  - RabbitMQ est trop lent
  - L'échantillonnage est à 100 %
  answer: 1
  explain: La propagation doit traverser chaque saut, HTTP comme messagerie.
- q: Tu gardes 1 % des traces au hasard et ne retrouves jamais celles des erreurs rares. Que changer ?
  options:
  - Passer à 100 % partout
  - Un tail sampling dans l'OpenTelemetry Collector qui garde toutes les traces en erreur ou lentes, et un faible pourcentage des autres
  - Supprimer les traces
  - Baisser à 0,1 %
  answer: 1
  explain: Le tail sampling décide après avoir vu la trace complète, donc peut garder ce qui est intéressant.
level: intermédiaire
---

Dans une architecture de microservices, une requête lente peut traverser dix services, une file de messages et trois bases de données. Les métriques disent que « c'est lent », les logs racontent chaque service séparément ; seule une **trace distribuée** montre le parcours complet et l'endroit exact où le temps se perd. **OpenTelemetry** est devenu la façon standard de produire ces traces, et plus largement tous les signaux.

> **Les outils cités dans cette fiche.**
> - **trace distribuée** : l'enregistrement du parcours d'une requête à travers plusieurs services.
> - **span** : une opération dans une trace (appel, requête SQL), avec sa durée et son parent.
> - **OpenTelemetry** (OTel) : le standard ouvert d'instrumentation et de transport des traces, métriques et logs.
> - **OTLP** : le protocole d'OpenTelemetry (en gRPC ou HTTP).
> - **W3C Trace Context** : le standard d'en-têtes HTTP (`traceparent`) qui transporte l'identifiant de trace.
> - **Jaeger** : un système de traces open source de la CNCF ; **Grafana Tempo** : celui de Grafana Labs ; **TraceQL** : le langage de requête de Tempo.
> - **exemplar** : un lien, attaché à un point de métrique, vers une trace représentative.

## Le vocabulaire en clair

| Terme | Ce que ça veut dire |
| --- | --- |
| **microservices** | une application découpée en petits services indépendants qui s'appellent entre eux par le réseau |
| **trace_id** | l'identifiant unique d'une requête de bout en bout, partagé par tous ses spans |
| **span_id** et **parent** | l'identifiant d'une étape, et celui de l'étape qui l'a appelée ; c'est ce qui forme l'arbre |
| **attribut** | une information attachée à un span (`http.method=POST`, `db.statement`, `k8s.pod.name`) |
| **propagation** | le passage du trace_id d'un service à l'autre, dans les en-têtes des requêtes |
| **en-tête HTTP** | une information envoyée avec une requête HTTP, en plus de son contenu |
| **SDK** | la bibliothèque à ajouter dans l'application pour créer des spans et des métriques |
| **auto-instrumentation** | un agent qui crée les spans tout seul en interceptant les bibliothèques connues (client HTTP, pilote SQL), sans modifier le code |
| **gRPC** | un protocole d'appel entre services, utilisé notamment par OTLP |
| **receiver / processor / exporter** | les trois étapes du Collector : recevoir, transformer, envoyer |
| **échantillonnage** (sampling) | ne garder qu'une partie des traces pour limiter le coût |

## Comment ça marche : une trace de bout en bout

1. Une requête `POST /commandes` arrive sur la passerelle. Elle n'a pas de contexte de trace : la passerelle crée un **trace_id** et un premier **span**, qui démarre son chronomètre.
2. Avant d'appeler le service `commandes`, elle ajoute l'en-tête `traceparent: 00-<trace_id>-<span_id>-01`.
3. Le service `commandes` lit l'en-tête, crée son propre span en indiquant la passerelle comme **parent**, et ainsi de suite pour chaque appel qu'il fait (base de données, service de paiement) : chaque étape crée un span enfant et transmet l'en-tête.
4. À la fin de chaque étape, le SDK arrête le chronomètre et envoie le span terminé (en OTLP) au **Collector** le plus proche.
5. Le Collector reçoit des spans de tous les services, ajoute des attributs (nom du pod, namespace), décide de garder ou non la trace (échantillonnage) et l'envoie au stockage (Tempo, Jaeger).
6. Le stockage rassemble tous les spans qui partagent le même trace_id ; l'interface reconstruit l'arbre grâce aux liens parent-enfant et l'affiche sous forme de barres sur une ligne de temps.

Si un service oublie de transmettre l'en-tête, ses appels suivants démarrent une **nouvelle** trace : on voit alors deux traces séparées au lieu d'une.

## Comprendre : l'arbre d'une requête

<!-- schema:arbre -->
<figure class="diagram"><svg viewBox="0 0 680 280" role="img" aria-label="L&#x27;arbre d&#x27;une trace" style="--minw:560px"><defs><marker id="g6-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g6-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g6-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g6-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><text x="14" y="24" class="dg-ct" text-anchor="start">trace 4bf92f35… · POST /commandes · 1 840 ms au total</text><text x="14" y="63" class="dg-s" text-anchor="start" style="--d:0">api-gateway</text><g class="dg-box dg-pop" style="--d:0"><rect x="230.0" y="50" width="8.26086956521739" height="18" rx="3"/></g><text x="676" y="63" class="dg-s" text-anchor="end" style="--d:0">40 ms</text><text x="14" y="93" class="dg-s" text-anchor="start" style="--d:1">commandes</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="238.26086956521738" y="80" width="369.67391304347825" height="18" rx="3"/></g><text x="676" y="93" class="dg-s" text-anchor="end" style="--d:1">1 790 ms</text><text x="30" y="123" class="dg-s" text-anchor="start" style="--d:2">SELECT clients</text><g class="dg-box dg-pop" style="--d:2"><rect x="242.3913043478261" y="110" width="5.163043478260869" height="18" rx="3"/></g><text x="676" y="123" class="dg-s" text-anchor="end" style="--d:2">25 ms</text><text x="30" y="153" class="dg-s" text-anchor="start" style="--d:3">POST paiement</text><g class="dg-box dg-a dg-pop" style="--d:3"><rect x="250.65217391304347" y="140" width="330.4347826086956" height="18" rx="3"/></g><text x="676" y="153" class="dg-at" text-anchor="end" style="--d:3">1 600 ms</text><text x="46" y="183" class="dg-s" text-anchor="start" style="--d:4">appel Stripe</text><g class="dg-box dg-a dg-pop" style="--d:4"><rect x="252.7173913043478" y="170" width="326.304347826087" height="18" rx="3"/></g><text x="676" y="183" class="dg-at" text-anchor="end" style="--d:4">1 580 ms</text><text x="30" y="213" class="dg-s" text-anchor="start" style="--d:5">publish RabbitMQ</text><g class="dg-box dg-pop" style="--d:5"><rect x="585.2173913043479" y="200" width="3" height="18" rx="3"/></g><text x="676" y="213" class="dg-s" text-anchor="end" style="--d:5">12 ms</text><text x="14" y="243" class="dg-s" text-anchor="start" style="--d:6">notifications (async)</text><g class="dg-box dg-pop" style="--d:6"><rect x="597.6086956521739" y="230" width="12.391304347826086" height="18" rx="3"/></g><text x="676" y="243" class="dg-s" text-anchor="end" style="--d:6">60 ms</text><line x1="230" y1="44" x2="230" y2="262" class="dg-grid"/><text x="230" y="272" class="dg-s" text-anchor="middle">0</text><text x="610" y="272" class="dg-s" text-anchor="middle">1 840 ms</text></svg><figcaption>La trace montre d&#x27;un coup d&#x27;œil où part le temps : ici, l&#x27;appel au prestataire de paiement.</figcaption></figure>
<!-- /schema:arbre -->

En un coup d'œil : le paiement externe prend presque tout le temps, avec une nouvelle tentative. Aucun tableau de bord de métriques ne l'aurait montré aussi vite.

## OpenTelemetry : un standard pour tous les signaux

```
application
  ├─ auto-instrumentation (agent Java, Python, .NET, Node) : HTTP, SQL, gRPC, Kafka… sans code
  └─ SDK OTel : spans et métriques métier ajoutés à la main
        │ OTLP
        ▼
OTel Collector (agent sur le nœud) ──► OTel Collector (passerelle)
   receivers → processors → exporters
                 batch, k8sattributes, filtre, masquage, tail_sampling
        │
        ├──► Tempo / Jaeger / Elastic APM / Datadog   (traces)
        ├──► Prometheus / Mimir                        (métriques)
        └──► Loki / Elasticsearch                      (logs)
```

```yaml
# OpenTelemetry Collector (extrait)
receivers:
  otlp: { protocols: { grpc: {}, http: {} } }
processors:
  batch: {}
  k8sattributes: {}            # ajoute namespace, pod, deployment
  tail_sampling:
    policies:
      - { name: erreurs, type: status_code, status_code: { status_codes: [ERROR] } }
      - { name: lentes, type: latency, latency: { threshold_ms: 1000 } }
      - { name: le-reste, type: probabilistic, probabilistic: { sampling_percentage: 5 } }
exporters:
  otlp/tempo: { endpoint: tempo:4317, tls: { insecure: true } }
service:
  pipelines:
    traces: { receivers: [otlp], processors: [k8sattributes, tail_sampling, batch], exporters: [otlp/tempo] }
```

Sur Kubernetes, l'**OpenTelemetry Operator** déploie les Collectors et injecte l'auto-instrumentation dans les pods par une simple annotation.

## Relier les signaux

- Le **trace_id** dans chaque ligne de log permet d'ouvrir les logs d'une trace, et inversement.
- Les **exemplars** relient un point d'histogramme Prometheus (un pic de latence) à une trace concrète.
- Tempo peut **générer des métriques** RED à partir des spans (span metrics, service graph).
- Les mêmes **attributs de ressource** (`service.name`, `deployment.environment`, `k8s.namespace.name`) dans tous les signaux, selon les conventions sémantiques d'OpenTelemetry.

## Les pièges

| Piège | Effet | Parade |
| --- | --- | --- |
| contexte non propagé | traces coupées | instrumenter chaque saut (HTTP, files, gRPC), garder `traceparent` dans les proxys |
| tout garder | coût de stockage énorme | head sampling simple, tail sampling pour garder erreurs et lenteurs |
| attributs à forte cardinalité dans les métriques dérivées | explosion de séries | n'utiliser que des attributs bornés pour les span metrics |
| données sensibles dans les attributs | fuite (SQL avec paramètres, en-têtes) | masquage dans le SDK ou le Collector |
| horloges décalées | spans dans le mauvais ordre | NTP partout |

> **À retenir.** Une trace est un arbre de spans qui montre où passe le temps d'une requête ; le contexte se propage par l'en-tête W3C traceparent et doit traverser chaque saut, files de messages comprises. OpenTelemetry standardise l'instrumentation (SDK et auto-instrumentation), le protocole OTLP et le Collector (receivers, processors, exporters), neutre vis-à-vis du stockage. Tempo et Jaeger stockent les traces. Échantillonner (tail sampling pour garder erreurs et lenteurs) et relier les signaux par le trace_id, les exemplars et des attributs communs.
