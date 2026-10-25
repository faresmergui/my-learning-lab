---
title: Durcir le cluster et l'accès à l'API
chapter: 12
order: 1
duration: 12
tags:
- CKS
- CIS
- API server
cards:
- q: Que fait kube-bench ?
  a: Il compare la configuration d'un cluster (API server, kubelet, etcd, fichiers sur les nœuds) au **CIS Benchmark Kubernetes** et liste chaque point en PASS, FAIL ou WARN, avec la correction proposée.
- q: Comment vérifier qu'un binaire Kubernetes n'a pas été modifié ?
  a: Calculer son empreinte avec `sha512sum` et la comparer à celle publiée avec la version officielle (fichier `.sha512` à côté du binaire sur `dl.k8s.io`).
- q: Quels réglages de l'API server limitent qui peut lui parler ?
  a: '`--anonymous-auth=false` (pas de requête sans identité, sauf besoin précis), `--authorization-mode=Node,RBAC`, l''admission `NodeRestriction`, et une API joignable seulement depuis un réseau privé ou une liste d''IP.'
- q: Que fait l'admission NodeRestriction ?
  a: Elle empêche le kubelet d'un nœud de modifier les objets **des autres nœuds** ou les pods qui ne tournent pas chez lui. Un nœud compromis ne peut pas s'en prendre au reste du cluster par l'API.
- q: Comment limiter les jetons de ServiceAccount ?
  a: '`automountServiceAccountToken: false` sur la ServiceAccount ou le pod quand l''appli n''appelle pas l''API ; sinon un jeton projeté à durée courte (`expirationSeconds`) et des droits RBAC minimaux. Éviter les vieux jetons stockés dans des Secrets, qui n''expirent pas.'
- q: Pourquoi bloquer `169.254.169.254` depuis les pods ?
  a: C'est l'adresse du **service de métadonnées** du cloud. Il peut donner les identifiants IAM du nœud. Une NetworkPolicy de sortie qui exclut cette adresse empêche un pod compromis de les récupérer.
quiz:
- q: kube-bench signale que le kubelet accepte les requêtes anonymes. Où corriges-tu ?
  options:
  - Dans le manifeste de l'API server
  - 'Dans la configuration du kubelet (`/var/lib/kubelet/config.yaml`), `authentication.anonymous.enabled: false`'
  - Dans une NetworkPolicy
  - Dans un Role RBAC
  answer: 1
  explain: Chaque composant a sa propre configuration. Pour le kubelet, on modifie son fichier puis on le redémarre avec `systemctl restart kubelet`.
- q: Une appli web n'appelle jamais l'API Kubernetes. Quel réglage réduit le risque si elle est compromise ?
  options:
  - '`hostNetwork: true`'
  - '`automountServiceAccountToken: false`'
  - Un ClusterRole admin
  - '`privileged: false` seulement'
  answer: 1
  explain: Sans jeton monté, un attaquant dans le conteneur n'a aucune identité à utiliser contre l'API.
- q: Tu modifies `/etc/kubernetes/manifests/kube-apiserver.yaml`. Comment appliquer le changement ?
  options:
  - '`kubectl apply -f` sur le fichier'
  - 'Rien : le kubelet voit le fichier changer et recrée le pod'
  - '`systemctl restart kube-apiserver`'
  - '`kubeadm init`'
  answer: 1
  explain: 'C''est un manifeste statique. Le kubelet le surveille et redémarre l''API server. Une faute de syntaxe l''empêche de revenir : garde une copie avant de modifier.'
level: intermédiaire
---

Le chapitre 8 a posé les bases : RBAC, NetworkPolicies, Pod Security. La **CKS** (Certified Kubernetes Security Specialist) va plus loin et demande de durcir le cluster lui-même. Cette fiche couvre la mise en place et le durcissement du cluster : vérifier sa configuration, ses binaires, l'accès à l'API, les jetons et les métadonnées du cloud.

> **Les outils cités dans cette fiche.**
> - **CIS Benchmark** : une liste de réglages de sécurité recommandés, publiée par le Center for Internet Security, pour un système donné (ici Kubernetes).
> - **kube-bench** : l'outil qui vérifie automatiquement un cluster contre ce benchmark et dit quoi corriger.
> - **sha512sum** : calcule l'empreinte d'un fichier. Deux fichiers identiques ont la même empreinte ; un seul octet changé la modifie entièrement.
> - **admission controller** : un contrôle que l'API server applique à chaque requête après l'authentification et le RBAC, pour accepter, refuser ou modifier un objet. **NodeRestriction** en est un.
> - **ServiceAccount** : l'identité d'un pod auprès de l'API ; son **jeton** est la preuve de cette identité.
> - **service de métadonnées** (IMDS) : une adresse spéciale (`169.254.169.254`) que chaque machine cloud interroge pour connaître sa configuration et ses identifiants temporaires.
> - **IAM** : la gestion des identités et des droits (qui peut faire quoi).
> - **VPN** : un tunnel chiffré qui relie un poste ou un site à un réseau privé à travers Internet.
> - **AWS** : Amazon Web Services, le cloud public d'Amazon.

## Comprendre : la surface d'attaque d'un cluster

Un attaquant qui entre dans un pod cherche à en sortir. Les portes les plus courantes sont toujours les mêmes :

| Porte | Ce qu'il cherche | Parade |
| --- | --- | --- |
| l'API server | des droits pour créer des pods privilégiés | RBAC strict, API privée, pas d'accès anonyme |
| le jeton de ServiceAccount | une identité déjà montée dans le pod | pas de jeton si inutile, jetons courts |
| le kubelet (port 10250) | lancer des commandes dans d'autres pods | authentification et autorisation du kubelet |
| les métadonnées du cloud | les identifiants IAM du nœud | bloquer `169.254.169.254` |
| un binaire modifié | une porte dérobée persistante | vérifier les empreintes |

Le durcissement consiste à fermer chacune de ces portes, puis à le vérifier avec un outil plutôt que de mémoire.

## Vérifier la configuration avec kube-bench

```bash
kube-bench run --targets master      # sur un nœud du control plane
kube-bench run --targets node        # sur un worker
```

Chaque ligne en `[FAIL]` donne la règle et la correction. Exemple typique :

```
[FAIL] 1.2.16 Ensure that the --profiling argument is set to false
Remediation: Edit /etc/kubernetes/manifests/kube-apiserver.yaml and set --profiling=false
```

Les composants du control plane se corrigent dans leurs **manifestes statiques** (`/etc/kubernetes/manifests/`), le kubelet dans `/var/lib/kubelet/config.yaml` suivi d'un `systemctl restart kubelet`. Avant de modifier un manifeste, garde-en une copie **hors** de ce dossier : un fichier de trop dans `manifests/` serait lancé lui aussi.

## Vérifier les binaires

```bash
sha512sum /usr/bin/kubelet
# comparer avec l'empreinte officielle, publiée à côté du binaire :
# https://dl.k8s.io/v1.34.1/bin/linux/amd64/kubelet.sha512
```

Si les deux empreintes diffèrent, le binaire n'est pas celui publié par le projet : on le remplace par la version officielle et on cherche comment il a été modifié.

## Restreindre l'accès à l'API

Dans le manifeste de l'API server, les réglages qui comptent :

```yaml
- --anonymous-auth=false                 # pas de requête sans identité
- --authorization-mode=Node,RBAC         # jamais AlwaysAllow
- --enable-admission-plugins=NodeRestriction
- --profiling=false
```

Et côté réseau : l'API ne doit être joignable que depuis un réseau privé, un VPN ou une liste d'adresses. Sur un service managé, c'est l'option « endpoint privé » ou la liste d'IP autorisées.

## Limiter les jetons de ServiceAccount

```yaml
apiVersion: v1
kind: ServiceAccount
metadata: { name: web, namespace: shop }
automountServiceAccountToken: false      # pas de jeton dans les pods par défaut
```

Pour les applis qui appellent vraiment l'API, Kubernetes monte un **jeton projeté** : il expire (une heure par défaut, renouvelé automatiquement) et n'est valable que pour ce pod. Les anciens jetons stockés dans des Secrets de type `kubernetes.io/service-account-token` n'expirent jamais : on évite d'en créer.

## Protéger les métadonnées du cloud

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: bloquer-metadonnees, namespace: shop }
spec:
  podSelector: {}
  policyTypes: [Egress]
  egress:
    - to:
        - ipBlock:
            cidr: 0.0.0.0/0
            except: [169.254.169.254/32]
```

Sur AWS, on ajoute en plus **IMDSv2** avec une limite de saut à 1 : la réponse du service de métadonnées ne traverse plus le réseau d'un conteneur.

## Mettre à jour

Une version de Kubernetes reçoit des correctifs de sécurité pendant environ **un an**. Un cluster qui n'est plus mis à jour accumule des failles connues. La procédure est celle de la fiche « Installer, mettre à jour et sauvegarder un cluster » (chapitre 1).

> **À retenir.** On vérifie avec kube-bench et `sha512sum`, on corrige dans les manifestes statiques ou la config du kubelet. L'API n'accepte ni anonyme ni `AlwaysAllow`, `NodeRestriction` est activé. Pas de jeton monté sans besoin, et l'adresse des métadonnées est bloquée pour les pods.
