---
title: Auditer l'API et détecter à l'exécution
chapter: 12
order: 3
duration: 11
tags:
- CKS
- audit
- Falco
cards:
- q: Quels sont les quatre niveaux d'une règle d'audit Kubernetes ?
  a: '`None` (rien), `Metadata` (qui, quoi, quand, sans contenu), `Request` (plus le corps de la requête), `RequestResponse` (plus la réponse). Plus le niveau est haut, plus le journal grossit.'
- q: Dans une politique d'audit, quelle règle s'applique si plusieurs correspondent ?
  a: La **première** de la liste. On met donc les règles précises (par exemple `None` pour le bruit) en haut et une règle générale à la fin.
- q: Quels flags de l'API server activent l'audit ?
  a: '`--audit-policy-file` (la politique) et `--audit-log-path` (le fichier de journal), plus `--audit-log-maxage`, `--audit-log-maxbackup` et `--audit-log-maxsize` pour la rotation. Il faut aussi monter les deux chemins en `hostPath` dans le manifeste.'
- q: De quoi se compose une règle Falco ?
  a: '`rule` (le nom), `desc`, `condition` (le filtre sur les événements système), `output` (le message, avec des champs comme `%container.name`) et `priority`.'
- q: Où ajouter ses propres règles Falco sans toucher aux règles fournies ?
  a: Dans `/etc/falco/falco_rules.local.yaml` (ou un fichier de `rules.d`), lu après les règles par défaut. On peut y redéfinir une règle existante.
- q: Qu'est-ce qu'un conteneur immuable ?
  a: 'Un conteneur qu''on ne modifie jamais en marche : système de fichiers en lecture seule, pas de shell ni de gestionnaire de paquets dans l''image. Pour changer quelque chose, on construit une nouvelle image et on redéploie.'
quiz:
- q: Tu veux savoir qui a lu les Secrets du namespace `paiement`, sans enregistrer leur contenu. Quel niveau ?
  options:
  - '`None`'
  - '`Metadata`'
  - '`Request`'
  - '`RequestResponse`'
  answer: 1
  explain: '`Metadata` enregistre l''utilisateur, le verbe, la ressource et l''heure. `RequestResponse` sur des Secrets écrirait leur valeur en clair dans le journal.'
- q: 'Falco alerte : « shell lancé dans le conteneur `api` ». Que fais-tu d''abord ?'
  options:
  - Supprimer la règle Falco
  - Identifier le pod et le nœud dans l'alerte, isoler le pod, puis analyser
  - Redémarrer le cluster
  - Augmenter la priorité de la règle
  answer: 1
  explain: 'Une alerte à l''exécution est un incident possible : on garde les preuves et on isole (NetworkPolicy, retrait du Service) avant de supprimer quoi que ce soit.'
- q: Quel réglage rend un conteneur plus immuable ?
  options:
  - '`readOnlyRootFilesystem: true`'
  - '`hostPID: true`'
  - '`imagePullPolicy: Never`'
  - '`replicas: 1`'
  answer: 0
  explain: Avec le système de fichiers en lecture seule, ni l'appli ni un attaquant ne peuvent modifier les binaires ou déposer un outil.
level: intermédiaire
---

Prévenir ne suffit jamais complètement. La CKS demande aussi de **voir** ce qui se passe : qui a fait quoi sur l'API (les journaux d'audit), et quels comportements suspects apparaissent dans les conteneurs pendant qu'ils tournent (Falco). Elle demande enfin des conteneurs **immuables**, qui rendent ces comportements plus faciles à repérer.

> **Les outils cités dans cette fiche.**
> - **journal d'audit** de l'API server : un fichier où l'API écrit chaque requête reçue (qui, quoi, sur quelle ressource, avec quel résultat), selon une **politique d'audit**.
> - **Falco** : un outil de détection qui observe les appels système des conteneurs et alerte quand une règle correspond (un shell lancé, un fichier sensible lu, une connexion inattendue).
> - **SIEM** : un outil qui centralise les journaux pour chercher et corréler les événements de sécurité.
> - **distroless** : des images de base qui ne contiennent que l'appli et ses bibliothèques, sans shell ni gestionnaire de paquets.
> - **CI** : l'intégration continue : chaque modification de code est automatiquement construite et testée.

## Comprendre : deux angles de vue

| Source | Ce qu'elle voit | Exemple d'alerte |
| --- | --- | --- |
| audit de l'API | les actions faites **via l'API** | un compte crée un ClusterRoleBinding à 3 h du matin |
| Falco | les actions faites **dans les conteneurs** et sur le nœud | un processus lit `/etc/shadow` dans un pod web |

Un attaquant qui passe par `kubectl exec` apparaît dans les deux : l'audit voit l'`exec`, Falco voit le shell lancé.

## Écrire une politique d'audit

```yaml
# /etc/kubernetes/audit/policy.yaml
apiVersion: audit.k8s.io/v1
kind: Policy
omitStages: [RequestReceived]          # évite de tout écrire en double
rules:
  - level: None                        # le bruit d'abord : ignoré
    users: ["system:kube-proxy"]
    verbs: ["watch"]
  - level: Metadata                    # les Secrets : qui et quand, jamais le contenu
    resources: [{ group: "", resources: ["secrets", "configmaps"] }]
  - level: RequestResponse             # les droits : tout le détail
    resources: [{ group: "rbac.authorization.k8s.io" }]
  - level: Metadata                    # tout le reste
```

La **première règle qui correspond** gagne : l'ordre compte.

## L'activer dans l'API server

```yaml
# extrait de /etc/kubernetes/manifests/kube-apiserver.yaml
    - --audit-policy-file=/etc/kubernetes/audit/policy.yaml
    - --audit-log-path=/var/log/kubernetes/audit/audit.log
    - --audit-log-maxage=30
    - --audit-log-maxbackup=10
    - --audit-log-maxsize=100
  volumeMounts:
    - { name: audit-policy, mountPath: /etc/kubernetes/audit, readOnly: true }
    - { name: audit-log, mountPath: /var/log/kubernetes/audit }
volumes:
  - { name: audit-policy, hostPath: { path: /etc/kubernetes/audit, type: DirectoryOrCreate } }
  - { name: audit-log, hostPath: { path: /var/log/kubernetes/audit, type: DirectoryOrCreate } }
```

L'oubli classique : les flags sans les volumes. L'API server, qui tourne dans un conteneur, ne trouve pas le fichier et ne redémarre pas. On lit ensuite le journal avec `jq` ou on l'envoie vers un SIEM.

## Lire et écrire des règles Falco

Falco fournit des centaines de règles. Une règle ressemble à ceci :

```yaml
# /etc/falco/falco_rules.local.yaml
- rule: Shell dans un conteneur de prod
  desc: Un shell interactif a été lancé dans un conteneur
  condition: >
    spawned_process and container
    and proc.name in (bash, sh, zsh)
    and k8s.ns.name = "shop"
  output: >
    Shell lancé (pod=%k8s.pod.name ns=%k8s.ns.name
    image=%container.image.repository cmd=%proc.cmdline user=%user.name)
  priority: WARNING
```

- `condition` filtre les événements système ; `spawned_process` et `container` sont des **macros** fournies par Falco.
- `output` est le message ; les champs `%…` sont remplacés par les valeurs réelles.
- On voit les alertes dans les logs de Falco : `journalctl -u falco` sur un nœud, ou `kubectl logs -n falco ds/falco` s'il tourne en DaemonSet.

À l'examen, une tâche typique consiste à modifier le format de `output` d'une règle existante ou à trouver, dans les alertes, quel pod a déclenché une règle.

## Des conteneurs immuables

Un conteneur immuable ne change jamais une fois lancé. Ça rend toute modification suspecte, donc facile à détecter :

```yaml
securityContext:
  readOnlyRootFilesystem: true        # rien ne s'écrit dans l'image
  allowPrivilegeEscalation: false
  runAsNonRoot: true
volumeMounts:
  - { name: tmp, mountPath: /tmp }    # seul endroit écrivable, et vide au démarrage
```

Avec une image **distroless**, il n'y a même pas de shell : un attaquant ne peut pas « se connecter » au conteneur. Pour corriger quelque chose, on reconstruit l'image et on redéploie, ce qui laisse une trace dans Git et la CI.

> **À retenir.** L'audit dit qui a fait quoi via l'API : `Metadata` pour les Secrets, première règle gagnante, flags **et** volumes dans l'API server. Falco voit ce qui se passe dans les conteneurs, avec des règles `condition` et `output`. Un conteneur immuable (lecture seule, sans shell) rend chaque écart visible.
