Bika's Git Workflow
===================

    dev			                                                  master
    |                                                                 |
    | $ git checkout dev                                              |
    | $ git pull origin dev                                           |
    |                                                                 |
    | $ git checkout -b branchA                                       |
    |------------------------> branchA                                |
    |                            |                                    |
    |                            |                                    |
    |                            | $ git commit -a                    |
    |                            |     ·                              |
    |                            |     ·                              |
    |                            | $ git commit -a                    |
    |                            |                                    |
    |                            |                                    |
    |                            |                                    |
    |                            |<-------------------------------+   |
    |                            · $ git pull origin branchA      |   |
    |                            · $ git checkout dev             |   |
    |                            · $ git remote update            |   |
    |                            · $ git pull origin dev          |   |
    |                            · $ git checkout branchA         |   |
    #-------------------------->>* $ git merge dev                |   |
    |                              $ git push origin branchA      |   |
    |<···························+ Pull request [on github]       |   |
    · REJECTED                   ·                                |   |
    |                            · $ git reset --hard ORIG_HEAD --+   |
    |                            |                                    |
    |                            | $ git commit -a                    |
    |                            |     ·                              |
    |                            |     ·                              |
    |                            | $ git commit -a                    |
    |                            |                                    |
    |                            |                                    |
    |                            · $ git pull origin branchA          |
    |                            · $ git checkout dev                 |
    |                            · $ git remote update                |
    |                            · $ git pull origin dev              |
    |                            · $ git checkout branchA             |
    #-------------------------->>* $ git merge dev                    |
    |                              $ git push origin branchA          |
    |<···························+ Pull request [on github]           |
    · ACCEPTED                  /                                     |
    *<<------------------------# merge A to dev [by maintainer]       |
    |                              $ git push origin :branchA         |
    |                                                                 |
    ·                                                                 |
    · Functional testing                                              |
    ·                                            merge dev to master  |
    ·                                            [by maintainer]      |
    #--------------------------------------------------------------->>*
    |                                                                 |
    |                                                                 |
    |                                                       rev.flag--@
    |                                                                 |

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
