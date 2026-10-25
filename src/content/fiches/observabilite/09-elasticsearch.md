---
title: 'La stack Elastic : Elasticsearch, Logstash, Beats'
chapter: 9
order: 1
duration: 13
tags:
- Observabilité
- Elasticsearch
- Elastic
- Logs
cards:
- q: Qu'est-ce qu'Elasticsearch ?
  a: Un moteur de **recherche et d'analyse distribué** construit sur Lucene. Il stocke des **documents JSON** dans des **index** et construit un **index inversé** de leurs champs, ce qui permet des recherches plein texte et des agrégations très rapides. Dans l'observabilité, il sert surtout aux logs, mais aussi aux métriques, aux traces (APM) et à la sécurité (SIEM).
- q: Que sont les shards et les replicas ?
  a: Un index est découpé en **shards primaires** (morceaux répartis sur les nœuds, qui permettent de paralléliser) ; chaque shard a des **replicas** (copies sur d'autres nœuds) pour la tolérance aux pannes et la lecture. Trop de petits shards coûtent cher en mémoire ; viser des shards de quelques dizaines de Go.
- q: Qu'est-ce que l'ILM et les data streams ?
  a: 'Un **data stream** est une suite d''index (`.ds-logs-app-…-000001`, `000002`…) derrière un nom unique, où l''on écrit en ajout seulement. L''**ILM** (Index Lifecycle Management) fait vivre ces index par phases : **hot** (écriture, disques rapides), **warm**, **cold**, **frozen** (moins cher, plus lent), puis **delete**, selon l''âge ou la taille.'
- q: Que signifient les états vert, jaune et rouge d'un cluster Elasticsearch ?
  a: '**Vert** : tous les shards primaires et replicas sont alloués. **Jaune** : tous les primaires sont là, mais des replicas manquent (redondance réduite, données servies). **Rouge** : au moins un shard primaire n''est pas alloué : une partie des données est indisponible.'
- q: Que font Logstash, Beats et Elastic Agent ?
  a: '**Beats** (Filebeat, Metricbeat…) sont de petits agents qui envoient fichiers et métriques. **Elastic Agent**, géré par **Fleet**, les remplace par un agent unique avec des intégrations prêtes. **Logstash** est un pipeline de traitement côté serveur (parser avec grok, enrichir, router) pour les transformations lourdes. Les **ingest pipelines** d''Elasticsearch font des transformations simples à l''arrivée.'
- q: Qu'est-ce qu'un mapping ?
  a: 'Le **schéma** d''un index : le type de chaque champ (`keyword` pour filtrer et agréger exactement, `text` pour la recherche plein texte, `date`, `long`, `ip`…). Un mapping dynamique mal maîtrisé crée des milliers de champs (**mapping explosion**) ; on fixe les mappings par **index templates** et on suit le schéma **ECS**.'
quiz:
- q: Le cluster passe en jaune après la perte d'un nœud sur trois. Que se passe-t-il ?
  options:
  - Des données sont perdues
  - Les primaires sont toujours là ; des replicas manquent, Elasticsearch les recrée sur les nœuds restants s'il a la place. La redondance est réduite le temps de revenir au vert
  - Le cluster s'arrête
  - Il faut tout réindexer
  answer: 1
  explain: Jaune = données servies mais moins protégées ; rouge = un primaire indisponible.
- q: Les disques des nœuds atteignent 95 % et les écritures sont refusées. Pourquoi ?
  options:
  - Bug
  - 'Elasticsearch applique des seuils de disque (watermarks) : au-delà du seuil « flood stage », les index passent en lecture seule pour protéger le cluster'
  - Le quota Kibana
  - Les shards sont trop petits
  answer: 1
  explain: Il faut libérer de la place (ILM, suppression) ou ajouter des nœuds ; depuis les versions récentes, le blocage se lève automatiquement quand l'espace revient.
level: intermédiaire
---

La **stack Elastic** (longtemps appelée ELK : Elasticsearch, Logstash, Kibana) est l'une des solutions de logs les plus répandues en entreprise, et la base de nombreux SIEM. Sa force est la **recherche plein texte** et l'**analyse** très rapides sur d'énormes volumes ; son coût est un cluster exigeant à dimensionner et à exploiter. Cette fiche couvre le stockage et la collecte ; la suivante, Kibana.

> **Les outils cités dans cette fiche.**
> - **Elasticsearch** : le moteur de recherche distribué d'Elastic, fondé sur **Lucene** (bibliothèque de recherche Java).
> - **OpenSearch** : le fork open source d'Elasticsearch et Kibana, mené par AWS depuis 2021.
> - **index inversé** : une table « mot → documents qui le contiennent », comme l'index d'un livre.
> - **Logstash** : le pipeline de traitement de données d'Elastic ; **grok** : son langage de parsing par motifs.
> - **Beats** (Filebeat, Metricbeat…) et **Elastic Agent** : les agents de collecte ; **Fleet** : la gestion centrale des agents.
> - **ILM** (Index Lifecycle Management) : la gestion du cycle de vie des index.
> - **ECS** (Elastic Common Schema) : le schéma commun de noms de champs (`host.name`, `http.response.status_code`…).
> - **SIEM** : un outil de détection d'incidents de sécurité à partir des logs.

## Le vocabulaire en clair

| Terme | Ce que ça veut dire |
| --- | --- |
| **document** | un enregistrement JSON (une ligne de log, un événement) stocké dans Elasticsearch |
| **champ** | une clé du document, comme `service.name` ou `http.response.status_code` |
| **index** | une collection de documents du même type, comme une table dans une base de données |
| **index inversé** | pour chaque mot, la liste des documents qui le contiennent : « timeout → documents 12, 845, 9031 » |
| **shard** | un morceau d'index ; un index de 100 Go peut être découpé en 2 shards de 50 Go sur deux nœuds |
| **replica** | une copie d'un shard sur un autre nœud, pour survivre à une panne et répartir les lectures |
| **nœud** | une instance d'Elasticsearch (un serveur ou un pod) ; plusieurs nœuds forment un **cluster** |
| **nœud master** | un nœud qui tient la carte du cluster (quels index, quels shards où) ; il en faut 3 pour le quorum |
| **mapping** | le schéma d'un index : le type de chaque champ |
| **text / keyword** | `text` est découpé en mots pour la recherche plein texte ; `keyword` est gardé tel quel pour filtrer exactement et compter |
| **rollover** | passer à un nouvel index quand le courant est trop gros ou trop vieux |
| **heap** | la mémoire réservée au programme Java d'Elasticsearch ; quand elle sature, tout ralentit |
| **watermark** | les seuils de remplissage disque (85 %, 90 %, 95 %) à partir desquels Elasticsearch arrête de placer des shards puis bloque les écritures |
| **snapshot** | une sauvegarde des index vers un stockage externe |
| **refresh** | l'opération (par défaut chaque seconde) qui rend les nouveaux documents visibles dans les recherches |

## Comment ça marche : indexer puis chercher

**À l'écriture** d'une ligne de log :

1. L'agent envoie le document JSON au cluster (à n'importe quel nœud, qui joue le rôle de coordinateur).
2. Le coordinateur détermine à quel **shard primaire** le document appartient et le lui transmet.
3. Le shard primaire analyse les champs : un champ `text` comme `message` est découpé en mots (« paiement », « refusé ») ajoutés à l'**index inversé** ; les champs `keyword` et les nombres sont rangés pour les filtres et les agrégations.
4. Il recopie le document vers ses **replicas**, puis confirme l'écriture.
5. Au prochain **refresh** (moins d'une seconde), le document devient cherchable.

**À la recherche** de `message : "timeout"` sur la dernière heure :

1. Le coordinateur envoie la requête à un exemplaire (primaire ou replica) de chaque shard concerné.
2. Chaque shard consulte son index inversé : le mot « timeout » donne directement la liste des documents, sans tout relire.
3. Le coordinateur rassemble les résultats, les trie et renvoie les meilleurs.

C'est l'inverse de Loki : beaucoup de travail et de place à l'écriture (indexer chaque mot), des recherches très rapides ensuite.

## Comprendre : documents, index, shards

```
document JSON ──► data stream « logs-commandes-prod »
                        │ (index de support, un nouveau à chaque rollover)
                        ▼
              .ds-logs-commandes-prod-2026.10.24-000042
                ├─ shard primaire 0 ──► replica 0 (autre nœud)
                └─ shard primaire 1 ──► replica 1 (autre nœud)

nœuds : master (état du cluster, ×3 pour le quorum) · data_hot · data_warm · data_cold · data_frozen · ingest · coordinating
```

Chaque champ `text` est découpé en termes et ajouté à l'index inversé ; chaque champ `keyword` permet les filtres exacts et les agrégations. C'est ce qui rend les recherches rapides, et ce qui rend le stockage plus cher que Loki.

## Collecter

| Composant | Rôle |
| --- | --- |
| Elastic Agent + Fleet | un agent par hôte, intégrations prêtes (système, nginx, Kubernetes, AWS…), géré depuis Kibana |
| Filebeat, Metricbeat | agents historiques, encore très utilisés |
| Logstash | parsing lourd (grok), enrichissement, routage vers plusieurs sorties |
| ingest pipelines | transformations à l'arrivée dans Elasticsearch (parser, renommer, géolocaliser) |
| Fluent Bit, Vector, OTel Collector | agents tiers, savent écrire dans Elasticsearch |

```ruby
# Logstash : parser un log nginx et l'envoyer dans un data stream
filter {
  grok { match => { "message" => "%{COMBINEDAPACHELOG}" } }
  date { match => [ "timestamp", "dd/MMM/yyyy:HH:mm:ss Z" ] }
}
output {
  elasticsearch { hosts => ["https://es:9200"] data_stream => "true" data_stream_dataset => "nginx" }
}
```

## Le cycle de vie des données

```json
PUT _ilm/policy/logs-30j
{ "policy": { "phases": {
  "hot":    { "actions": { "rollover": { "max_primary_shard_size": "50gb", "max_age": "1d" } } },
  "warm":   { "min_age": "3d",  "actions": { "forcemerge": { "max_num_segments": 1 } } },
  "cold":   { "min_age": "14d", "actions": {} },
  "delete": { "min_age": "30d", "actions": { "delete": {} } } } } }
```

Avec des **index templates** (mappings, nombre de shards, politique ILM) appliqués à chaque nouveau data stream, la rétention et les coûts deviennent automatiques. Les **snapshots** vers un dépôt objet (S3, Swift, GCS) servent de sauvegarde et alimentent les phases froides.

## Exploiter un cluster

```bash
curl -s https://es:9200/_cluster/health?pretty           # green / yellow / red
curl -s https://es:9200/_cat/nodes?v                     # nœuds, rôles, charge, heap
curl -s https://es:9200/_cat/indices?v&s=store.size:desc # plus gros index
curl -s https://es:9200/_cat/shards?v | grep UNASSIGNED  # shards non alloués
curl -s https://es:9200/_cluster/allocation/explain?pretty   # pourquoi un shard n'est pas alloué
```

| Problème | Piste |
| --- | --- |
| cluster jaune ou rouge | `_cluster/allocation/explain` : nœud perdu, disque plein, contraintes d'allocation |
| index en lecture seule | watermark disque atteint : libérer de la place, ILM, nouveaux nœuds |
| mémoire (heap) saturée | trop de shards, agrégations lourdes : moins de shards, plus gros |
| mapping explosion | champs dynamiques non maîtrisés : templates, `dynamic: false`, ECS |
| ingestion lente | trop de replicas pendant l'ingestion, refresh trop fréquent, nœuds ingest saturés |

Elastic propose aussi **Elastic Cloud** (géré) et **ECK** (Elastic Cloud on Kubernetes, un opérateur). Côté licences, Elasticsearch est disponible sous licence libre AGPL en plus des licences d'Elastic depuis 2024 ; OpenSearch reste une alternative Apache 2.0 très proche.

> **À retenir.** Elasticsearch stocke des documents JSON dans des index découpés en shards primaires et replicas, avec un index inversé qui rend la recherche et l'agrégation très rapides, au prix d'un stockage plus coûteux. Collecte par Elastic Agent (Fleet), Beats, Logstash ou agents tiers ; schéma ECS et index templates pour maîtriser les mappings. Data streams et ILM gèrent hot, warm, cold, frozen puis suppression. Santé : vert, jaune (replicas manquants), rouge (primaire manquant) ; `_cat` et `allocation/explain` pour diagnostiquer.
