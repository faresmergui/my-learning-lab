---
title: 'RAG : brancher la documentation de l''équipe'
chapter: 6
order: 1
duration: 11
tags:
- IA
- RAG
- Embeddings
cards:
- q: Qu'est-ce que le RAG ?
  a: '**Retrieval-Augmented Generation** : avant de répondre, on **cherche** les passages pertinents dans une base de documents (runbooks, wiki, postmortems, doc d''architecture), on les met dans le contexte, et le modèle répond **en s''appuyant dessus**, idéalement en citant ses sources.'
- q: Quelles sont les étapes d'un pipeline RAG ?
  a: '**Ingestion** : découper les documents en morceaux (chunks), calculer leur embedding, les stocker dans une base vectorielle avec leurs métadonnées. **Requête** : calculer l''embedding de la question, chercher les morceaux les plus proches (souvent combiné à une recherche par mots-clés), éventuellement les reclasser, puis les donner au modèle.'
- q: Qu'est-ce qu'une base vectorielle ?
  a: 'Une base qui stocke des vecteurs (embeddings) et retrouve rapidement les plus proches d''un vecteur donné. Exemples : **pgvector** (extension PostgreSQL), **Qdrant**, **Weaviate**, **Milvus**, **OpenSearch** ou Elasticsearch avec recherche vectorielle.'
- q: RAG ou fine-tuning pour que l'IA connaisse nos procédures ?
  a: 'Le **RAG** dans presque tous les cas : la doc change souvent, on peut citer la source, contrôler les droits d''accès par document et mettre à jour sans réentraîner. Le **fine-tuning** sert plutôt à changer le style ou un comportement précis, pas à apprendre des faits qui évoluent.'
- q: Pourquoi la qualité des documents compte-t-elle plus que le modèle ?
  a: 'Parce que le RAG ne fait que **ressortir** ce qui est écrit : des runbooks obsolètes, contradictoires ou incomplets donnent des réponses obsolètes, contradictoires ou incomplètes. Dater, nettoyer et structurer la documentation est souvent le vrai chantier.'
quiz:
- q: Le bot interne répond à un stagiaire avec le contenu d'une procédure réservée à l'équipe sécurité. Quel est le défaut ?
  options:
  - Le modèle est trop intelligent
  - 'Les droits d''accès des documents ne sont pas appliqués à la recherche : il faut filtrer les morceaux selon les permissions de l''utilisateur'
  - La température est trop haute
  - Il faut un autre modèle d'embeddings
  answer: 1
  explain: Un RAG doit respecter les permissions de la source (ACL par document ou par espace) au moment de la recherche.
- q: Le bot répond avec une procédure de redémarrage d'il y a trois ans, devenue fausse. Que corriger en priorité ?
  options:
  - Le modèle
  - 'La base documentaire : retirer ou marquer les documents obsolètes, privilégier les récents (métadonnée de date), et afficher la source et sa date dans la réponse'
  - La base vectorielle
  - Rien
  answer: 1
  explain: Le RAG est aussi bon que la documentation qu'il indexe.
level: intermédiaire
---

Un assistant généraliste ne connaît ni ton architecture, ni tes runbooks, ni les postmortems de l'équipe. Le **RAG** comble ce manque : il va chercher les bons passages dans votre documentation et les donne au modèle avant qu'il réponde. C'est la façon la plus répandue de construire un « assistant de l'équipe plateforme » ou un bot d'astreinte.

> **Les outils cités dans cette fiche.**
> - **RAG** (Retrieval-Augmented Generation) : la génération appuyée sur une recherche de documents.
> - **embedding** : un vecteur de nombres qui représente le sens d'un texte (voir la première fiche du module).
> - **chunk** : un morceau de document (quelques paragraphes) indexé séparément.
> - **base vectorielle** : une base qui retrouve les vecteurs les plus proches (pgvector, Qdrant, Weaviate, Milvus, OpenSearch).
> - **reranker** : un modèle qui reclasse les résultats de recherche par pertinence.
> - **fine-tuning** : réentraîner légèrement un modèle sur ses propres exemples.
> - **webhook** : un appel HTTP automatique envoyé par un outil quand un événement se produit.
> - **API** : interface qui permet à un programme d'en piloter un autre par des requêtes (souvent HTTP).
> - **conteneur** : un processus isolé qui embarque son application et ses dépendances, lancé à partir d'une image (voir le module Docker).
> - **SQL** : le langage de requête des bases de données relationnelles (PostgreSQL, MySQL).

## Comprendre : chercher puis répondre

<!-- schema:rag -->
<figure class="diagram"><svg viewBox="0 0 680 330" role="img" aria-label="Le RAG : chercher puis répondre" style="--minw:560px"><defs><marker id="g9-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g9-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g9-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g9-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><rect x="14" y="14" width="652" height="98" rx="12" class="dg-zone "/><text x="26" y="32" class="dg-zl" text-anchor="start">ingestion · régulière</text><g class="dg-box dg-pop" style="--d:0"><rect x="30" y="40" width="140" height="56" rx="9"/></g><text x="100.0" y="58.0" class="dg-t" text-anchor="middle" style="--d:0">documents</text><text x="100.0" y="76.0" class="dg-s" text-anchor="middle" style="--d:0"><tspan x="100.0" dy="0">runbooks, wiki,</tspan><tspan x="100.0" dy="14">postmortems</tspan></text><g class="dg-box dg-pop" style="--d:1"><rect x="190" y="40" width="140" height="56" rx="9"/></g><text x="260.0" y="65.0" class="dg-t" text-anchor="middle" style="--d:1">chunks</text><text x="260.0" y="83.0" class="dg-s" text-anchor="middle" style="--d:1">découpage</text><path d="M170 68 L188 68" class="dg-l c" marker-end="url(#g9-c)"/><g class="dg-box dg-pop" style="--d:2"><rect x="350" y="40" width="140" height="56" rx="9"/></g><text x="420.0" y="65.0" class="dg-t" text-anchor="middle" style="--d:2">embeddings</text><text x="420.0" y="83.0" class="dg-s" text-anchor="middle" style="--d:2">texte → vecteurs</text><path d="M330 68 L348 68" class="dg-l c" marker-end="url(#g9-c)"/><g class="dg-box dg-c dg-pop" style="--d:3"><rect x="510" y="40" width="140" height="56" rx="9"/></g><text x="580.0" y="65.0" class="dg-t" text-anchor="middle" style="--d:3">base vectorielle</text><text x="580.0" y="83.0" class="dg-s" text-anchor="middle" style="--d:3">+ titre, date, droits</text><path d="M490 68 L508 68" class="dg-l c" marker-end="url(#g9-c)"/><rect x="14" y="132" width="652" height="186" rx="12" class="dg-zone dg-zc"/><text x="26" y="150" class="dg-zl" text-anchor="start">requête</text><g class="dg-box dg-pop" style="--d:4"><rect x="30" y="162" width="150" height="60" rx="9"/></g><text x="105.0" y="182.0" class="dg-t" text-anchor="middle" style="--d:4">question</text><text x="105.0" y="200.0" class="dg-s" text-anchor="middle" style="--d:4"><tspan x="105.0" dy="0">« comment purger</tspan><tspan x="105.0" dy="14">la file RabbitMQ ? »</tspan></text><g class="dg-box dg-c dg-pop" style="--d:5"><rect x="210" y="162" width="170" height="60" rx="9"/></g><text x="295.0" y="182.0" class="dg-t" text-anchor="middle" style="--d:5">recherche</text><text x="295.0" y="200.0" class="dg-s" text-anchor="middle" style="--d:5"><tspan x="295.0" dy="0">passages proches</tspan><tspan x="295.0" dy="14">filtrés par droits</tspan></text><g class="dg-box dg-pop" style="--d:6"><rect x="410" y="162" width="240" height="60" rx="9"/></g><text x="530.0" y="182.0" class="dg-t" text-anchor="middle" style="--d:6">prompt</text><text x="530.0" y="200.0" class="dg-s" text-anchor="middle" style="--d:6"><tspan x="530.0" dy="0">consigne + 5 passages</tspan><tspan x="530.0" dy="14">sourcés + question</tspan></text><path d="M180 192 L208 192" class="dg-l c" marker-end="url(#g9-c)"/><path d="M380 192 L408 192" class="dg-l c" marker-end="url(#g9-c)"/><path d="M580 96 L580 122 L295 122 L295 160" class="dg-l c" marker-end="url(#g9-c)"/><g class="dg-box dg-ok dg-pop" style="--d:7"><rect x="210" y="248" width="440" height="54" rx="9"/></g><text x="430.0" y="272.0" class="dg-t" text-anchor="middle" style="--d:7">réponse avec ses sources</text><text x="430.0" y="290.0" class="dg-s" text-anchor="middle" style="--d:7">« D&#x27;après le runbook rabbitmq-ops (mars) : … »</text><path d="M530 222 L530 246" class="dg-l ok" marker-end="url(#g9-ok)"/></svg><figcaption>Le modèle ne répond qu&#x27;à partir des passages retrouvés, et cite sa source : on peut vérifier.</figcaption></figure>
<!-- /schema:rag -->

La recherche par le sens retrouve « vider la queue » même si le document dit « purger les messages » ; la recherche par **mots-clés** reste meilleure pour les noms exacts (un nom de service, un code d'erreur) : les bons systèmes combinent les deux (recherche **hybride**).

## Les choix qui comptent

| Choix | Bonne pratique |
| --- | --- |
| découpage | suivre la structure (titres, sections), quelques centaines de tokens, garder le titre du document dans chaque chunk |
| métadonnées | source, date, équipe, environnement, droits d'accès |
| recherche | hybride (sens + mots-clés), puis reclassement |
| nombre de passages | quelques passages pertinents plutôt que beaucoup |
| réponse | citer la source et sa date, dire « je ne trouve pas » plutôt qu'inventer |
| mise à jour | réindexation automatique quand un document change (webhook, tâche planifiée) |

## Pour une équipe DevOps

- **Runbooks et procédures d'astreinte** : « que faire quand l'alerte X se déclenche ».
- **Postmortems** : « est-ce qu'on a déjà eu ce symptôme ? ».
- **Documentation d'architecture** : « quel service parle à quelle base ».
- **Dépôts de code et d'IaC** : « où est défini le security group de l'API ».
- **Tickets résolus** : la mémoire de l'équipe.

Techniquement, un premier RAG tient dans **PostgreSQL avec pgvector**, un modèle d'embeddings (hébergé ou par API) et un LLM : rien d'exotique pour une équipe qui exploite déjà des bases et des conteneurs.

## Les limites

- **Garbage in, garbage out** : une documentation obsolète produit des réponses obsolètes. Dater, archiver, désigner des propriétaires.
- **Les droits** : un utilisateur ne doit retrouver que ce qu'il pourrait lire dans la source.
- **Les questions transverses** (« combien d'incidents réseau cette année ? ») ne se résolvent pas par quelques passages : il faut un outil qui interroge les données (SQL, API du gestionnaire de tickets), donc un agent.
- **L'évaluation** : garder une liste de questions types avec les bonnes réponses pour vérifier que les changements (découpage, modèle) améliorent vraiment les choses.

> **À retenir.** Le RAG cherche les passages utiles dans votre documentation et les donne au modèle, qui répond en citant ses sources. Ingestion (chunks, embeddings, métadonnées, base vectorielle) puis requête (recherche hybride, filtre par droits, reclassement). Préféré au fine-tuning pour des connaissances qui changent. Sa qualité dépend surtout de celle des documents : dater, nettoyer, respecter les droits, évaluer avec des questions types.
