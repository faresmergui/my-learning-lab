---
title: Synthèse Kubernetes
description: "Les objets, les commandes kubectl et la méthode de débogage, sur une page."
---

## L'architecture

| Composant | Où | Rôle |
| --- | --- | --- |
| kube-apiserver | control plane | Point d'entrée unique, valide et stocke les objets |
| etcd | control plane | Base clé-valeur qui contient l'état du cluster |
| kube-scheduler | control plane | Choisit le nœud de chaque pod |
| kube-controller-manager | control plane | Boucles de réconciliation (Deployment, ReplicaSet, Node…) |
| kubelet | chaque nœud | Lance et surveille les conteneurs des pods du nœud |
| kube-proxy / CNI | chaque nœud | Réseau des Services et des pods |

Tout fonctionne par **réconciliation** : on déclare l'état voulu, les contrôleurs rapprochent la réalité de cet état.

## Les objets à connaître

| Objet | Sert à |
| --- | --- |
| Pod | Un ou plusieurs conteneurs qui partagent réseau et volumes |
| Deployment | Pods sans état, mises à jour progressives, retour arrière |
| StatefulSet | Pods avec identité et stockage stables (bases de données) |
| DaemonSet | Un pod par nœud (agents de logs, monitoring) |
| Job / CronJob | Tâche qui se termine / tâche planifiée |
| Service | Adresse stable devant un groupe de pods (ClusterIP, NodePort, LoadBalancer) |
| Ingress / Gateway | Routage HTTP(S) depuis l'extérieur |
| ConfigMap / Secret | Configuration / données sensibles injectées dans les pods |
| PVC / PV / StorageClass | Demande de stockage / volume réel / type de stockage |
| Namespace | Découpage logique du cluster |
| ServiceAccount, Role, RoleBinding | Identité et droits (RBAC) |
| NetworkPolicy | Pare-feu entre pods |

## kubectl au quotidien

```bash
kubectl get pods -A -o wide                 # tous les pods, avec nœud et IP
kubectl get deploy,svc,ing -n shop          # plusieurs types à la fois
kubectl describe pod api-7d9f -n shop       # événements et détails
kubectl logs api-7d9f -c app --previous     # logs du conteneur précédent (après un crash)
kubectl logs -f deploy/api                  # suivre les logs d'un Deployment
kubectl exec -it api-7d9f -- sh             # shell dans le conteneur
kubectl port-forward svc/api 8080:80        # accéder à un Service en local
kubectl apply -f manifests/                 # appliquer un dossier
kubectl diff -f manifests/                  # voir ce qui changerait
kubectl rollout status deploy/api           # suivre un déploiement
kubectl rollout undo deploy/api             # revenir à la révision précédente
kubectl scale deploy/api --replicas=5
kubectl top pods --sort-by=memory           # consommation (metrics-server)
kubectl get events --sort-by=.lastTimestamp
kubectl auth can-i create pods --as system:serviceaccount:shop:api
kubectl explain deploy.spec.strategy        # documentation d'un champ
```

## Lire l'état d'un pod

| État | Cause habituelle | Premier réflexe |
| --- | --- | --- |
| Pending | Pas de nœud qui convient (ressources, taints, PVC) | `describe pod`, section Events |
| ContainerCreating longtemps | Volume ou Secret introuvable, CNI | `describe pod` |
| ImagePullBackOff | Image ou tag inexistant, registre privé sans secret | Vérifier l'image et `imagePullSecrets` |
| CrashLoopBackOff | L'application plante au démarrage | `logs --previous` |
| OOMKilled | Limite mémoire dépassée | Augmenter la limite ou corriger la fuite |
| Running mais 0/1 Ready | Readiness probe en échec | `describe pod`, tester l'endpoint |

## La méthode de débogage

1. **Le pod** tourne-t-il et est-il Ready ? `get pods`, `describe`, `logs`.
2. **Le Service** trouve-t-il les pods ? `kubectl get endpointslices -l kubernetes.io/service-name=api` : vide = sélecteur ou readiness en cause.
3. **Le réseau** : depuis un pod de test, `curl api.shop.svc.cluster.local`. Vérifier les NetworkPolicies.
4. **L'Ingress** : règle, classe d'Ingress, certificat, logs du contrôleur.

## Ressources et QoS

| Champ | Effet |
| --- | --- |
| `requests` | Réservé pour le placement par le scheduler |
| `limits.cpu` | Le conteneur est **ralenti** (throttling) au-delà |
| `limits.memory` | Le conteneur est **tué** (OOMKilled) au-delà |

Classes QoS : **Guaranteed** (requests = limits partout), **Burstable** (requests définies), **BestEffort** (rien). En cas de manque de mémoire sur le nœud, BestEffort part en premier.

## Les probes

| Probe | Question | En cas d'échec |
| --- | --- | --- |
| startupProbe | L'application a-t-elle fini de démarrer ? | Redémarrage après le délai |
| readinessProbe | Peut-elle recevoir du trafic ? | Retirée du Service, pas redémarrée |
| livenessProbe | Est-elle bloquée ? | Conteneur redémarré |

Piège : une liveness qui dépend de la base de données redémarre tous les pods quand la base tombe.

## Placement

- **nodeSelector / nodeAffinity** : attirer les pods vers certains nœuds.
- **taints / tolerations** : un nœud repousse les pods qui ne tolèrent pas sa taint.
- **podAntiAffinity / topologySpreadConstraints** : répartir les réplicas sur plusieurs nœuds ou zones.
- **PodDisruptionBudget** : garder un minimum de pods pendant les maintenances.

## Sécurité

- RBAC : **Role** (namespace) ou **ClusterRole**, liés à un ServiceAccount par un **RoleBinding**. Moindre privilège.
- Pod Security Standards : niveaux `privileged`, `baseline`, `restricted`, appliqués par label de namespace.
- `securityContext` : `runAsNonRoot`, `readOnlyRootFilesystem`, `allowPrivilegeEscalation: false`, capabilities retirées.
- NetworkPolicy : commencer par un **deny all** par namespace, puis ouvrir ce qui est nécessaire.

## Installer, mettre à jour, sauvegarder

- `kubeadm init`, un CNI, puis `kubeadm join` (`kubeadm token create --print-join-command`).
- Mise à jour : **une version mineure à la fois**, control plane d'abord (`kubeadm upgrade plan`, `apply`, puis `upgrade node`), chaque nœud drainé avant la mise à jour du kubelet.
- etcd : `etcdctl snapshot save` avec `--endpoints`, `--cacert`, `--cert`, `--key` (lus dans `etcd.yaml`) ; `etcdutl snapshot restore --data-dir <nouveau>` puis modifier le `hostPath` du manifeste.
- Certificats valables un an : `kubeadm certs check-expiration`, `kubeadm certs renew all`.

## CRD et opérateurs

- Une **CRD** ajoute un type à l'API ; un **opérateur** (contrôleur) le fait vivre. Sans opérateur, l'objet est stocké mais rien ne se passe.
- `kubectl get crd`, `kubectl api-resources`, `kubectl explain <type>.spec`, puis le `status` de l'objet.
- Supprimer une CRD supprime **tous** ses objets.

## Sécurité avancée (CKS)

| Thème | Gestes |
| --- | --- |
| conformité | `kube-bench run --targets master` / `node`, corriger dans `/etc/kubernetes/manifests/` ou `/var/lib/kubelet/config.yaml` |
| binaires | `sha512sum` comparé à l'empreinte officielle |
| API | `--anonymous-auth=false`, `--authorization-mode=Node,RBAC`, admission `NodeRestriction`, API privée |
| jetons | `automountServiceAccountToken: false`, jetons projetés courts |
| métadonnées cloud | NetworkPolicy de sortie qui exclut `169.254.169.254/32` |
| AppArmor | profil chargé sur le nœud (`apparmor_parser`, `aa-status`), `appArmorProfile: { type: Localhost, localhostProfile: … }` |
| sandbox | `RuntimeClass` (gVisor `runsc`, Kata) et `runtimeClassName` |
| trafic | mTLS avec un mesh (Istio `PeerAuthentication STRICT`) ou chiffrement Cilium |
| audit | politique (`None`, `Metadata`, `Request`, `RequestResponse`, première règle gagnante), flags **et** volumes dans l'API server |
| exécution | règles Falco (`condition`, `output`, `priority`) dans `falco_rules.local.yaml` |
| immuabilité | `readOnlyRootFilesystem`, image distroless, `emptyDir` pour `/tmp` |
