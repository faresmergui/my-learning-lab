---
title: Des GPU dans Kubernetes et OpenStack
chapter: 9
order: 1
duration: 13
tags:
- IA
- GPU
- Kubernetes
- OpenStack
cards:
- q: Comment un pod Kubernetes obtient-il un GPU ?
  a: Un **device plugin** (celui de NVIDIA, installé par le **GPU Operator**) annonce les GPU du nœud comme une ressource étendue `nvidia.com/gpu`. Le pod la demande dans `resources.limits` ; le scheduler le place sur un nœud qui en a, et le conteneur voit le GPU grâce au **NVIDIA Container Toolkit**.
- q: Que fait le NVIDIA GPU Operator ?
  a: 'Il installe et gère automatiquement tout ce qu''il faut sur les nœuds GPU : pilote NVIDIA, Container Toolkit, device plugin, **DCGM exporter** (métriques), **GPU Feature Discovery** (labels du modèle de GPU), et la configuration MIG ou du time-slicing.'
- q: Comment partager un GPU entre plusieurs pods ?
  a: '**MIG** (Multi-Instance GPU, sur A100, H100…) découpe le GPU en instances isolées matériellement, chacune avec sa mémoire. Le **time-slicing** fait alterner plusieurs pods sur le même GPU sans isolation de mémoire. Les pilotes **DRA** (Dynamic Resource Allocation) de Kubernetes offrent une allocation plus fine et plus récente.'
- q: Comment donner un GPU à une instance OpenStack ?
  a: 'Trois façons : le **PCI passthrough** (le GPU entier est donné à la VM, via un alias PCI dans nova.conf et une flavor `pci_passthrough:alias`), le **vGPU** (le GPU est découpé par le pilote NVIDIA vGPU, sous licence, et exposé comme ressource `VGPU` dans Placement), ou des instances **MIG** exposées en vGPU. Ironic permet aussi des serveurs GPU entiers en bare metal.'
- q: Pourquoi teinter (taint) les nœuds GPU ?
  a: 'Pour que seuls les pods qui demandent un GPU (et ont la tolérance) y aillent : sinon des pods ordinaires occupent CPU et mémoire de ces nœuds très chers et empêchent les workloads GPU d''y être placés.'
- q: Qu'est-ce que KServe ?
  a: 'Une plateforme Kubernetes de **service de modèles** : une ressource `InferenceService` décrit le modèle et le serveur (vLLM, Triton, Hugging Face…), et KServe gère le déploiement, l''autoscaling (jusqu''à zéro avec Knative), les versions et le routage du trafic.'
quiz:
- q: 'Un pod qui demande `nvidia.com/gpu: 1` reste en Pending avec `Insufficient nvidia.com/gpu`. Le nœud a pourtant un GPU. Que vérifies-tu ?'
  options:
  - Le DNS
  - 'Que le device plugin (GPU Operator) tourne sur ce nœud et annonce la ressource (`kubectl describe node` : Capacity nvidia.com/gpu), que le pilote est chargé, et qu''aucun autre pod n''occupe déjà le GPU'
  - Le quota CPU
  - L'image du pod
  answer: 1
  explain: Sans device plugin, Kubernetes ne sait pas que le GPU existe.
- q: Sur OpenStack, une instance GPU échoue avec `No valid host` alors qu'un compute a un GPU libre. Piste ?
  options:
  - Glance
  - 'La flavor ne correspond pas : alias PCI (passthrough) ou ressource VGPU absente de Placement sur ce compute, filtre PciPassthroughFilter non activé, ou IOMMU désactivé sur l''hôte'
  - Le quota de volumes
  - Keystone
  answer: 1
  explain: Le placement GPU dépend de la configuration PCI/vGPU de Nova, de Placement et de l'hôte (IOMMU, pilote vfio).
level: intermédiaire
---

Faire tourner de l'IA sur sa propre infrastructure, c'est d'abord savoir **exposer des GPU** aux workloads, les partager et les superviser. Pour quelqu'un qui exploite Kubernetes et OpenStack au quotidien, cette fiche relie les briques déjà connues (scheduler, ressources, Placement, flavors) à ce qu'il faut ajouter pour les GPU.

> **Les outils cités dans cette fiche.**
> - **device plugin** : le composant Kubernetes qui annonce un matériel spécial (GPU, carte réseau) au kubelet.
> - **NVIDIA GPU Operator** : l'opérateur qui installe pilotes et composants GPU sur les nœuds Kubernetes.
> - **NVIDIA Container Toolkit** : ce qui permet à un conteneur d'accéder au GPU de l'hôte.
> - **MIG** (Multi-Instance GPU) : le découpage matériel d'un GPU en plusieurs instances isolées.
> - **DRA** (Dynamic Resource Allocation) : l'API Kubernetes récente pour allouer finement des matériels.
> - **KServe** : la plateforme Kubernetes de service de modèles ; **Knative** : la couche serverless qui lui permet de descendre à zéro réplica.
> - **PCI passthrough** : donner un périphérique physique entier à une VM ; **vGPU** : le partage d'un GPU entre VM par le pilote NVIDIA ; **IOMMU** : la fonction du processeur qui rend le passthrough possible.
> - **scheduler** : le composant qui décide où placer une charge de travail (sur quel nœud ou quel hôte).
> - **pod** : la plus petite unité de Kubernetes : un ou plusieurs conteneurs qui partagent réseau et volumes.
> - **namespace** : un espace de noms : dans Kubernetes, une partition du cluster ; sous Linux, une isolation du noyau.
> - **cache** : une copie rapide de données souvent demandées, pour éviter de les recalculer ou de les relire.
> - **pipeline** : une suite d'étapes automatiques (construire, tester, déployer) lancée à chaque modification.
> - **noyau** : le cœur du système d'exploitation (le kernel Linux), qui gère processus, mémoire, disques et réseau.
> - **cluster** : un groupe de machines qui travaillent ensemble comme un seul système.

## Comprendre : la chaîne d'accès au GPU

```
Kubernetes                                     OpenStack
pod (limits: nvidia.com/gpu: 1)                instance (flavor avec alias PCI ou resources:VGPU=1)
   │ scheduler : nœud avec la ressource           │ scheduler + Placement : compute avec la ressource
   ▼                                              ▼
kubelet ◄─ device plugin (GPU Operator)        nova-compute ─ libvirt : passthrough (vfio-pci) ou mdev (vGPU)
   │ NVIDIA Container Toolkit                     │
   ▼                                              ▼
conteneur voit /dev/nvidia0                    la VM voit un GPU (pilote NVIDIA dans l'invité)
            └────────── pilote NVIDIA sur l'hôte ──────────┘
```

## Sur Kubernetes

```yaml
apiVersion: v1
kind: Pod
metadata: { name: vllm }
spec:
  tolerations: [ { key: nvidia.com/gpu, operator: Exists, effect: NoSchedule } ]
  nodeSelector: { nvidia.com/gpu.product: NVIDIA-H100-80GB-HBM3 }   # label posé par GPU Feature Discovery
  containers:
    - name: vllm
      image: vllm/vllm-openai:<version>
      args: ["--model", "meta-llama/Llama-3.1-8B-Instruct", "--max-model-len", "16384"]
      resources: { limits: { nvidia.com/gpu: 1 } }
      volumeMounts: [ { name: cache, mountPath: /root/.cache/huggingface } ]
  volumes: [ { name: cache, persistentVolumeClaim: { claimName: hf-cache } } ]
```

```bash
kubectl describe node gpu-1 | grep -A3 -i 'nvidia.com/gpu'   # capacité et allocation
kubectl get pods -n gpu-operator                               # pilote, toolkit, device plugin, dcgm
kubectl exec -it vllm -- nvidia-smi                            # le GPU vu depuis le conteneur
```

| Partage | Isolation | Usage |
| --- | --- | --- |
| un GPU par pod | totale | production, gros modèles |
| MIG (ex. 7 instances sur un A100/H100) | matérielle (mémoire et calcul) | petits modèles, plusieurs équipes |
| time-slicing | aucune sur la mémoire | dev, notebooks, tests |
| DRA | selon le pilote | allocation fine, versions récentes de Kubernetes |

Bonnes pratiques : **taint** des nœuds GPU, **quotas** de `requests.nvidia.com/gpu` par namespace, cache des poids sur un volume partagé, sondes de démarrage généreuses, et supervision avec le **DCGM exporter** dans Prometheus.

Pour aller plus loin : **KServe** (`InferenceService` avec autoscaling), **Kubeflow** pour l'entraînement et les pipelines, **Ray** pour l'inférence et l'entraînement distribués, et **LeaderWorkerSet** pour un modèle réparti sur plusieurs nœuds.

## Sur OpenStack

```ini
# nova.conf (compute) : PCI passthrough
[pci]
device_spec = { "vendor_id": "10de", "product_id": "2330" }
alias = { "vendor_id": "10de", "product_id": "2330", "device_type": "type-PCI", "name": "h100" }
# nova.conf (contrôleur) : même alias, et PciPassthroughFilter dans enabled_filters
```

```bash
openstack flavor create --vcpus 16 --ram 131072 --disk 200 \
  --property pci_passthrough:alias='h100:1' g1.h100
# vGPU : le pilote NVIDIA vGPU expose des types mdev, déclarés dans [devices] enabled_mdev_types
openstack flavor create --vcpus 8 --ram 65536 --disk 100 --property resources:VGPU=1 g1.vgpu
openstack resource provider inventory list <compute-gpu>      # VGPU dans Placement
```

Points d'attention : **IOMMU** activé dans le BIOS et le noyau (`intel_iommu=on` ou `amd_iommu=on`), GPU lié à `vfio-pci` sur l'hôte pour le passthrough, licence NVIDIA pour le vGPU, **agrégats d'hôtes** dédiés aux computes GPU, et pas de live migration en passthrough. Avec **Ironic**, on peut aussi louer des serveurs GPU entiers en bare metal, souvent le meilleur choix pour l'entraînement.

## Combiner les deux

Un schéma courant : OpenStack fournit des **VM GPU** (passthrough) ou des serveurs **bare metal**, sur lesquels tourne un cluster Kubernetes avec le GPU Operator, et KServe ou vLLM y servent les modèles. L'équipe plateforme gère les GPU comme une ressource rare : quotas, réservations, supervision du taux d'utilisation (un GPU inactif coûte aussi cher qu'un GPU plein).

> **À retenir.** Kubernetes voit les GPU grâce au device plugin installé par le GPU Operator ; un pod demande `nvidia.com/gpu`, on teinte les nœuds GPU et on partage par MIG, time-slicing ou DRA. OpenStack donne des GPU aux VM par PCI passthrough (alias, PciPassthroughFilter, IOMMU) ou vGPU (ressource VGPU dans Placement), ou des serveurs entiers par Ironic. Superviser avec DCGM, mettre des quotas, et viser un taux d'utilisation élevé.
