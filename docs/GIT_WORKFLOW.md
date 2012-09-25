Bika's Git Workflow
===================

When making inconsequential changes, or adding very small features, it's
acceptable to commit directly on the dev branch. If a feature or issue
rquires review, then it's better to create a new branch. There are many ways
of accomplishing the same tasks, some combination of the ideas and commands
below will work for you.

#### Creating and working on a new branch

    $ git remote update
    $ git checkout dev
    $ git pull origin dev
    $ git checkout -b feature_branch
      <modify files>
    $ git commit -a
    $ git push origin feature_branch

#### Testing someone else's feature branch

    $ git remote update
    $ git checkout dev
    $ git pull origin dev
    $ git pull origin feature_branch
    $ git checkout feature_branch

#### Updating a feature branch if code in dev branch has changed

    $ git remote update
    $ git checkout dev
    $ git pull origin dev
    $ git checkout feature_branch
    $ git merge dev

#### Merging a complete and tested feature branch back into dev

    $ git remote update
    $ git checkout feature_branch
    $ git pull origin feature_branch
    $ git checkout dev
    $ git pull origin dev
    $ git merge feature_branch
    $ git branch -d feature_branch

Other useful git commands
=========================

Current status

    $ git status

List current info about branches, local and remote repos

    $ git branch -va

For saving the local code state before changing branch without losing
data (save option) and for reloading them after branch change (pop)

    $ git stash save
    $ git stash pop

For undoing the most recent commit on the current branch

    $ git reset HEAD~1

Timeline with the last commits

    $ git log --pretty=format:"%h %s" --graph

Use kdiff3 for resolving merge conflicts

    $ git mergetool -t kdiff3

Use rebase to tidy up a series of commits before pushing.

    $ git remote update
    $ git checkout feature_branch
    $ git pull origin feature_branch
    $ git rebase -i origin/feature_branch

