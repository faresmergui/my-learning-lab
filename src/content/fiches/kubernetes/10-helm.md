---
title: 'Helm : charts et releases'
chapter: 10
order: 1
duration: 9
level: intermédiaire
tags:
- CKA
cards:
- q: Qu'est-ce qu'un chart, une release et une révision ?
  a: Le **chart** est le paquet (templates + valeurs par défaut). La **release** est une installation de ce chart dans un namespace. Chaque `upgrade` crée une nouvelle **révision**.
- q: Quelle commande installe ou met à jour une release en une fois ?
  a: '`helm upgrade --install api ./chart -n shop -f values-prod.yaml`. Idéal en CI, car elle marche que la release existe ou non.'
- q: Dans quel ordre Helm applique-t-il les valeurs ?
  a: '`values.yaml` du chart, puis chaque fichier `-f` dans l''ordre, puis les `--set`. La dernière valeur gagne.'
- q: Comment voir les manifestes générés sans rien installer ?
  a: '`helm template api ./chart -f values-prod.yaml`, ou `helm upgrade --install … --dry-run` pour passer aussi par la validation du cluster.'
- q: Où Helm stocke-t-il l'historique d'une release ?
  a: Dans des **Secrets** du namespace de la release, nommés `sh.helm.release.v1.<release>.v<révision>`.
- q: Comment revenir à une révision précédente ?
  a: '`helm history api -n shop` pour lister, puis `helm rollback api 3 -n shop`.'
quiz:
- q: Tu lances `helm upgrade` avec `--set image.tag=2.1`, puis un second `helm upgrade` sans ce `--set`. Quel tag est déployé ?
  options:
  - 2.1, Helm le garde en mémoire
  - Celui de `values.yaml`, sauf si tu utilises `--reuse-values`
  - Le dernier tag de l'image
  - La commande échoue
  answer: 1
  explain: Chaque upgrade repart des valeurs du chart et de celles que tu passes. Mets tes valeurs dans des fichiers versionnés plutôt qu'en `--set`, pour éviter ces surprises.
- q: Tu veux voir ce qu'un `helm upgrade` va changer avant de l'appliquer. Quel outil ?
  options:
  - helm lint
  - Le plugin helm-diff (`helm diff upgrade`)
  - helm status
  - helm get notes
  answer: 1
  explain: '`helm diff upgrade` affiche les différences ligne par ligne, comme un `terraform plan`.'
---

Helm est le gestionnaire de paquets de Kubernetes. Il transforme des templates et des valeurs en manifestes, et garde l'historique de ce qui a été installé.


> **Les termes et outils cités dans cette fiche.**
> - **YAML** : un format de fichier texte structuré par l'indentation, utilisé par Kubernetes, Ansible, GitLab CI…

## Structure d'un chart

```
api/
├── Chart.yaml          # nom, version du chart, version de l'appli
├── values.yaml         # valeurs par défaut
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    └── _helpers.tpl    # fonctions réutilisables
```

```yaml
# templates/deployment.yaml (extrait)
spec:
  replicas: {{ .Values.replicaCount }}
  template:
    spec:
      containers:
        - name: api
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          resources: {{- toYaml .Values.resources | nindent 12 }}
```

<!-- schema:helm -->
<figure class="diagram"><svg viewBox="0 0 680 250" role="img" aria-label="Ce que fait helm install ou upgrade" style="--minw:560px"><defs><marker id="g15-n" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head n"/></marker><marker id="g15-c" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head c"/></marker><marker id="g15-a" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head a"/></marker><marker id="g15-ok" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1 L9 5 L0 9 z" class="dg-head ok"/></marker></defs><g class="dg-box dg-pop" style="--d:0"><rect x="14" y="18" width="150" height="48" rx="9"/></g><text x="89.0" y="39.0" class="dg-t" text-anchor="middle" style="--d:0">templates/</text><text x="89.0" y="57.0" class="dg-s" text-anchor="middle" style="--d:0">deployment.yaml…</text><g class="dg-box dg-pop" style="--d:0"><rect x="14" y="80" width="150" height="48" rx="9"/></g><text x="89.0" y="101.0" class="dg-t" text-anchor="middle" style="--d:0">values.yaml</text><text x="89.0" y="119.0" class="dg-s" text-anchor="middle" style="--d:0">défauts du chart</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="14" y="142" width="150" height="48" rx="9"/></g><text x="89.0" y="163.0" class="dg-t" text-anchor="middle" style="--d:1">-f values-prod.yaml</text><text x="89.0" y="181.0" class="dg-s" text-anchor="middle" style="--d:1">tes valeurs</text><g class="dg-box dg-c dg-pop" style="--d:1"><rect x="14" y="196" width="150" height="40" rx="9"/></g><text x="89.0" y="221.0" class="dg-s" text-anchor="middle" style="--d:1">--set image.tag=…</text><g class="dg-box dg-c dg-pop" style="--d:2"><rect x="226" y="80" width="140" height="60" rx="9"/></g><text x="296.0" y="100.0" class="dg-t" text-anchor="middle" style="--d:2">helm</text><text x="296.0" y="118.0" class="dg-s" text-anchor="middle" style="--d:2"><tspan x="296.0" dy="0">moteur de</tspan><tspan x="296.0" dy="14">templates</tspan></text><path d="M164 42 L196 42 L196 110 L224 110" class="dg-l"/><path d="M164 104 L196 104 L196 110 L224 110" class="dg-l" marker-end="url(#g15-n)"/><path d="M164 166 L196 166 L196 110 L224 110" class="dg-l"/><path d="M164 216 L196 216 L196 110 L224 110" class="dg-l"/><g class="dg-box dg-pop" style="--d:3"><rect x="410" y="84" width="110" height="52" rx="9"/></g><text x="465.0" y="107.0" class="dg-t" text-anchor="middle" style="--d:3">manifests</text><text x="465.0" y="125.0" class="dg-s" text-anchor="middle" style="--d:3">YAML final</text><path d="M366 110 L408 110" class="dg-l c flow" marker-end="url(#g15-c)"/><rect x="540" y="14" width="126" height="222" rx="12" class="dg-zone "/><text x="552" y="32" class="dg-zl" text-anchor="start">release api</text><g class="dg-box dg-off dg-pop" style="--d:4"><rect x="556" y="44" width="94" height="40" rx="9"/></g><text x="603.0" y="69.0" class="dg-t" text-anchor="middle" style="--d:4">rév. 1</text><g class="dg-box dg-pop" style="--d:5"><rect x="556" y="106" width="94" height="40" rx="9"/></g><text x="603.0" y="131.0" class="dg-t" text-anchor="middle" style="--d:5">rév. 2</text><g class="dg-box dg-c dg-pop" style="--d:6"><rect x="556" y="168" width="94" height="40" rx="9"/></g><text x="603.0" y="193.0" class="dg-t" text-anchor="middle" style="--d:6">rév. 3</text><path d="M520 110 L538 110" class="dg-l" marker-end="url(#g15-n)"/><path d="M650 188 C 674 176, 674 138, 652 126" class="dg-l a dash" marker-end="url(#g15-a)"/><text x="612" y="232" class="dg-at" text-anchor="middle">rollback → rév. 2</text></svg><figcaption>Les valeurs se superposent : défauts du chart, puis tes fichiers -f, puis les --set. Chaque upgrade crée une révision.</figcaption></figure>
<!-- /schema:helm -->

## Comprendre ce que fait Helm

Helm fait deux choses distinctes :

1. **Générer** du YAML : il prend les fichiers de `templates/`, remplace les `{{ … }}` par les valeurs (du `values.yaml`, puis de tes fichiers `-f`, puis des `--set`), et produit des manifestes Kubernetes ordinaires. `helm template` montre ce résultat sans rien installer.
2. **Suivre** ce qu'il a installé : chaque installation est une **release** (un nom, comme `api`, dans un namespace). À chaque `upgrade`, Helm enregistre une **révision** (dans un Secret du namespace) avec les manifestes appliqués. C'est ce qui permet `helm history` et `helm rollback`, et qui lui fait supprimer les objets retirés du chart.

Le langage des templates est celui de Go : `.Values` pour les valeurs, `.Chart` pour les métadonnées du chart, `.Release` pour la release (`.Release.Name`, `.Release.Namespace`). Les `|` enchaînent des fonctions : `toYaml .Values.resources | nindent 12` convertit un bloc de valeurs en YAML et l'indente de 12 espaces. L'indentation est la principale source d'erreurs des charts : `helm template` et `helm lint` les révèlent avant le déploiement.

## Version du chart et version de l'appli

`Chart.yaml` porte deux versions : `version` (celle du **chart**, qui change quand on modifie les templates) et `appVersion` (celle de l'**application** packagée, souvent utilisée comme tag d'image par défaut). On peut publier une nouvelle version de chart sans changer l'appli, et inversement.

## Le cycle de vie

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm upgrade --install api ./api -n shop --create-namespace -f values-prod.yaml
helm list -n shop
helm get values api -n shop         # valeurs utilisées
helm history api -n shop
helm rollback api 3 -n shop
helm uninstall api -n shop
```

## Valeurs : qui gagne ?

```
values.yaml du chart  <  -f values-commun.yaml  <  -f values-prod.yaml  <  --set image.tag=2.1
```

> **Piège classique.** Les `--set` ne sont pas mémorisés d'un upgrade à l'autre. Un fichier de valeurs par environnement, versionné dans Git, évite de déployer par erreur une ancienne version.

```bash
helm template api ./api -f values-prod.yaml | kubectl apply --dry-run=server -f -
helm lint ./api
```

> **À retenir.** Helm génère des manifestes à partir de templates et de valeurs, puis suit chaque installation (release) révision par révision, d'où `helm history` et `helm rollback`. Garde un fichier de valeurs par environnement dans Git, et vérifie le rendu avec `helm template` et `helm lint` avant de déployer.
