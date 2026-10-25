---
title: IA, machine learning et LLM
chapter: 1
order: 1
duration: 11
tags:
- IA
- LLM
cards:
- q: Quelle différence entre IA, machine learning, deep learning et IA générative ?
  a: L'**IA** est le domaine général (faire faire à une machine des tâches « intelligentes »). Le **machine learning** apprend des règles à partir d'exemples au lieu de les programmer. Le **deep learning** est du machine learning avec des réseaux de neurones à nombreuses couches. L'**IA générative** est la partie du deep learning qui **produit** du contenu (texte, code, image, son).
- q: Qu'est-ce qu'un LLM ?
  a: 'Un **Large Language Model** : un réseau de neurones (architecture transformer) entraîné sur d''énormes quantités de texte et de code pour **prédire le token suivant**. À force, il a appris la grammaire, des faits, des langages de programmation et des façons de raisonner, qu''il ressort en générant du texte.'
- q: Qu'est-ce qu'un token ?
  a: 'Le morceau de texte que le modèle manipule : un mot court, un bout de mot, un signe. En moyenne environ **4 caractères en anglais**, un peu moins de mots par token en français et dans le code. Les limites de contexte, la vitesse et le prix se comptent en tokens.'
- q: Quelles sont les trois étapes de fabrication d'un assistant comme Claude ou ChatGPT ?
  a: '1) **Pré-entraînement** : prédire le token suivant sur un immense corpus (le modèle « sait » mais ne converse pas). 2) **Ajustement** (fine-tuning sur des exemples de dialogues) : il apprend à suivre des instructions. 3) **Alignement par retours** (RLHF et méthodes voisines) : il apprend à être utile, honnête et à refuser ce qui est dangereux.'
- q: Que sont les poids d'un modèle et que veut dire « modèle ouvert » ?
  a: 'Les **poids** (paramètres) sont les milliards de nombres appris pendant l''entraînement : c''est le modèle. Un modèle **à poids ouverts** (Llama, Mistral, Qwen, Gemma…) peut être téléchargé et exécuté sur sa propre infrastructure ; un modèle **fermé** (Claude, GPT, Gemini) s''utilise seulement par API.'
- q: Qu'est-ce qu'un embedding ?
  a: Une représentation d'un texte sous forme d'un **vecteur de nombres** tel que deux textes de sens proche ont des vecteurs proches. Il sert à chercher par le sens (recherche sémantique, RAG), à regrouper ou classer des documents.
quiz:
- q: Un LLM te donne avec assurance une option Terraform qui n'existe pas. Pourquoi est-ce possible ?
  options:
  - Le modèle est cassé
  - 'Il génère le texte le plus plausible, pas une vérité vérifiée : sans source ni outil, il peut produire une réponse crédible mais fausse (hallucination)'
  - Terraform a supprimé l'option
  - Il ment volontairement
  answer: 1
  explain: 'La plausibilité n''est pas la vérité : on vérifie dans la documentation, ou on donne au modèle un moyen de vérifier (doc fournie, `terraform validate`).'
- q: Ton entreprise interdit d'envoyer du code à un service externe. Quelle option reste possible ?
  options:
  - Aucune IA
  - Un modèle à poids ouverts hébergé en interne (sur vos GPU, par exemple sur Kubernetes ou OpenStack), ou une offre cloud avec engagement contractuel sur les données si la politique l'accepte
  - Copier le code dans un chat public
  - Désactiver le pare-feu
  answer: 1
  explain: C'est l'un des grands intérêts des modèles ouverts, au prix de l'infrastructure à opérer (voir les fiches inférence et GPU).
level: intermédiaire
---

L'IA générative est devenue en deux ans un outil de travail aussi courant que le terminal ou Git. Pour bien s'en servir, et pour la faire tourner sur sa propre infrastructure, il faut un modèle mental juste de ce qu'elle est : ni magie, ni simple « autocomplétion ». Cette fiche pose le vocabulaire que tout le module utilise.

> **Les outils cités dans cette fiche.**
> - **LLM** (Large Language Model) : un grand modèle de langage, le moteur des assistants comme Claude, ChatGPT ou Gemini.
> - **transformer** : l'architecture de réseau de neurones de presque tous les LLM, fondée sur le mécanisme d'**attention**.
> - **token** : l'unité de texte que le modèle lit et produit.
> - **embedding** : un vecteur de nombres qui représente le sens d'un texte.
> - **GPU** : le processeur graphique, indispensable pour entraîner et exécuter les modèles car il fait des millions de calculs en parallèle.
> - **RLHF** (Reinforcement Learning from Human Feedback) : un apprentissage à partir de préférences humaines pour rendre le modèle utile et sûr.
> - **YAML** : un format de fichier texte structuré par l'indentation, utilisé par Kubernetes, Ansible, GitLab CI…
> - **provider** : le plugin qui permet à Terraform de piloter une plateforme (AWS, OpenStack, Kubernetes).
> - **API** : interface qui permet à un programme d'en piloter un autre par des requêtes (souvent HTTP).
> - **manifest** : un fichier YAML qui décrit un objet Kubernetes.

## Comprendre : les poupées russes

```
Intelligence artificielle   (faire réaliser des tâches « intelligentes »)
 └─ Machine learning         (apprendre à partir d'exemples)
     └─ Deep learning        (réseaux de neurones profonds)
         └─ IA générative    (produire texte, code, images)
             └─ LLM          (le texte et le code)
```

Le machine learning « classique » est partout depuis longtemps en exploitation : détection d'anomalies sur des métriques, prévision de capacité, filtrage du spam. Ce qui a changé, c'est la **généralité** : un seul LLM sait écrire du YAML, expliquer un log, résumer un incident et traduire une documentation.

## Comment un LLM produit une réponse

1. Le texte est découpé en **tokens** (`kubectl get pods` fait 5 ou 6 tokens).
2. Le modèle calcule, pour chaque token possible, une **probabilité** d'être le suivant, en tenant compte de tout le contexte.
3. On en choisit un (le plus probable, ou un tirage selon la **température**), on l'ajoute, et on recommence.

Tout ce que fait un assistant, y compris « raisonner », vient de cette boucle. Les modèles récents produisent souvent un **raisonnement intermédiaire** avant de répondre, ce qui améliore nettement les tâches difficiles (débogage, calcul, plans), au prix de plus de tokens et de temps.

## Comment on fabrique un assistant

| Étape | Données | Résultat |
| --- | --- | --- |
| pré-entraînement | des milliers de milliards de tokens (web, livres, code) | un modèle qui « sait » mais ne fait que continuer du texte |
| ajustement aux instructions | des dialogues d'exemple | un modèle qui répond aux demandes |
| alignement | préférences humaines et principes | un assistant utile, honnête, qui refuse le dangereux |

Le modèle a une **date de coupure** : il ne connaît pas ce qui est sorti après son entraînement (une nouvelle version de Kubernetes, un nouveau provider). Il faut alors lui fournir l'information, ou lui donner un outil de recherche.

## Modèles fermés, modèles ouverts

| | Fermés (Claude, GPT, Gemini) | Ouverts (Llama, Mistral, Qwen, Gemma, DeepSeek…) |
| --- | --- | --- |
| accès | API ou application | téléchargement des poids |
| qualité | en général la meilleure | proche pour beaucoup de tâches, en retrait sur les plus dures |
| données | envoyées au fournisseur (selon le contrat) | restent chez toi |
| exploitation | aucune | GPU, serveur d'inférence, mises à jour : ton travail |
| coût | au token | au GPU (fixe), rentable à fort volume |

Pour un ingénieur cloud, les deux comptent : les modèles fermés comme outils de travail, les modèles ouverts comme **charge de travail à héberger**, de plus en plus demandée aux équipes plateforme.

## Ce que l'IA fait bien, et moins bien

- **Bien** : rédiger et transformer du texte et du code, expliquer, résumer, traduire d'un format à l'autre (bash vers Ansible, docker-compose vers manifests), proposer des pistes de diagnostic.
- **Moins bien** : les faits précis et récents sans source, le calcul exact sans outil, la connaissance de **ton** infrastructure (qu'il ne voit pas), et la responsabilité : c'est toi qui valides et qui appliques.

> **À retenir.** Un LLM est un réseau de neurones transformer qui prédit le token suivant ; pré-entraînement, ajustement et alignement en font un assistant. Il produit du plausible, pas du vérifié : il peut halluciner, et il ignore ce qui suit sa date de coupure et ce qui est propre à ton infrastructure. Modèles fermés par API, modèles ouverts à héberger soi-même. Les embeddings représentent le sens d'un texte et servent à la recherche sémantique.
