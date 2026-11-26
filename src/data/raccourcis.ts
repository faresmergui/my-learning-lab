// Shortcuts cheat sheet, shown on /raccourcis/.
// To add a shortcut: append a line [keys, description] to the right section.
// Keys: tokens separated by spaces, each one drawn as a key (⌘ ⇧ P → three keys).
// A lone "/" is drawn as "or". In a section with `cmd: true` the keys are a
// command typed as-is, shown as code. Mac notation: ⌘ cmd, ⌃ ctrl, ⌥ option, ⇧ shift.
// `star: true` on a line (third item) marks a shortcut worth learning first.

export type Shortcut = [keys: string, desc: string, star?: boolean];
export interface Section { title: string; cmd?: boolean; items: Shortcut[] }
export interface Tool { id: string; title: string; color: string; note?: string; sections: Section[] }

export const tools: Tool[] = [
  {
    id: 'vim', title: 'Vim', color: '#34d399',
    note: 'Échap pour revenir en mode normal. Un nombre devant répète : 5j, 3dd, 2w.',
    sections: [
      { title: 'Modes', items: [
        ['i', 'Insérer avant le curseur', true], ['a', 'Insérer après le curseur'],
        ['I', 'Insérer en début de ligne'], ['A', 'Insérer en fin de ligne', true],
        ['o', 'Nouvelle ligne en dessous', true], ['O', 'Nouvelle ligne au-dessus'],
        ['v', 'Sélection caractère'], ['V', 'Sélection ligne', true], ['⌃V', 'Sélection bloc (colonne)'],
        ['Échap / ⌃[', 'Revenir en mode normal'],
      ] },
      { title: 'Se déplacer', items: [
        ['h j k l', 'Gauche, bas, haut, droite'],
        ['w b e', 'Mot suivant, précédent, fin du mot', true],
        ['0 ^ $', 'Début de ligne, 1er caractère, fin de ligne', true],
        ['gg G', 'Début, fin du fichier', true], ['42G / :42', 'Aller à la ligne 42'],
        ['⌃D ⌃U', 'Descendre, monter d’une demi-page'],
        ['%', 'Parenthèse ou accolade correspondante'],
        ['f x / t x', 'Sauter sur (f) ou avant (t) le caractère x ; ; répète'],
        ['{ }', 'Paragraphe précédent, suivant'], ['zz', 'Centrer l’écran sur le curseur'],
      ] },
      { title: 'Éditer', items: [
        ['x', 'Supprimer le caractère'], ['dd', 'Couper la ligne', true], ['yy', 'Copier la ligne', true],
        ['p P', 'Coller après, avant', true], ['u', 'Annuler', true], ['⌃R', 'Rétablir', true],
        ['.', 'Répéter la dernière modification', true], ['cw', 'Remplacer jusqu’à la fin du mot'],
        ['ciw', 'Remplacer le mot entier', true], ['ci"', 'Remplacer le texte entre guillemets'],
        ['dt x', 'Supprimer jusqu’au caractère x'], ['D / C', 'Couper / remplacer jusqu’à la fin de ligne'],
        ['r x', 'Remplacer un caractère par x'], ['>> <<', 'Indenter, désindenter'],
        ['J', 'Joindre la ligne suivante'], ['~', 'Inverser la casse'],
      ] },
      { title: 'Chercher et remplacer', items: [
        ['/motif', 'Chercher vers le bas', true], ['?motif', 'Chercher vers le haut'],
        ['n N', 'Résultat suivant, précédent', true], ['*', 'Chercher le mot sous le curseur'],
        [':%s/a/b/g', 'Remplacer a par b dans tout le fichier', true],
        [':%s/a/b/gc', 'Idem en confirmant chaque remplacement'], [':noh', 'Effacer le surlignage'],
      ] },
      { title: 'Fichiers et fenêtres', items: [
        [':w', 'Enregistrer'], [':q', 'Quitter'], [':wq / ZZ', 'Enregistrer et quitter', true],
        [':q!', 'Quitter sans enregistrer', true], [':e fichier', 'Ouvrir un fichier'],
        [':sp / :vs', 'Couper la fenêtre horizontalement / verticalement'],
        ['⌃W w', 'Passer à la fenêtre suivante'], [':set nu', 'Afficher les numéros de ligne'],
        [':set paste', 'Coller sans indentation automatique'],
      ] },
    ],
  },
  {
    id: 'terminal', title: 'Terminal', color: '#f2c94c',
    note: 'Raccourcis readline : bash, zsh, et la plupart des invites (python, psql…). Sur Mac, ⌥ comme Méta s’active dans Terminal > Réglages > Profils > Clavier.',
    sections: [
      { title: 'Ligne de commande', items: [
        ['⌃A', 'Début de ligne', true], ['⌃E', 'Fin de ligne', true],
        ['⌥B ⌥F', 'Mot précédent, suivant'], ['⌃W', 'Effacer le mot avant le curseur', true],
        ['⌃U', 'Effacer jusqu’au début de ligne', true], ['⌃K', 'Effacer jusqu’à la fin de ligne'],
        ['⌃Y', 'Recoller ce qui vient d’être effacé'], ['⌃_', 'Annuler la dernière modif'],
        ['⌃X ⌃E', 'Éditer la commande dans $EDITOR (vim)'], ['Tab Tab', 'Lister les complétions'],
      ] },
      { title: 'Historique', items: [
        ['⌃R', 'Rechercher dans l’historique (⌃R encore = plus ancien)', true],
        ['⌃G', 'Sortir de la recherche'], ['↑ ↓ / ⌃P ⌃N', 'Commande précédente, suivante'],
        ['!!', 'Relancer la dernière commande (sudo !!)', true], ['!$ / ⌥.', 'Dernier argument de la commande précédente', true],
        ['!git', 'Relancer la dernière commande qui commence par git'],
      ] },
      { title: 'Processus et écran', items: [
        ['⌃C', 'Interrompre la commande', true], ['⌃D', 'Fin d’entrée / quitter le shell'],
        ['⌃Z', 'Suspendre (fg pour reprendre, bg en arrière-plan)'], ['⌃L', 'Effacer l’écran', true],
        ['⌃S ⌃Q', 'Geler, dégeler l’affichage (si l’écran ne répond plus : ⌃Q)'],
      ] },
      { title: 'Terminal.app / iTerm2', items: [
        ['⌘T', 'Nouvel onglet'], ['⌘W', 'Fermer l’onglet'], ['⌘⇧[ ⌘⇧]', 'Onglet précédent, suivant'],
        ['⌘K', 'Vider l’écran et l’historique visible'], ['⌘D', 'iTerm2 : couper verticalement'],
        ['⌘⇧D', 'iTerm2 : couper horizontalement'], ['⌘[ ⌘]', 'iTerm2 : volet précédent, suivant'],
        ['⌘F', 'Chercher dans la sortie'], ['⌘+ ⌘-', 'Agrandir, réduire le texte'],
      ] },
    ],
  },
  {
    id: 'tmux', title: 'tmux', color: '#22d3ee',
    note: 'Tout commence par le préfixe ⌃B (relâcher, puis la touche).',
    sections: [
      { title: 'Sessions', items: [
        ['tmux new -s nom', 'Nouvelle session nommée'], ['tmux a -t nom', 'Se rattacher à une session', true],
        ['tmux ls', 'Lister les sessions'], ['⌃B d', 'Se détacher (la session continue)', true],
        ['⌃B s', 'Choisir une session'], ['⌃B $', 'Renommer la session'],
      ] },
      { title: 'Fenêtres', items: [
        ['⌃B c', 'Nouvelle fenêtre', true], ['⌃B n / ⌃B p', 'Fenêtre suivante, précédente'],
        ['⌃B 0…9', 'Aller à la fenêtre n'], ['⌃B ,', 'Renommer la fenêtre'], ['⌃B w', 'Liste des fenêtres'],
        ['⌃B &', 'Fermer la fenêtre'],
      ] },
      { title: 'Volets', items: [
        ['⌃B %', 'Couper verticalement', true], ['⌃B "', 'Couper horizontalement', true],
        ['⌃B ←↑→↓', 'Changer de volet'], ['⌃B z', 'Zoomer, dézoomer le volet', true],
        ['⌃B x', 'Fermer le volet'], ['⌃B Espace', 'Changer de disposition'],
        ['⌃B [', 'Mode copie / défilement (q pour sortir)'],
      ] },
    ],
  },
  {
    id: 'git', title: 'Git', color: '#fb923c',
    sections: [
      { title: 'Au quotidien', cmd: true, items: [
        ['git status -sb', 'État court avec la branche', true], ['git add -p', 'Ajouter morceau par morceau', true],
        ['git commit --amend --no-edit', 'Ajouter au dernier commit (pas encore poussé)'],
        ['git switch -c ma-branche', 'Créer une branche et y aller', true], ['git switch -', 'Revenir à la branche précédente'],
        ['git pull --rebase', 'Récupérer sans commit de merge', true], ['git push -u origin HEAD', 'Pousser la branche courante'],
      ] },
      { title: 'Regarder', cmd: true, items: [
        ['git log --oneline --graph -20', 'Historique compact', true], ['git diff --staged', 'Ce qui partira dans le commit'],
        ['git show HEAD', 'Le dernier commit'], ['git blame -L 10,20 f', 'Qui a écrit ces lignes'],
        ['git log -S "texte"', 'Commits qui ont ajouté ou retiré ce texte'],
      ] },
      { title: 'Réparer', cmd: true, items: [
        ['git restore f', 'Annuler les modifs non indexées d’un fichier'], ['git restore --staged f', 'Désindexer un fichier'],
        ['git reset --soft HEAD~1', 'Défaire le dernier commit, garder les modifs', true],
        ['git stash / git stash pop', 'Mettre de côté, puis reprendre', true],
        ['git reflog', 'Retrouver un commit « perdu »', true], ['git revert <sha>', 'Annuler un commit déjà poussé'],
        ['git rebase -i HEAD~3', 'Réécrire les 3 derniers commits (branche à soi)'],
      ] },
    ],
  },
  {
    id: 'kubectl', title: 'kubectl (CKA)', color: '#4f7cf0',
    note: 'À taper en début d’examen : alias k=kubectl, complete -o default -F __start_kubectl k, export do="--dry-run=client -o yaml".',
    sections: [
      { title: 'Lire', cmd: true, items: [
        ['k get po -A -o wide', 'Tous les pods, avec nœud et IP', true], ['k describe po nom', 'Détails et événements', true],
        ['k logs nom -c ctn -f', 'Logs d’un conteneur, en continu'], ['k logs nom --previous', 'Logs du conteneur qui a planté', true],
        ['k get events --sort-by=.lastTimestamp', 'Événements dans l’ordre'], ['k explain pod.spec --recursive', 'Champs d’une ressource, sans la doc', true],
        ['k api-resources', 'Noms courts : po, deploy, svc, cm, pvc…'], ['k auth can-i create pod --as=u', 'Tester un droit RBAC'],
      ] },
      { title: 'Créer vite', cmd: true, items: [
        ['k run p --image=nginx $do > p.yaml', 'Squelette de pod', true], ['k create deploy d --image=nginx --replicas=3 $do', 'Squelette de déploiement', true],
        ['k expose deploy d --port=80 --type=NodePort', 'Service devant un déploiement'], ['k create cm c --from-literal=k=v', 'ConfigMap'],
        ['k create secret generic s --from-literal=k=v', 'Secret'], ['k create role r --verb=get --resource=pods', 'Rôle RBAC'],
        ['k create rolebinding rb --role=r --user=u', 'Lier le rôle'],
      ] },
      { title: 'Agir', cmd: true, items: [
        ['k config set-context --current --namespace=ns', 'Changer de namespace par défaut', true],
        ['k scale deploy d --replicas=5', 'Mettre à l’échelle'], ['k set image deploy d nginx=nginx:1.27', 'Changer d’image'],
        ['k rollout undo deploy d', 'Revenir à la version précédente', true], ['k exec -it nom -- sh', 'Shell dans le pod'],
        ['k delete po nom --force --grace-period=0', 'Supprimer tout de suite (gain de temps)'],
        ['k drain node --ignore-daemonsets', 'Vider un nœud', true], ['k uncordon node', 'Remettre le nœud en service'],
      ] },
    ],
  },
  {
    id: 'macos', title: 'macOS', color: '#8a8f9d',
    sections: [
      { title: 'Système', items: [
        ['⌘ Espace', 'Spotlight', true], ['⌘ Tab', 'Changer d’app'], ['⌘ `', 'Changer de fenêtre dans la même app'],
        ['⌘Q', 'Quitter l’app'], ['⌘H', 'Masquer l’app'], ['⌘M', 'Réduire la fenêtre'],
        ['⌘⌥ Échap', 'Forcer à quitter', true], ['⌃⌘Q', 'Verrouiller l’écran', true],
        ['⌃ ↑', 'Mission Control'], ['⌃ ← →', 'Bureau précédent, suivant'],
      ] },
      { title: 'Captures', items: [
        ['⌘⇧3', 'Capture de tout l’écran'], ['⌘⇧4', 'Capture d’une zone', true],
        ['⌘⇧4 Espace', 'Capture d’une fenêtre'], ['⌘⇧5', 'Outil capture et enregistrement vidéo', true],
        ['⌃ + capture', 'Copier dans le presse-papiers au lieu d’un fichier'],
      ] },
      { title: 'Texte et Finder', items: [
        ['⌥ ← →', 'Mot précédent, suivant'], ['⌘ ← →', 'Début, fin de ligne'], ['⌥ ⌫', 'Effacer le mot'],
        ['⌘⌃ Espace', 'Emojis et symboles'], ['⌘⇧.', 'Afficher les fichiers cachés', true],
        ['⌘⇧G', 'Aller au dossier (taper un chemin)', true], ['⌥⌘C', 'Copier le chemin du fichier'],
        ['Espace', 'Coup d’œil (Quick Look)'], ['⌘ ⌫', 'Mettre à la corbeille'], ['⌘⌥V', 'Déplacer (après ⌘C)'],
      ] },
    ],
  },
  {
    id: 'zen', title: 'Zen', color: '#e03a46',
    note: 'Zen reprend les raccourcis de Firefox. Liste complète et personnalisation : Réglages > Raccourcis clavier.',
    sections: [
      { title: 'Onglets', items: [
        ['⌘T', 'Nouvel onglet'], ['⌘W', 'Fermer l’onglet'], ['⌘⇧T', 'Rouvrir l’onglet fermé', true],
        ['⌘1…8 / ⌘9', 'Aller à l’onglet n / au dernier'], ['⌃ Tab', 'Onglet suivant'],
        ['⌘L', 'Barre d’adresse', true], ['⌘⇧P', 'Fenêtre privée'], ['⌘F', 'Chercher dans la page'],
        ['⌘⇧R', 'Recharger sans cache'], ['⌘⇧C', 'Copier l’URL de la page (Zen)', true],
        ['⌃⌥⇧C', 'Copier l’URL au format Markdown (Zen)'],
      ] },
      { title: 'Spécifique Zen', items: [
        ['⌃⌥C', 'Mode compact', true], ['⌃⌥S', 'Barre latérale flottante'], ['⌃⌥T', 'Barre d’outils flottante'],
        ['⌃⌥E / ⌃⌥Q', 'Espace de travail suivant, précédent', true],
        ['⌃⌥V / ⌃⌥H', 'Vue scindée verticale, horizontale (onglets sélectionnés)', true],
        ['⌃⌥G', 'Vue scindée en grille'], ['⌃⌥U', 'Fermer la vue scindée'],
      ] },
    ],
  },
  {
    id: 'vscode', title: 'VS Code', color: '#3b82f6',
    sections: [
      { title: 'Naviguer', items: [
        ['⌘⇧P', 'Palette de commandes', true], ['⌘P', 'Ouvrir un fichier par son nom', true],
        ['⌃G', 'Aller à la ligne'], ['⌘⇧O', 'Aller à un symbole du fichier'], ['F12', 'Aller à la définition'],
        ['⌃ -', 'Revenir en arrière'], ['⌘B', 'Afficher, masquer la barre latérale'], ['⌃ `', 'Terminal intégré', true],
        ['⌘⇧F', 'Chercher dans tout le projet'], ['⌘\\', 'Couper l’éditeur'],
      ] },
      { title: 'Éditer', items: [
        ['⌘D', 'Sélectionner l’occurrence suivante', true], ['⌘⇧L', 'Sélectionner toutes les occurrences'],
        ['⌥⌘ ↑ ↓', 'Curseur sur la ligne au-dessus, en dessous'], ['⌥ ↑ ↓', 'Déplacer la ligne', true],
        ['⌥⇧ ↑ ↓', 'Dupliquer la ligne'], ['⌘⇧K', 'Supprimer la ligne'], ['⌘/', 'Commenter', true],
        ['F2', 'Renommer le symbole partout'], ['⌥⇧F', 'Formater le fichier'], ['⌘.', 'Correctif rapide'],
      ] },
    ],
  },
  {
    id: 'obsidian', title: 'Obsidian', color: '#8b5cf6',
    sections: [
      { title: 'Essentiels', items: [
        ['⌘O', 'Ouvrir une note (recherche rapide)', true], ['⌘P', 'Palette de commandes', true],
        ['⌘N', 'Nouvelle note'], ['⌘⇧F', 'Chercher dans le coffre'], ['⌘E', 'Lecture / édition', true],
        ['⌘ clic', 'Ouvrir le lien dans un nouvel onglet'], ['[[', 'Insérer un lien vers une note', true],
        ['⌘K', 'Insérer un lien Markdown'], ['⌘⌥ ←  →', 'Note précédente, suivante'], ['⌘G', 'Vue graphe'],
        ['⌘L', 'Case à cocher'], ['⌘ ,', 'Réglages (et Raccourcis pour en ajouter)'],
      ] },
    ],
  },
  {
    id: 'resolve', title: 'DaVinci Resolve', color: '#f472b6',
    note: 'Page Montage (Edit). Les raccourcis se modifient dans DaVinci Resolve > Personnalisation du clavier.',
    sections: [
      { title: 'Lecture et pages', items: [
        ['Espace', 'Lecture, pause'], ['J K L', 'Arrière, stop, avant (2× = plus vite)', true],
        ['← →', 'Image précédente, suivante'], ['↑ ↓', 'Coupe précédente, suivante'],
        ['I O', 'Point d’entrée, de sortie', true], ['⇧2 … ⇧8', 'Pages Média, Cut, Montage, Fusion, Étalonnage, Fairlight, Exportation'],
        ['⇧Z', 'Ajuster la timeline à l’écran', true], ['⌘+ ⌘-', 'Zoomer, dézoomer la timeline'],
      ] },
      { title: 'Montage', items: [
        ['A', 'Outil sélection'], ['B', 'Outil lame (couper)', true], ['T', 'Outil trim'],
        ['⌘B', 'Couper à la tête de lecture', true], ['⌫', 'Supprimer en laissant un trou'],
        ['⇧⌫', 'Supprimer et refermer le trou (ripple)', true], ['N', 'Magnétisme on / off'],
        ['M', 'Ajouter un marqueur (rythme de la musique)', true], ['D', 'Activer, désactiver le clip'],
        ['⌘R', 'Contrôles de vitesse (retime)'], ['F9 / F10', 'Insérer / écraser depuis le moniteur source'],
        ['⌘Z / ⌘⇧Z', 'Annuler / rétablir'],
      ] },
    ],
  },
];
