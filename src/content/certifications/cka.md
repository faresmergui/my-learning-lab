---
title: CKA
name: Certified Kubernetes Administrator
org: Linux Foundation / CNCF
order: 1
color: "#4f7cf0"
description: Administrer un cluster Kubernetes en ligne de commande, en conditions réelles.
officialUrl: https://training.linuxfoundation.org/certification/certified-kubernetes-administrator-cka/
checked: 22 octobre 2026
format:
  - { label: Type, value: "Examen pratique : des tâches à réaliser sur de vrais clusters, dans un terminal distant" }
  - { label: Durée, value: "2 heures, pour 15 à 20 tâches" }
  - { label: Score pour réussir, value: "66 %" }
  - { label: Documentation autorisée, value: "kubernetes.io (docs, blog) et les docs des outils cités dans l'énoncé" }
  - { label: Inclus, value: "Une seconde tentative gratuite et deux sessions de simulateur (killer.sh)" }
  - { label: Validité, value: "2 ans" }
domains:
  - name: Troubleshooting
    weight: 30
    fiches: [kubernetes/09-methode-de-debug, kubernetes/02-probes-et-etats, kubernetes/09-metriques-et-monitoring, reseaux/08-reseau-kubernetes-et-cni, linux/07-journald-et-logs]
  - name: Architecture, installation et configuration du cluster
    weight: 25
    fiches: [kubernetes/01-composants-du-cluster, kubernetes/01-trajet-d-une-requete, kubernetes/08-rbac, kubernetes/10-helm, kubernetes/10-kustomize-et-gitops, kubernetes/01-installer-mettre-a-jour-sauvegarder, kubernetes/10-crd-et-operateurs]
  - name: Services et réseau
    weight: 20
    fiches: [kubernetes/04-services, kubernetes/04-ingress-et-gateway-api, kubernetes/08-network-policies, reseaux/03-dns]
  - name: Workloads et scheduling
    weight: 15
    fiches: [kubernetes/03-deployments-et-rolling-updates, kubernetes/03-statefulset-daemonset-job, kubernetes/02-pods-multi-conteneurs, kubernetes/05-injecter-la-configuration, kubernetes/07-requests-limits-qos, kubernetes/07-taints-et-affinites, kubernetes/07-repartir-et-prioriser]
  - name: Stockage
    weight: 10
    fiches: [kubernetes/06-pv-pvc-storageclass, kubernetes/06-volumes-ephemeres]
  - name: Se préparer à l'examen
    fiches: [kubernetes/11-passer-l-examen-cka]
---

## Ce que l'examen vérifie vraiment

La CKA ne pose aucune question de cours : elle te donne un cluster et une tâche (« le pod `api` ne démarre pas, répare-le », « crée un utilisateur qui ne peut lire que les pods du namespace `dev` »). Elle vérifie que tu sais **faire**, **vite**, avec `kubectl` et la documentation. Le troubleshooting pèse presque un tiers de la note : c'est là qu'il faut être le plus à l'aise.

## Les pièges

- **Le mauvais contexte.** Chaque tâche indique sur quel cluster travailler. Une tâche parfaite faite sur le mauvais cluster rapporte zéro point. Lance la commande `kubectl config use-context …` (ou le `ssh`) donnée en tête de tâche, à chaque fois.
- **Le mauvais namespace.** Ajoute `-n <ns>` partout, ou change le namespace par défaut du contexte. Un objet créé dans `default` au lieu de `dev` ne compte pas.
- **Rester bloqué.** Toutes les tâches ne valent pas autant de points. Au-delà de 6 à 8 minutes sur une tâche, note-la et passe à la suivante.
- **Écrire le YAML à la main.** C'est lent et source de fautes d'indentation. Génère-le, puis modifie-le.
- **Oublier de vérifier.** Après chaque tâche, un `kubectl get` ou un `describe` confirme que l'objet est bien là et dans l'état voulu.

## À connaître par cœur

```bash
# Générer du YAML au lieu de l'écrire
kubectl create deployment api --image=nginx --replicas=3 --dry-run=client -o yaml > api.yaml
kubectl run tmp --image=busybox:1.36 --restart=Never --dry-run=client -o yaml -- sleep 3600
kubectl expose deployment api --port=80 --target-port=8080 --dry-run=client -o yaml

# Trouver un champ sans quitter le terminal
kubectl explain pod.spec.containers.securityContext

# RBAC
kubectl create role ... ; kubectl create rolebinding ...
kubectl auth can-i list pods -n dev --as=jane

# Diagnostic
kubectl describe pod <pod> ; kubectl logs <pod> --previous
kubectl get events -n <ns> --sort-by=.lastTimestamp
journalctl -u kubelet -n 50     # sur le nœud
```

Côté cluster, sache aussi retrouver les manifestes des composants du control plane (`/etc/kubernetes/manifests/`, ce sont des pods statiques), la configuration du kubelet (`/var/lib/kubelet/config.yaml`) et les certificats (`/etc/kubernetes/pki/`).

## Stratégie le jour J

1. **Premier tour rapide** : fais toutes les tâches courtes et sûres, saute les longues.
2. **Deuxième tour** : reviens sur les tâches notées, de la plus rentable à la moins rentable.
3. **Dix dernières minutes** : relis les tâches faites, vérifie contexte et namespace.

Prépare-toi avec la fiche « Passer l'examen CKA » et les deux sessions du simulateur : la première tôt, pour mesurer l'écart, la seconde quelques jours avant l'examen.
