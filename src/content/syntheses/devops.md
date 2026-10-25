---
title: Synthèse DevOps
description: "Git, CI/CD, GitLab CI, Ansible, GitOps, observabilité, stratégies de déploiement et SRE."
---

## Git au quotidien

```bash
git switch -c feat/api            # nouvelle branche
git add -p                        # ajouter par morceaux
git commit --amend --no-edit      # corriger le dernier commit (non poussé)
git rebase -i origin/main         # réorganiser ses commits avant la MR
git rebase --continue / --abort
git cherry-pick SHA
git stash push -m "wip"  /  git stash pop
git log --oneline --graph --all
git reflog                        # retrouver un commit « perdu »
git bisect start / good / bad     # trouver le commit fautif
git reset --soft HEAD~1           # annuler le commit, garder les changements
git revert SHA                    # annuler un commit déjà partagé
git push --force-with-lease       # forcer sans écraser le travail d'un autre
```

## Les principes du CI/CD

- **Petit, souvent, automatiquement** : un changement petit se relit, se teste et s'annule facilement.
- **Un artefact** construit une fois, tagué avec le SHA, promu tel quel de staging à prod.
- **Configuration externe** : pas de rebuild par environnement.
- **Livraison continue** (prêt à partir, un humain décide) ≠ **déploiement continu** (part tout seul).

| Mesure DORA | Question |
| --- | --- |
| Fréquence de déploiement | À quelle fréquence livre-t-on ? |
| Délai de mise en production | Combien de temps du commit à la prod ? |
| Taux d'échec des changements | Quelle part des déploiements cause un incident ? |
| Temps de restauration | Combien de temps pour rétablir le service ? |

## GitLab CI

| Mot-clé | Rôle |
| --- | --- |
| `stages` | Ordre des étapes |
| `image`, `services` | Conteneur du job, services annexes (base de test) |
| `script`, `before_script` | Commandes |
| `rules` | Quand lancer le job (branche, MR, fichiers modifiés) |
| `needs` | Lancer dès qu'un job précis a fini (DAG) |
| `artifacts` / `cache` | Fichiers transmis aux jobs suivants / réutilisés entre pipelines |
| `extends`, `include` | Réutiliser une configuration |
| `environment` | Suivi des déploiements par environnement |
| `when: manual` | Bouton de validation humaine |
| `id_tokens` | Jeton OIDC pour s'authentifier au cloud sans secret statique |

## Ansible

```bash
ansible all -i inventory -m ping
ansible-playbook -i inventory/prod site.yml --check --diff
ansible-playbook site.yml --limit web01 --tags nginx
ansible-vault encrypt group_vars/prod/vault.yml
ansible-inventory -i inventory --graph
```

- Idempotence : relancer ne doit afficher que des `ok`. Éviter `command` / `shell`, ou ajouter `creates` / `changed_when`.
- Handlers : exécutés une fois en fin de play, seulement si notifiés par un `changed`.
- Variables : `defaults` du rôle < `group_vars` < `host_vars` < `-e`.
- `serial` pour mettre à jour le parc par lots.

## GitOps avec ArgoCD

- **Git est la seule source de vérité**, un agent dans le cluster **tire** l'état (pull).
- États : **Synced / OutOfSync** (conforme à Git ?) et **Healthy / Degraded** (ça marche ?).
- `selfHeal` annule les changements manuels, `prune` supprime ce qui a été retiré de Git.
- App of apps et **ApplicationSet** pour gérer plusieurs apps et clusters.
- Sync waves : CRD et namespaces d'abord, l'application ensuite.
- Secrets : Sealed Secrets, External Secrets Operator ou SOPS.

```bash
argocd app list
argocd app diff api
argocd app sync api
argocd app history api  /  argocd app rollback api ID
```

## Les stratégies de déploiement

| Stratégie | Principe | Retour arrière | Coût |
| --- | --- | --- | --- |
| Recreate | Tout arrêter, tout redémarrer | Redéployer | Coupure |
| Rolling update | Remplacer les pods petit à petit | `rollout undo` | Faible |
| Blue/green | Deux environnements, bascule du trafic | Rebasculer, instantané | Double infra pendant la bascule |
| Canary | Une petite part du trafic sur la nouvelle version | Couper le canary | Outillage (Argo Rollouts, mesh) |
| Feature flags | Code déployé, fonctionnalité activée à la demande | Désactiver le flag | Dette de flags à nettoyer |

## L'observabilité

| Signal | Question | Outils |
| --- | --- | --- |
| Métriques | Combien, à quelle vitesse ? | Prometheus, Grafana |
| Logs | Que s'est-il passé ? | Loki, Elasticsearch |
| Traces | Où passe le temps d'une requête ? | OpenTelemetry, Tempo, Jaeger |

- **Golden signals** : latence, trafic, erreurs, saturation.
- **RED** pour les services (Rate, Errors, Duration), **USE** pour les ressources (Utilisation, Saturation, Erreurs).
- Alerter sur les **symptômes** vus par l'utilisateur, pas sur chaque cause possible.

```promql
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))
histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))
```

## SRE

- **SLI** : la mesure (part des requêtes réussies en moins de 300 ms).
- **SLO** : l'objectif (99,9 % sur 30 jours).
- **Budget d'erreur** : 100 % − SLO. Budget épuisé : on ralentit les mises en production et on fiabilise.
- **Postmortem sans reproche** : chronologie, cause, ce qui a aidé, actions avec un responsable.
- **Toil** : travail manuel répétitif à automatiser.
