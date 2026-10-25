---
title: Isoler les workloads et chiffrer le trafic
chapter: 12
order: 2
duration: 11
tags:
- CKS
- AppArmor
- gVisor
- mTLS
cards:
- q: Comment applique-t-on un profil AppArmor à un conteneur ?
  a: 'Le profil doit être **chargé sur le nœud** (`apparmor_parser`, vérifier avec `aa-status`). Puis dans le `securityContext` : `appArmorProfile: { type: Localhost, localhostProfile: <nom> }`.'
- q: Que se passe-t-il si le profil AppArmor demandé n'est pas chargé sur le nœud ?
  a: Le pod **ne démarre pas** (erreur de création du conteneur). Il faut charger le profil sur chaque nœud où le pod peut aller, souvent avec un DaemonSet ou l'outil de configuration des nœuds.
- q: À quoi sert une RuntimeClass ?
  a: À choisir le **runtime** qui lance les conteneurs d'un pod, par exemple **gVisor** (`runsc`) ou **Kata Containers**, plus isolés que runc. Le pod la demande avec `runtimeClassName`.
- q: Différence entre gVisor et Kata Containers ?
  a: '**gVisor** intercepte les appels système dans un noyau écrit en espace utilisateur : le conteneur ne parle presque plus au vrai noyau. **Kata** lance chaque pod dans une **petite machine virtuelle** avec son propre noyau.'
- q: Qu'apporte le mTLS entre pods ?
  a: Chaque pod prouve son identité avec un certificat **et** le trafic est chiffré. Un attaquant sur le réseau ne peut ni lire ni se faire passer pour un service. On l'obtient avec un service mesh (Istio, Linkerd) ou le chiffrement de Cilium.
- q: Comment réduire l'empreinte du système hôte d'un nœud ?
  a: Un OS minimal fait pour les conteneurs (Bottlerocket, Talos, Flatcar), aucun paquet ni service inutile, pas de SSH ouvert, et un rôle IAM du nœud limité à ce dont le kubelet a besoin.
quiz:
- q: Un pod de traitement d'images exécute du code fourni par les clients. Quelle protection ajoutes-tu en priorité ?
  options:
  - Plus de réplicas
  - Une RuntimeClass gVisor ou Kata pour isoler du noyau
  - Un Service de type LoadBalancer
  - Un PodDisruptionBudget
  answer: 1
  explain: Du code non fiable peut chercher une faille du noyau. Un runtime sandbox ajoute une barrière entre le conteneur et le noyau de l'hôte.
- q: Le pod reste en `CreateContainerError` après l'ajout d'un `appArmorProfile` de type Localhost. Première vérification ?
  options:
  - Le nom de l'image
  - '`aa-status` sur le nœud pour voir si le profil est chargé'
  - Les NetworkPolicies
  - Le quota du namespace
  answer: 1
  explain: Le profil est lu sur le nœud qui lance le conteneur. S'il n'y est pas chargé, le runtime refuse de démarrer le conteneur.
level: intermédiaire
---

Un conteneur n'est pas une machine virtuelle : il partage le **noyau** de l'hôte. Pod Security et le `securityContext` (chapitre 8) retirent déjà les privilèges dangereux. La CKS demande d'aller plus loin pour les charges sensibles : limiter ce que le processus peut toucher avec AppArmor, l'éloigner du noyau avec un runtime sandbox, et chiffrer le trafic entre les pods.

> **Les outils cités dans cette fiche.**
> - **AppArmor** : un module de sécurité du noyau Linux qui limite, par programme, les fichiers, capacités et accès réseau autorisés (voir la fiche Linux sur SELinux et AppArmor).
> - **apparmor_parser** et **aa-status** : chargent un profil AppArmor dans le noyau et listent les profils chargés.
> - **seccomp** : un filtre du noyau qui limite les appels système qu'un programme peut faire.
> - **runc** : le runtime par défaut qui crée les conteneurs ; il s'appuie directement sur le noyau de l'hôte.
> - **gVisor** (commande `runsc`) : un runtime de Google qui place un noyau simulé entre le conteneur et le vrai noyau.
> - **Kata Containers** : un runtime qui lance chaque pod dans une machine virtuelle légère.
> - **mTLS** (TLS mutuel) : du TLS où le client **et** le serveur présentent un certificat, donc où chacun prouve son identité.
> - **service mesh** (**Istio**, **Linkerd**) : une couche qui ajoute à chaque pod un proxy chargé du mTLS, des nouvelles tentatives et des métriques, sans changer le code.
> - **Cilium** : un CNI qui peut aussi chiffrer le trafic entre nœuds (WireGuard ou IPsec) et authentifier les pods.
> - **API** : interface qui permet à un programme d'en piloter un autre par des requêtes (souvent HTTP).
> - **SSH** : le protocole de connexion à distance chiffrée à une machine, en ligne de commande.

## Comprendre : trois couches d'isolation

| Couche | Ce qu'elle limite | Outil |
| --- | --- | --- |
| droits du processus | root, capacités, escalade | `securityContext`, Pod Security |
| accès aux ressources | fichiers, réseau, appels système | AppArmor, seccomp |
| contact avec le noyau | les failles du noyau partagé | gVisor, Kata (RuntimeClass) |

Chaque couche coûte un peu plus en complexité ou en performance. On ne met pas gVisor partout : on le réserve aux pods qui exécutent du code peu fiable ou exposé.

## AppArmor dans un pod

Un profil AppArmor est un fichier texte qui liste ce qu'un programme a le droit de faire. Exemple de profil qui interdit toute écriture :

```
#include <tunables/global>
profile k8s-deny-write flags=(attach_disconnected) {
  #include <abstractions/base>
  file,          # lecture autorisée
  deny /** w,    # aucune écriture nulle part
}
```

```bash
# Sur chaque nœud qui peut recevoir le pod
apparmor_parser -q /etc/apparmor.d/k8s-deny-write
aa-status | grep k8s-deny-write
```

```yaml
spec:
  containers:
    - name: web
      image: registry.shop.fr/web:1.4
      securityContext:
        appArmorProfile:
          type: Localhost
          localhostProfile: k8s-deny-write
```

Les autres types sont `RuntimeDefault` (le profil prudent du runtime) et `Unconfined` (aucun profil). Les anciens clusters utilisaient une annotation `container.apparmor.security.beta.kubernetes.io/<conteneur>` : tu peux la croiser dans de vieux manifestes.

## Les runtimes sandbox avec RuntimeClass

```yaml
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata: { name: gvisor }
handler: runsc            # nom du runtime configuré dans containerd sur les nœuds
---
apiVersion: v1
kind: Pod
metadata: { name: convertisseur }
spec:
  runtimeClassName: gvisor
  containers: [{ name: app, image: registry.shop.fr/convert:2.0 }]
```

Pour vérifier que le pod tourne bien sous gVisor : `kubectl exec convertisseur -- dmesg` affiche les messages du noyau simulé de gVisor au lieu de ceux de l'hôte.

Le prix à payer : des appels système plus lents (gVisor) ou plus de mémoire par pod (Kata), et certaines applis qui utilisent des fonctions rares du noyau ne marchent pas.

## Chiffrer le trafic entre les pods

Par défaut, le trafic entre deux pods circule **en clair** sur le réseau du cluster. Deux approches pour le protéger :

- **Un service mesh** (Istio, Linkerd) : un proxy à côté de chaque pod établit du mTLS avec le proxy d'en face. Avec Istio, une `PeerAuthentication` en mode `STRICT` refuse tout trafic qui n'est pas en mTLS.
- **Le chiffrement du CNI** : Cilium chiffre tout le trafic entre nœuds avec WireGuard ou IPsec, sans proxy dans les pods.

Le mesh apporte en plus l'**identité** de chaque service (on peut autoriser « le front peut appeler l'API » sur cette base). Le chiffrement du CNI est plus simple mais ne fait que chiffrer.

## Réduire l'empreinte de l'hôte

Moins il y a de choses sur un nœud, moins il y a à attaquer :

- un OS fait pour les conteneurs (Bottlerocket, Talos, Flatcar) : système de fichiers en lecture seule, pas de gestionnaire de paquets ;
- aucun service inutile, ports fermés, pas de SSH (ou SSH seulement par un bastion) ;
- un **rôle IAM du nœud** minimal : un pod qui atteint les identifiants du nœud ne doit pas pouvoir piloter tout le compte cloud.

> **À retenir.** AppArmor limite ce qu'un conteneur peut toucher, à condition que le profil soit chargé sur le nœud. Une RuntimeClass gVisor ou Kata éloigne les pods non fiables du noyau. Le trafic entre pods est en clair par défaut : mTLS avec un mesh, ou chiffrement du CNI.
