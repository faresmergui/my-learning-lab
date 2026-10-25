---
title: 'Les logs : structurer, collecter, conserver'
chapter: 7
order: 1
duration: 11
tags:
- Observabilité
- Logs
- Fluent Bit
- Vector
cards:
- q: Pourquoi écrire des logs structurés ?
  a: Parce qu'un log en **JSON** (ou logfmt) avec des champs nommés (`level`, `service`, `trace_id`, `user`, `duration_ms`) se filtre, s'agrège et se relie aux traces **sans expression régulière fragile**. Un log texte libre oblige à parser, et casse dès qu'on change le message.
- q: Quels sont les principaux agents de collecte de logs ?
  a: '**Fluent Bit** (léger, en C, très répandu sur Kubernetes), **Fluentd** (plus lourd, en Ruby, nombreux plugins), **Vector** (en Rust, performant, avec un langage de transformation, VRL), **Grafana Alloy** (successeur de Promtail pour Loki), **Filebeat** et **Elastic Agent** (pour Elasticsearch), **Logstash** (traitement lourd côté serveur), et l''**OpenTelemetry Collector**.'
- q: Où les conteneurs doivent-ils écrire leurs logs ?
  a: Sur la **sortie standard et la sortie d'erreur** (stdout/stderr). Le runtime les écrit dans `/var/log/containers/` (ou `/var/log/pods/`) sur le nœud, où un agent en **DaemonSet** les lit, ajoute les métadonnées Kubernetes (namespace, pod, labels) et les envoie.
- q: Quels niveaux de log utiliser ?
  a: '`ERROR` (une opération a échoué, à regarder), `WARN` (anormal mais géré), `INFO` (événements métier et de cycle de vie, avec parcimonie), `DEBUG` (détail pour le développement, désactivé en production par défaut). Trop de logs `INFO` coûte cher et noie l''essentiel.'
- q: Que ne jamais écrire dans un log ?
  a: 'Des **secrets** (mots de passe, jetons, en-têtes Authorization, clés), des **données personnelles** inutiles ou des numéros de carte : les logs sont copiés, indexés, conservés et lus par beaucoup de monde. Les masquer à la source, ou au plus tard dans l''agent de collecte.'
quiz:
- q: La facture du stockage de logs a triplé ce mois-ci. Par quoi commencer ?
  options:
  - Supprimer tous les logs
  - Identifier les plus gros émetteurs (par service et par niveau), baisser les logs DEBUG/INFO bavards, filtrer ou échantillonner dans l'agent, et adapter la rétention par type de log
  - Augmenter le budget
  - Passer en texte libre
  answer: 1
  explain: Quelques services bavards font souvent l'essentiel du volume ; le filtrage à la source est le levier le plus efficace.
- q: Dans une pile d'appels Java, chaque ligne arrive comme un log séparé. Que configurer ?
  options:
  - Rien
  - Le regroupement multi-lignes dans l'agent (parser multiline de Fluent Bit, Vector ou Alloy), ou mieux, un logger qui écrit en JSON sur une ligne
  - Augmenter la rétention
  - Changer de langage
  answer: 1
  explain: Un log JSON sur une ligne évite tout le problème du multi-lignes.
level: intermédiaire
---

Les logs racontent le détail de ce qui s'est passé : l'erreur exacte, la requête concernée, l'utilisateur, la trace. Ce sont aussi les données les plus volumineuses et les plus coûteuses de l'observabilité. Avant de choisir entre Loki, Elasticsearch ou Datadog, il faut maîtriser trois choses communes à tous : écrire de **bons logs**, les **collecter** proprement et décider combien de temps les **garder**.

> **Les outils cités dans cette fiche.**
> - **log structuré** : un log écrit en champs nommés (JSON, logfmt) plutôt qu'en phrase libre.
> - **Fluent Bit** et **Fluentd** : des agents de collecte de logs du projet Fluent (CNCF).
> - **Vector** : un agent et routeur de données d'observabilité ; **VRL** : son langage de transformation.
> - **Grafana Alloy** : l'agent de Grafana (logs, métriques, traces), qui remplace Promtail.
> - **Filebeat**, **Elastic Agent** et **Logstash** : la collecte et le traitement côté Elastic.
> - **DaemonSet** : un objet Kubernetes qui lance un pod sur chaque nœud (voir le module Kubernetes).
> - **journald** : le journal de systemd sur Linux (voir la fiche Linux sur les logs).

## Le vocabulaire en clair

| Terme | Ce que ça veut dire |
| --- | --- |
| **log** (journal) | une ligne écrite par un programme pour dire ce qu'il fait ou ce qui s'est mal passé |
| **stdout / stderr** | la sortie standard et la sortie d'erreur d'un programme : ce qu'il affiche dans le terminal |
| **JSON** | un format texte structuré en paires `"clé": valeur`, lisible par les humains et les programmes |
| **logfmt** | un format plus simple : `level=error service=api msg="paiement refusé"` |
| **parser** | découper une ligne de log en champs nommés (date, niveau, message…) |
| **enrichir** | ajouter des informations à un log (nom du pod, namespace, nom de l'hôte) |
| **multi-lignes** | un log qui s'étale sur plusieurs lignes (pile d'appels Java) et qu'il faut recoller en un seul événement |
| **agent** | un petit programme installé sur chaque machine qui lit les logs et les envoie |
| **tampon** (buffer) | une zone où l'agent garde les logs quand la destination ne répond pas, pour ne pas les perdre |
| **Kafka** | une plateforme de file de messages souvent placée entre les agents et le stockage pour absorber les pics |
| **index** | une structure qui permet de retrouver vite les logs selon un champ (comme l'index d'un livre) |
| **rétention** | la durée de conservation des logs avant suppression |

## Comment ça marche : le voyage d'une ligne de log sur Kubernetes

1. L'application écrit `{"level":"error","msg":"paiement refusé"}` sur sa **sortie standard**.
2. Le **runtime de conteneurs** (containerd) capture cette sortie et l'ajoute à un fichier sur le nœud, `/var/log/pods/<namespace>_<pod>_<id>/<conteneur>/0.log`, avec la date et le flux (stdout ou stderr).
3. L'**agent** (Fluent Bit, en DaemonSet donc présent sur chaque nœud) suit ce fichier comme un `tail -f` et retient où il en est, pour reprendre au bon endroit après un redémarrage.
4. Il **parse** la ligne (décode le JSON), l'**enrichit** en demandant à l'API Kubernetes le namespace, les labels et le nœud du pod, **filtre** ce qui est inutile et **masque** les données sensibles.
5. Il regroupe les lignes en lots et les **envoie** au stockage (Loki, Elasticsearch, Datadog). Si la destination ne répond pas, il les garde dans son **tampon** et réessaie.
6. Le stockage les range et les rend cherchables ; tu les retrouves dans Grafana ou Kibana quelques secondes plus tard.

Quand le pod est supprimé, ses fichiers de logs disparaissent du nœud : seuls les logs déjà envoyés restent. C'est pourquoi la collecte centralisée est indispensable sur Kubernetes.

## Comprendre : la chaîne d'un log

<!-- schema:chaine -->
<figure class="diagram"><svg viewBox="0 0 680 212" role="img" aria-label="La chaîne d&#x27;un log" style="--minw:560px"><defs><marker id="g4-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g4-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g4-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g4-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-pop" style="--d:0"><rect x="14" y="30" width="120" height="70" rx="9"/></g><text x="74.0" y="55.0" class="dg-t" text-anchor="middle" style="--d:0">application</text><text x="74.0" y="73.0" class="dg-s" text-anchor="middle" style="--d:0"><tspan x="74.0" dy="0">stdout, fichier,</tspan><tspan x="74.0" dy="14">journald</tspan></text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="147" y="30" width="120" height="70" rx="9"/></g><text x="207.0" y="55.0" class="dg-t" text-anchor="middle" style="--d:1">agent</text><text x="207.0" y="73.0" class="dg-s" text-anchor="middle" style="--d:1"><tspan x="207.0" dy="0">lire, parser,</tspan><tspan x="207.0" dy="14">enrichir, masquer</tspan></text><path d="M135 65 L146 65" class="dg-l c" marker-end="url(#g4-c)"/><text x="207" y="136" class="dg-s" text-anchor="middle" style="--d:1"><tspan x="207" dy="0">Fluent Bit</tspan><tspan x="207" dy="14">Vector · Alloy</tspan><tspan x="207" dy="14">Filebeat</tspan><tspan x="207" dy="14">OTel Collector</tspan></text><g class="dg-box dg-ghost dg-pop" style="--d:2"><rect x="280" y="30" width="120" height="70" rx="9"/></g><text x="340.0" y="62.0" class="dg-t" text-anchor="middle" style="--d:2">tampon</text><text x="340.0" y="80.0" class="dg-s" text-anchor="middle" style="--d:2">optionnel</text><path d="M268 65 L279 65" class="dg-l c" marker-end="url(#g4-c)"/><text x="340" y="136" class="dg-s" text-anchor="middle" style="--d:2"><tspan x="340" dy="0">Kafka</tspan><tspan x="340" dy="14">Logstash</tspan></text><g class="dg-box dg-c dg-pop" style="--d:3"><rect x="413" y="30" width="120" height="70" rx="9"/></g><text x="473.0" y="62.0" class="dg-t" text-anchor="middle" style="--d:3">stockage</text><text x="473.0" y="80.0" class="dg-s" text-anchor="middle" style="--d:3">indexé</text><path d="M401 65 L412 65" class="dg-l c" marker-end="url(#g4-c)"/><text x="473" y="136" class="dg-s" text-anchor="middle" style="--d:3"><tspan x="473" dy="0">Loki</tspan><tspan x="473" dy="14">Elasticsearch</tspan><tspan x="473" dy="14">Datadog · Splunk</tspan></text><g class="dg-box dg-pop" style="--d:4"><rect x="546" y="30" width="120" height="70" rx="9"/></g><text x="606.0" y="62.0" class="dg-t" text-anchor="middle" style="--d:4">recherche</text><text x="606.0" y="80.0" class="dg-s" text-anchor="middle" style="--d:4">tableaux de bord</text><path d="M534 65 L545 65" class="dg-l c" marker-end="url(#g4-c)"/><text x="606" y="136" class="dg-s" text-anchor="middle" style="--d:4"><tspan x="606" dy="0">Grafana</tspan><tspan x="606" dy="14">Kibana</tspan><tspan x="606" dy="14">Datadog</tspan></text><text x="14" y="124" class="dg-zl" text-anchor="start">outils</text></svg><figcaption>Masquer les données sensibles se fait dans l&#x27;agent, avant que le log ne soit stocké.</figcaption></figure>
<!-- /schema:chaine -->

## Écrire de bons logs

```json
{"ts":"2026-10-24T08:12:03.512Z","level":"error","service":"commandes","env":"prod",
 "msg":"paiement refusé","order_id":"A-88123","provider":"stripe","http_status":502,
 "duration_ms":3012,"trace_id":"4bf92f3577b34da6a3ce929d0e0e4736"}
```

- **Un événement par ligne**, en JSON (ou logfmt).
- Des **champs stables** : `level`, `service`, `env`, `msg`, plus les identifiants utiles (commande, requête).
- Le **trace_id** pour relier le log à la trace (voir la fiche traces).
- Des **niveaux** respectés, `DEBUG` coupé en production.
- **Aucun secret** ni donnée personnelle superflue.

## Collecter sur Kubernetes

```yaml
# Fluent Bit (extrait, format YAML)
pipeline:
  inputs:
    - name: tail
      path: /var/log/containers/*.log
      multiline.parser: docker, cri
      tag: kube.*
  filters:
    - name: kubernetes            # ajoute namespace, pod, labels, annotations
      match: kube.*
      merge_log: on               # décode le JSON du message
    - name: grep
      match: kube.*
      exclude: log ^.*healthz.*$  # jeter le bruit des sondes
  outputs:
    - name: loki
      match: kube.*
      host: loki-gateway
      labels: namespace=$kubernetes['namespace_name'], app=$kubernetes['labels']['app']
```

| Agent | Points forts |
| --- | --- |
| Fluent Bit | très léger, standard sur Kubernetes, sorties vers tout |
| Vector | performant, transformations puissantes (VRL), routage |
| Grafana Alloy | logs, métriques et traces dans un agent, natif pour Loki |
| Filebeat / Elastic Agent | intégration Elastic, modules prêts (nginx, système) |
| OpenTelemetry Collector | standard ouvert, un agent pour tous les signaux |

## Volume, coût et rétention

- **Mesurer** le volume par service et par niveau : quelques services bavards font souvent l'essentiel.
- **Filtrer à la source** : sondes de santé, logs d'accès répétitifs, `DEBUG`.
- **Échantillonner** les logs très répétitifs (garder 1 sur 10 des succès, tous les échecs).
- **Rétention par classe** : 7 à 30 jours pour les logs applicatifs, plus longtemps pour l'**audit** et la sécurité (exigences légales), archivage froid peu coûteux (stockage objet).
- **Métriques plutôt que logs** pour compter : un compteur d'erreurs coûte bien moins que des millions de lignes indexées.

> **À retenir.** Des logs structurés en JSON, un événement par ligne, avec des champs stables, un niveau et le trace_id, sans secret. Les conteneurs écrivent sur stdout ; un agent en DaemonSet (Fluent Bit, Vector, Alloy, Filebeat, OTel Collector) lit, enrichit avec les métadonnées Kubernetes, filtre, masque et envoie. Les logs sont le signal le plus coûteux : mesurer le volume, filtrer à la source, échantillonner, fixer une rétention par classe, et compter avec des métriques.
