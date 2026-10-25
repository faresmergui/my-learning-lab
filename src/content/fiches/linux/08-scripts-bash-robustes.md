---
title: Scripts bash robustes
chapter: 8
order: 1
duration: 9
level: intermédiaire
tags:
- LFCS
cards:
- q: Que fait `set -euo pipefail` ?
  a: '`-e` : arrête le script à la première erreur. `-u` : erreur si une variable n''est pas définie. `-o pipefail` : un pipe échoue si **une** de ses commandes échoue, pas seulement la dernière.'
- q: Pourquoi toujours écrire `"$var"` avec des guillemets ?
  a: Sans guillemets, bash découpe la valeur sur les espaces et interprète les `*`. Un fichier nommé `mon rapport.csv` devient deux arguments.
- q: Différence entre `[ ]` et `[[ ]]` ?
  a: '`[[ ]]` est propre à bash : pas de découpage des variables, et il gère `&&`, `||`, `=~` (regex) et les motifs. `[ ]` est la commande POSIX `test`.'
- q: À quoi sert `trap` ?
  a: 'À exécuter du code sur un signal ou à la sortie du script, par exemple pour nettoyer : `trap ''rm -rf "$tmp"'' EXIT`.'
- q: Comment donner une valeur par défaut à une variable ?
  a: '`${PORT:-8080}` : utilise `8080` si `PORT` est vide ou non définie. `${VAR:?message}` arrête le script avec un message.'
- q: Quel outil analyse un script bash et signale les erreurs classiques ?
  a: '**ShellCheck** (`shellcheck script.sh`), à brancher dans l''éditeur et dans la CI.'
quiz:
- q: Ton script contient `rm -rf "$DIR/"*`, et `DIR` est vide par erreur. Quelle protection l'aurait arrêté ?
  options:
  - set -x
  - Écrire `${DIR:?}` dans la commande
  - set -e
  - shopt -s nullglob
  answer: 1
  explain: Avec une variable vide, la commande devient `rm -rf /*`. `set -u` n'aide que si `DIR` n'est pas définie du tout. `${DIR:?DIR non défini}` arrête aussi le script quand elle est vide.
- q: '`curl … | jq .` échoue sur le curl, mais le script continue malgré `set -e`. Pourquoi ?'
  options:
  - '`set -e` ne marche pas avec curl'
  - Sans `pipefail`, seul le code de retour de `jq` compte
  - jq ignore les erreurs
  - Il faut `set -x`
  answer: 1
  explain: C'est exactement le rôle de `-o pipefail`.
---

Un script de quelques lignes devient vite un outil dont dépend toute l'équipe. Quelques habitudes évitent la plupart des catastrophes.


> **Les termes et outils cités dans cette fiche.**
> - **CI** : l'intégration continue : chaque modification de code est automatiquement construite et testée.
> - **JSON** : un format texte de données en paires « clé : valeur », lisible par les humains et les programmes.
> - **commit** : un instantané enregistré des modifications dans Git, avec un message et un auteur.

## Le modèle de départ

```bash
#!/usr/bin/env bash
set -euo pipefail

ENV="${1:?Usage: $0 <env>}"
PORT="${PORT:-8080}"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

log() { printf '[%s] %s\n' "$(date +%T)" "$*" >&2; }

main() {
  log "Déploiement sur $ENV (port $PORT)"
  if [[ "$ENV" =~ ^(staging|prod)$ ]]; then
    kubectl --context "$ENV" apply -k "overlays/$ENV"
  else
    log "Environnement inconnu : $ENV"
    exit 1
  fi
}
main "$@"
```

## Les règles d'or

| Règle | Pourquoi |
| --- | --- |
| `set -euo pipefail` | s'arrêter au lieu de continuer sur une erreur |
| Guillemets partout : `"$var"` | éviter le découpage et les jokers |
| `$(cmd)` plutôt que les backticks | lisible, imbriquable |
| `[[ … ]]` en bash | plus sûr que `[ … ]` |
| `local` dans les fonctions | ne pas écraser les variables globales |
| `mktemp` + `trap … EXIT` | fichiers temporaires toujours nettoyés |
| `shellcheck` | attraper le reste |

## Boucler proprement sur des fichiers

```bash
while IFS= read -r -d '' f; do
  gzip -- "$f"
done < <(find /var/log/api -name '*.log' -mtime +7 -print0)
```

> **Piège classique.** `for f in $(ls *.log)` casse sur les noms avec espaces. Utilise `for f in *.log` ou `find -print0` avec `read -d ''`.

## Ce que fait vraiment `set -euo pipefail`

Par défaut, bash est très tolérant : une commande échoue, il passe à la suivante. Dans un script de déploiement, c'est dangereux. Imagine :

```bash
cd /srv/app/releases/old
rm -rf *
```

Si le `cd` échoue (répertoire absent), le `rm` s'exécute **dans le répertoire courant**. Les trois options changent ce comportement :

- **`-e`** : le script s'arrête dès qu'une commande renvoie une erreur (code de retour différent de 0) ;
- **`-u`** : utiliser une variable non définie est une erreur. Sans ça, `rm -rf "$DIR/"` avec `DIR` mal orthographié devient `rm -rf "/"` ;
- **`-o pipefail`** : un pipeline échoue si **n'importe quelle** commande échoue, pas seulement la dernière. Sans ça, `curl … | jq …` « réussit » même si `curl` a échoué.

## Le code de retour

Chaque commande renvoie un nombre : **0 = succès**, tout le reste = échec. C'est ce que testent `if`, `&&`, `||` et `set -e`. `$?` contient celui de la dernière commande. Ton script doit lui aussi sortir avec un code non nul en cas d'erreur (`exit 1`), sinon la CI ou cron croiront qu'il a réussi.

## Pourquoi les guillemets partout

Sans guillemets, bash **découpe** la valeur d'une variable sur les espaces et **développe** les jokers (`*`). Avec `f="mon fichier.log"`, `rm $f` tente de supprimer `mon` et `fichier.log`. `rm "$f"` supprime le bon fichier. La règle simple : toujours `"$var"`, sauf si tu sais exactement pourquoi tu ne le fais pas.

## Les expansions utiles du modèle

| Syntaxe | Effet |
| --- | --- |
| `${1:?message}` | erreur avec ce message si le premier argument est absent |
| `${PORT:-8080}` | valeur par défaut si `PORT` est vide ou absente |
| `"$@"` | tous les arguments, chacun préservé |
| `trap '…' EXIT` | code exécuté à la sortie du script, même en cas d'erreur |

## Quand arrêter le bash

Au-delà d'une centaine de lignes, de structures de données ou de JSON à manipuler, un script Python ou Go sera plus lisible et plus testable. Bash excelle pour enchaîner des commandes, pas pour programmer.

> **À retenir.** `set -euo pipefail`, des guillemets autour de chaque variable, `mktemp` + `trap … EXIT`, et `shellcheck` avant chaque commit. Au-delà d'une centaine de lignes ou dès qu'il faut manipuler des données, passe à Python.
