---
title: grep, sed, awk et jq
chapter: 8
order: 2
duration: 9
level: intermédiaire
tags:
- LFCS
cards:
- q: Comment chercher récursivement un mot en affichant les numéros de ligne ?
  a: '`grep -rn ''timeout'' /etc/nginx/`. `-i` ignore la casse, `-v` inverse, `-E` active les regex étendues, `-C 3` ajoute du contexte.'
- q: Comment remplacer un texte dans un fichier, sur place ?
  a: '`sed -i ''s/ancien/nouveau/g'' fichier`. Sur macOS : `sed -i '''' ''s/…/…/g''`.'
- q: Comment afficher la 1re et la 9e colonne d'un log nginx avec awk ?
  a: '`awk ''{print $1, $9}'' access.log` : IP du client et code HTTP.'
- q: Comment compter les occurrences de chaque valeur d'une colonne ?
  a: '`awk ''{print $9}'' access.log | sort | uniq -c | sort -rn | head`.'
- q: Comment extraire un champ d'un JSON en ligne de commande ?
  a: 'Avec **jq** : `kubectl get pods -o json | jq -r ''.items[].metadata.name''`.'
- q: À quoi sert `xargs` ?
  a: 'À transformer une liste reçue sur l''entrée en **arguments** d''une commande : `find . -name ''*.tmp'' -print0 | xargs -0 rm`.'
quiz:
- q: Quelle commande donne les 10 IP qui font le plus de requêtes dans `access.log` ?
  options:
  - grep -c ip access.log
  - awk '{print $1}' access.log | sort | uniq -c | sort -rn | head
  - sed -n 1,10p access.log
  - cut -d' ' -f1 access.log | head
  answer: 1
  explain: '`uniq -c` ne compte que les lignes **consécutives** identiques, d''où le `sort` avant.'
- q: Comment lister les pods qui ne sont pas en `Running` avec jq ?
  options:
  - jq '.items[] | select(.status.phase != "Running") | .metadata.name'
  - jq '.Running'
  - jq -v Running
  - jq '.items | length'
  answer: 0
  explain: '`select()` filtre les éléments. Ajoute `-r` pour avoir les noms sans guillemets.'
---

Ces outils se combinent avec des pipes. Le principe : chacun fait une seule chose, bien.


> **Les termes et outils cités dans cette fiche.**
> - **JSON** : un format texte de données en paires « clé : valeur », lisible par les humains et les programmes.
> - **YAML** : un format de fichier texte structuré par l'indentation, utilisé par Kubernetes, Ansible, GitLab CI…

## grep : trouver

```bash
grep -rn --include='*.yaml' 'image:' k8s/
grep -E 'error|fatal' app.log | grep -v healthcheck
grep -c ' 500 ' access.log          # compter
```

## sed : transformer

```bash
sed -i 's/replicas: 2/replicas: 3/' deploy.yaml
sed -n '120,140p' app.log           # afficher des lignes précises
sed '/^#/d; /^$/d' nginx.conf       # retirer commentaires et lignes vides
```

## awk : travailler par colonnes

```bash
awk '{print $1, $9}' access.log
awk '$9 >= 500 {n++} END {print n " erreurs"}' access.log
awk -F: '$3 >= 1000 {print $1}' /etc/passwd     # utilisateurs « humains »
df -h | awk 'NR>1 && $5+0 > 80 {print $6, $5}'    # disques à plus de 80 %
```

## sort, uniq, cut, wc

```bash
cut -d, -f2 export.csv | sort | uniq -c | sort -rn | head
wc -l *.log
```

## jq : le JSON

```bash
kubectl get pods -A -o json \
  | jq -r '.items[] | select(.status.phase != "Running") | "\(.metadata.namespace)/\(.metadata.name)"'
aws ec2 describe-instances | jq -r '.Reservations[].Instances[] | [.InstanceId, .State.Name] | @tsv'
```

## Le principe des pipes

Le `|` branche la **sortie** d'une commande sur l'**entrée** de la suivante. Chaque outil lit du texte ligne par ligne et en recrache : c'est pourquoi on peut les combiner à l'infini. Un pipeline se lit de gauche à droite comme une recette :

```bash
cut -d, -f2 export.csv | sort | uniq -c | sort -rn | head
#  prendre la colonne 2  │ trier │ compter les doublons │ trier par nombre │ garder le top 10
```

`uniq` ne fusionne que des lignes **adjacentes** : il faut presque toujours `sort` avant.

Deux autres flux comptent : la **sortie d'erreur** (`2>`) n'entre pas dans le pipe par défaut. `cmd 2>&1 | grep x` y ajoute les erreurs ; `2>/dev/null` les fait taire.

## Choisir le bon outil

| Besoin | Outil | Pourquoi |
| --- | --- | --- |
| garder les lignes qui contiennent quelque chose | `grep` | le plus rapide, `-v` pour l'inverse |
| remplacer du texte, supprimer des lignes | `sed` | édition ligne par ligne, `-i` pour modifier le fichier |
| raisonner par colonnes, calculer, conditionner | `awk` | c'est un petit langage : variables, `if`, sommes |
| interroger du JSON | `jq` | `grep` et `sed` cassent dès que le format bouge |
| du YAML | `yq` | même syntaxe que `jq` |

## Les expressions régulières, en bref

`grep -E` et `sed -E` utilisent des **regex**, un mini-langage pour décrire des motifs :

| Motif | Signifie |
| --- | --- |
| `^` / `$` | début / fin de ligne |
| `.` | n'importe quel caractère |
| `*`, `+`, `?` | zéro ou plus, un ou plus, zéro ou un du précédent |
| `[0-9]`, `[a-z]` | un caractère de cette plage |
| `(a\|b)` avec `-E` | a ou b |

Exemple : `grep -E '^[0-9.]+ .* (5[0-9]{2}) '` garde les lignes de log d'accès avec un code 5xx.

Toujours tester un `sed -i` **sans** `-i` d'abord : il affiche le résultat sans toucher au fichier.

> **À retenir.** Construis un pipeline pas à pas : lance la première commande, regarde la sortie, ajoute le maillon suivant. C'est plus rapide que d'écrire tout d'un coup et de déboguer ensuite.
