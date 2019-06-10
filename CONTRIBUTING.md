# Contributing to senaite.core

Third-party contributions are essential for keeping `senaite.core` continuously
improving. We simply cannot access the huge number of platforms and myriad
configurations for running `senaite.core`. We want to keep it as easy as
possible to contribute changes that get things working in your environment.
There are a few guidelines that we need contributors to follow so that we can
have a chance of keeping on top of things.

The following is a set of guidelines for contributing to senaite.core, which is
hosted in the [SENAITE Organization](https://github.com/senaite) on GitHub.
These are just guidelines, not rules. Use your best judgment, and feel free to
propose changes to this document in a [pull request](#how-to-submit-a-pull-request).

## Code of Conduct

This project adheres to the Contributor Covenant [code of
conduct](CODE_OF_CONDUCT.md). By participating, you are expected to
uphold this code. Please report unacceptable behavior.

## Reporting an issue

Have you found a bug in the code which is not in the [list of known
bugs](https://github.com/senaite/senaite.core/issues)? Do you have a
suggestion for improvement? Then by all means please [submit a new
issue](https://github.com/senaite/senaite.core/issues/new), and do not
hesitate to comment on existing [open
issues](https://github.com/senaite/senaite.core/issues).

When filling a new issue, please remember to:

 * **Use a clear and descriptive title** for the issue to identify the
problem.

 * **Describe the exact steps which reproduce the problem** in as many
details as possible. For example, start by describing your computing
platform (Operating System and version, how did you installed senaite.core
and its dependencies, what file or front-end are you using as a signal
source, etc.). You can also include the configuration file(s) you are
using, or a dump of the terminal output you are getting. The more
information you provide, the more chances to get useful answers.

 * **Please be patient**. This organization is run on a volunteer basis,
so it can take some time to the Developer Team to reach your issue.
They will do their best to fix it as soon as possible.

 * If you opened an issue that is now solved, it is a good practice to
**close it**.

The list of [open issues](https://github.com/senaite/senaite.core/issues)
can be a good starting point and a source of ideas if you are looking to
contribute to the source code.


## Contributing to the source code

### Preliminaries

   1. If you still have not done so, [create your personal account on GitHub](
   https://github.com/join).

   2. [Fork senaite.core from GitHub](
   https://github.com/senaite/senaite.core/fork). This will copy the whole
   `senaite.core` repository to your personal account.

   3. Then, go to your favourite working folder in your computer and clone your
   forked repository by typing (replacing ```YOUR_USERNAME``` by
   the actual username of your GitHub account):

          $ git clone https://github.com/YOUR_USERNAME/senaite.core

   4. Your forked repository https://github.com/YOUR_USERNAME/senaite.core will
   receive the default name of `origin`. You can also add the original
   `senaite.core` repository, which is usually called `upstream`:

          $ cd senaite.core
          $ git remote add upstream https://github.com/senaite/senaite.core.git

To verify the new upstream repository you have specified for your fork, type
`git remote -v`. You should see the URL for your fork as `origin`, and the URL
for the original repository as `upstream`:

```
$ git remote -v
origin    https://github.com/YOUR_USERNAME/senaite.core.git (fetch)
origin    https://github.com/YOUR_USERNAME/senaite.core.git (push)
upstream  https://github.com/senaite/senaite.core.git (fetch)
upstream  https://github.com/senaite/senaite.core.git (push)
```

### Start working on your contribution

Checkout the `master` branch of the git repository in order to get synchronized
with the latest code:

```
$ git checkout master
$ git pull upstream master
```

Now you can do changes, add files, do commits (please take a look at
[how to write good commit messages](https://chris.beams.io/posts/git-commit/)!)
and push them to your repository:

```
$ git push origin my_feature
```

If there have been new pushes to the `master` branch of the `upstream`
repository since the last time you pulled from it, you might want to put your
commits on top of them (this is mandatory for pull requests):

```
$ git remote update
$ git pull --rebase upstream master
```

Alternatively, you can merge `senaite.core`'s `master` into your branch:

```
$ git remote update
$ git merge --no-ff upstream master
```

Although a merge is safer than rebase, the latter eliminates the unnecessary
merge commits required by `git merge` and makes the project history easier to
navigate. We strongly encourage the developer to know in detail the differences,
pros and cons between doing a `gir rebase` or `git merge`. Good documentation on
this regard can be found in the [Atlassian's Merging vs. Rebasing tutorial](
https://www.atlassian.com/git/tutorials/merging-vs-rebasing).

Note this `git rebase` or `git merge` is required for keeping your branch
aligned with the latest code from the repos. The incorporation of your work into
`master` through a Pull Request will always be done using `git merge`.

### How to submit a pull request

When the contribution is ready, you can [submit a pull
request](https://github.com/senaite/senaite.core/compare/). Head to your
GitHub repository, switch to your `my_feature` branch, and click the
_**Pull Request**_ button, which will do all the work for you. Ensure the
comparison is done with the `master` branch unless you forked from another one.

Once a pull request is sent, the Developer Team will review the set of changes,
discuss potential modifications, and even push follow-up commits if necessary.

Some things that will increase the chance that your pull request is accepted:

 * Write tests.
 * Follow [Plone's Python styleguide](https://docs.plone.org/develop/styleguide/python.html).
 * Write a descriptive and detailed summary. Please consider that reviewing pull
   requests is hard, so include as much information as possible to make your
   pull request's intent clear.
 * Do not address multiple bugfixes or features in the same Pull Request.
 * Include whitespace and formatting changes in discrete commits.
 * Add a changelog entry in [CHANGES.rst](https://github.com/senaite/senaite.core/CHANGES.rst)

For more details about Git usage, please check out Chapters 1 and 2 from
[Pro Git book](https://git-scm.com/book/en/v2).


## Contributing with new ideas

All suggestions and proposals are welcome. We strongly believe that the
feedback of the community is an important asset to make a better project. With
the aim to get the most of these contributions, but without interfering with
the undergoing work regarding to issues and Pull Requests, we've created a
[Community discussion board](
https://community.senaite.org). This is the right place if
you are willing to discuss about new ideas, further steps or improvements.

If you want to keep in touch with the community members and up-to-date
with the latest discussions, please join to the [Gitter community channel](
https://gitter.im/senaite/Lobby).

If you want to stay informed about senaite at easy pace, don't forget
to subscribe to our [users list](https://sourceforge.net/projects/senaite/lists/senaite-users)
