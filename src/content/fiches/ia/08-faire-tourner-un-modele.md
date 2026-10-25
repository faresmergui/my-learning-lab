---
title: 'L''inférence : servir un modèle'
chapter: 8
order: 1
duration: 13
tags:
- IA
- Inférence
- GPU
- vLLM
cards:
- q: Combien de mémoire GPU faut-il pour charger un modèle ?
  a: 'En première approximation **nombre de paramètres × octets par paramètre** : un modèle de 8 milliards de paramètres demande environ 16 Go en FP16/BF16 (2 octets), 8 Go en 8 bits, 4 à 5 Go en 4 bits. Il faut **en plus** de la mémoire pour le **KV cache**, qui grossit avec la longueur du contexte et le nombre de requêtes simultanées.'
- q: Qu'est-ce que la quantification ?
  a: 'Stocker les poids avec moins de bits (8 ou 4 au lieu de 16) pour diviser la mémoire nécessaire et accélérer l''inférence, au prix d''une légère perte de qualité. Formats courants : GGUF (llama.cpp, Ollama), AWQ, GPTQ, FP8.'
- q: Qu'est-ce que le KV cache ?
  a: 'La mémoire où le modèle garde les calculs intermédiaires (clés et valeurs de l''attention) de tous les tokens déjà traités, pour ne pas les recalculer à chaque nouveau token. Il dépend de la longueur du contexte et du nombre de requêtes en parallèle : c''est souvent lui qui limite la capacité d''un serveur.'
- q: Différence entre Ollama et vLLM ?
  a: '**Ollama** (basé sur llama.cpp) est fait pour un poste ou un petit serveur : installation simple, modèles quantifiés, CPU ou GPU. **vLLM** est un serveur d''inférence de production pour GPU : **batching continu**, PagedAttention pour le KV cache, parallélisme sur plusieurs GPU, API compatible OpenAI. Autres serveurs de production : SGLang, TGI, NVIDIA Triton/TensorRT-LLM.'
- q: Quelles métriques suivre sur un serveur d'inférence ?
  a: Le **temps jusqu'au premier token** (TTFT), les **tokens par seconde** par requête et au total, la **latence** p50/p99, le nombre de requêtes en attente, l'**occupation du KV cache**, l'utilisation et la mémoire des GPU (DCGM exporter), et les erreurs (contexte trop long, mémoire épuisée).
- q: Qu'est-ce que le batching continu ?
  a: Le serveur traite plusieurs requêtes **en même temps** sur le GPU et ajoute ou retire des requêtes à chaque étape de génération, au lieu d'attendre qu'un lot soit fini. Le débit total est multiplié, au prix d'une latence individuelle un peu plus élevée.
quiz:
- q: Tu veux servir un modèle de 70 milliards de paramètres en BF16. Un GPU de 80 Go suffit-il ?
  options:
  - Oui, largement
  - 'Non : les poids seuls font environ 140 Go ; il faut plusieurs GPU (parallélisme tensoriel) ou une version quantifiée (environ 35 à 40 Go en 4 bits), plus la place du KV cache'
  - Oui, si on désactive le KV cache
  - Ça dépend du CPU
  answer: 1
  explain: '70 milliards × 2 octets ≈ 140 Go : on répartit sur deux GPU de 80 Go ou plus, ou on quantifie.'
- q: Le serveur vLLM répond bien à une requête, mais la latence explose à 50 utilisateurs simultanés. Quelle piste ?
  options:
  - Le CPU
  - 'Le KV cache et la concurrence : limiter la longueur maximale de contexte, ajouter des répliques (ou des GPU), et regarder les requêtes en attente'
  - Le DNS
  - Rien à faire
  answer: 1
  explain: Chaque requête active consomme du KV cache ; quand il est plein, les requêtes attendent.
level: intermédiaire
---

Héberger un modèle, c'est-à-dire faire de l'**inférence**, devient une demande courante pour les équipes plateforme : confidentialité des données, coûts à fort volume, besoin de modèles spécialisés. Pour un ingénieur cloud, c'est un service comme un autre, avec une différence de taille : la ressource rare et chère est la **mémoire GPU**. Cette fiche explique comment raisonner et quels outils utiliser.

> **Les outils cités dans cette fiche.**
> - **inférence** : utiliser un modèle déjà entraîné pour produire des réponses (par opposition à l'entraînement).
> - **VRAM** : la mémoire du GPU, où doivent tenir les poids et le KV cache.
> - **FP16 / BF16 / FP8** : des formats de nombres sur 16 ou 8 bits ; **quantification** : réduire le nombre de bits par poids.
> - **Ollama** et **llama.cpp** : des outils simples pour faire tourner des modèles sur un poste ou un petit serveur.
> - **vLLM**, **SGLang**, **TGI**, **Triton/TensorRT-LLM** : des serveurs d'inférence de production.
> - **Hugging Face** : la plateforme où sont publiés la plupart des modèles ouverts.
> - **DCGM exporter** : l'exporter Prometheus des métriques des GPU NVIDIA.
> - **latence** : le délai entre une demande et sa réponse.

## Comprendre : où va la mémoire GPU

```
VRAM d'un GPU de 80 Go
┌──────────────────────────────┬──────────────────────────┬────┐
│ poids du modèle              │ KV cache                 │ …  │
│ 8B en BF16 ≈ 16 Go           │ contextes × requêtes     │    │
│ 70B en 4 bits ≈ 35-40 Go     │ (souvent le vrai limite) │    │
└──────────────────────────────┴──────────────────────────┴────┘
```

| Modèle | BF16 (2 octets) | 8 bits | 4 bits |
| --- | --- | --- | --- |
| 8 milliards de paramètres | ~16 Go | ~8 Go | ~5 Go |
| 32 milliards | ~64 Go | ~32 Go | ~18 Go |
| 70 milliards | ~140 Go | ~70 Go | ~38 Go |

Ces chiffres ne comptent que les poids. Le **KV cache** s'y ajoute : plus les contextes sont longs et les utilisateurs nombreux, plus il en faut. Un modèle qui « tient » juste en mémoire n'aura de la place que pour très peu de requêtes simultanées.

## Deux phases, deux goulots

1. **Prefill** : le modèle lit tout le prompt d'un coup. C'est limité par la **puissance de calcul** et détermine le temps jusqu'au premier token.
2. **Decode** : il génère un token à la fois. C'est limité par la **bande passante mémoire** du GPU et détermine les tokens par seconde.

C'est pourquoi les serveurs de production regroupent les requêtes (**batching continu**) : le GPU lit les poids une fois pour plusieurs utilisateurs.

## Choisir son outil

| Outil | Pour quoi | Points forts |
| --- | --- | --- |
| Ollama / llama.cpp | poste, petit serveur, test | simple, modèles quantifiés GGUF, CPU possible |
| vLLM | production sur GPU | batching continu, PagedAttention, multi-GPU, API compatible OpenAI |
| SGLang | production, agents | très performant, réutilisation de préfixes |
| TGI (Hugging Face) | production | intégré à l'écosystème Hugging Face |
| Triton + TensorRT-LLM | performance maximale sur NVIDIA | optimisation poussée, plus complexe |

```bash
# sur un poste
ollama run qwen2.5-coder:7b

# un serveur de production
vllm serve meta-llama/Llama-3.1-8B-Instruct --max-model-len 16384 --gpu-memory-utilization 0.9
curl http://localhost:8000/v1/chat/completions -H 'Content-Type: application/json' \
  -d '{"model":"meta-llama/Llama-3.1-8B-Instruct","messages":[{"role":"user","content":"Bonjour"}]}'
```

L'**API compatible OpenAI** est devenue le standard de fait : la plupart des outils (clients, agents, passerelles) savent parler à un vLLM interne comme à un service externe.

## Exploiter un serveur d'inférence

- **Métriques** : TTFT, tokens/s, latence p99, requêtes en attente, occupation du KV cache (vLLM expose `/metrics` pour Prometheus), et pour le GPU : utilisation, mémoire, température, erreurs (DCGM).
- **Capacité** : se dimensionne en **requêtes simultanées** et en longueur de contexte, pas seulement en nombre d'utilisateurs ; limiter `max-model-len` à ce dont on a besoin.
- **Démarrage** : télécharger et charger des dizaines de Go prend du temps ; mettre les poids en cache local ou sur un volume partagé, prévoir des sondes de démarrage longues.
- **Mises à jour** : versionner le modèle comme une image (nom, révision), tester avant de basculer.
- **Licences** : chaque modèle ouvert a sa licence (Apache 2.0, licences communautaires avec conditions) ; la vérifier avant un usage en entreprise.

> **À retenir.** La ressource clé de l'inférence est la mémoire GPU : poids (paramètres × octets) plus KV cache (contexte × requêtes simultanées). La quantification (8 ou 4 bits) divise la mémoire au prix d'un peu de qualité. Prefill limité par le calcul, decode par la bande passante mémoire. Ollama pour un poste, vLLM (ou SGLang, TGI, Triton) en production, avec une API compatible OpenAI. Superviser TTFT, tokens/s, file d'attente, KV cache et GPU.
