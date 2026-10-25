---
title: Synthèse IA
description: "LLM, prompts, IA pour le code et l'IaC, agents et MCP, RAG, AIOps, inférence et GPU, LLMOps, sécurité et feuille de route."
---

## Les bases

- IA ⊃ machine learning ⊃ deep learning ⊃ IA générative ⊃ **LLM**.
- Un LLM (transformer) **prédit le token suivant** ; pré-entraînement, ajustement aux instructions, alignement.
- **Token** ≈ 4 caractères en anglais ; contexte, prix et vitesse se comptent en tokens.
- **Embedding** : vecteur qui représente le sens d'un texte (recherche sémantique, RAG).
- Modèles **fermés** (API) vs **à poids ouverts** (hébergés chez soi).
- Le modèle est **sans état** : il ne sait que ce qui est dans le contexte de la requête.
- Il produit du **plausible**, pas du vérifié : hallucinations sur les détails, les versions récentes et ton infrastructure.

## Bien l'utiliser

| Élément du prompt | Exemple |
| --- | --- |
| contexte | versions, cloud, contraintes |
| tâche | précise, une à la fois |
| entrées | fichier, erreur, logs filtrés |
| format | fichier complet, tableau, JSON |
| critère de réussite | passe `terraform validate`, pas de droits root |

- Température basse pour le code et l'automatisation ; itérer ; demander des alternatives.
- Jamais de secrets, kubeconfig ni tfstate dans un outil externe.

## Code et IaC

- Complétion, chat, **agents de code** (avec un fichier d'instructions `CLAUDE.md` / `AGENTS.md`).
- Chaîne de garde-fous : fmt/lint → validate/dry-run → scanner (Checkov, Trivy) → politique (OPA, Kyverno) → **plan relu** → revue de MR.
- Pièges : droits trop larges, syntaxe d'une ancienne version, remplacements destructifs, options inventées.

## Agents, MCP et RAG

- Agent = LLM dans une boucle d'appels d'outils ; le modèle propose, **l'application exécute** avec ses droits.
- **MCP** branche des outils (GitLab, Kubernetes, Prometheus, outils internes) ; le serveur fixe ce que l'IA peut faire.
- Garde-fous : identité dédiée, **lecture par défaut**, écritures par MR ou approbation, isolation, journal, limites.
- **RAG** : chunks + embeddings + base vectorielle (pgvector, Qdrant) → recherche hybride → filtre par droits → réponse avec sources.
- RAG plutôt que fine-tuning pour des connaissances qui changent ; la qualité dépend des documents.

## Exploitation (AIOps)

- Tri et regroupement d'alertes, résumé, hypothèses avec leurs vérifications, runbook, messages, postmortem.
- Donner les **changements récents**, les logs filtrés, la topologie.
- L'astreinte décide ; seules des remédiations simples, réversibles et bornées s'automatisent.

## Inférence et GPU

| Modèle | BF16 | 4 bits |
| --- | --- | --- |
| 8 milliards de paramètres | ~16 Go | ~5 Go |
| 70 milliards | ~140 Go | ~38 Go |

- Mémoire GPU = poids + **KV cache** (contexte × requêtes simultanées).
- Ollama sur un poste ; **vLLM**, SGLang, TGI, Triton en production ; API compatible OpenAI.
- Métriques : TTFT, tokens/s, file d'attente, KV cache, DCGM.
- Kubernetes : **GPU Operator**, `nvidia.com/gpu`, taints, MIG / time-slicing / DRA, KServe.
- OpenStack : **PCI passthrough** (alias, PciPassthroughFilter, IOMMU), **vGPU** (`resources:VGPU`), Ironic.

## LLMOps

- **Passerelle LLM** : auth, quotas, masquage, journal, coûts, routage interne/externe.
- Versionner prompts, modèles, documents, outils ; **évaluer en CI** sur un jeu de questions types.
- Observer tokens, coûts, traces, qualité ; réduire les coûts par routage, contexte court, cache de prompt, quotas.

## Sécurité et gouvernance

- **Injection de prompt** : limiter les capacités, faire approuver, filtrer les sorties.
- Fuites : outils approuvés, masquage, droits dans le RAG.
- Chaîne d'approvisionnement : sources vérifiées, **safetensors**, serveurs MCP revus.
- Politique d'usage, registre des usages, RGPD, AI Act.

## Dans le métier

1. Toi : assistant approuvé, agent de code, briefer et vérifier.
2. L'équipe : pré-revue de MR, prompts partagés, politique d'usage.
3. L'assistant d'équipe : RAG sur les runbooks, MCP en lecture, bot d'astreinte.
4. La plateforme : passerelle, GPU, inférence.
- Mesurer avec DORA et MTTR ; garder la décision humaine sur la production.
