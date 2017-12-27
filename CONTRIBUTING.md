# Contributing to senaite.core

Third-party contributions are essential for keeping senaite.core
continuously improving. We simply cannot access the huge number of
platforms and myriad configurations for running senaite.lims. We want to
keep it as easy as possible to contribute changes that get things
working in your environment. There are a few guidelines that we need
contributors to follow so that we can have a chance of keeping on top of
things.

The following is a set of guidelines for contributing to senaite.core, which
is hosted in the [SENAITE Organization](https://github.com/senaite) on
GitHub. These are just guidelines, not rules. Use your best judgment,
and feel free to propose changes to this document in a [pull
request](#how-to-submit-a-pull-request).

## Code of Conduct

This project adheres to the Contributor Covenant [code of
conduct](CODE_OF_CONDUCT.md). By participating, you are expected to
uphold this code. Please report unacceptable behavior.

## Reporting an issue

Have you found a bug in the code which is not in the [list of known
bugs](https://github.com/senaite/senaite.core/issues)? Do you have a
suggestion for improvement? Then by all means please [submit a new
issue](https://github.com/senait/senaite.core/issues/new), and do not
hesitate to comment on existing [open
issues](https://github.com/senaite/senaite.core/issues).

When filling a new issue, please remember to:

 * **Use a clear and descriptive title** for the issue to identify the
problem.

 * **Describe the exact steps which reproduce the problem** in as many
details as possible. For example, start by describing your computing
platform (Operating System and version, how did you installed senaite.lims
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

   1. If you still have not done so, [create your personal account on
GitHub](https://github.com/join).

   2. [Fork senaite.core from
GitHub](https://github.com/senaite/senaite.core/fork). This will copy the
whole senaite.core repository to your personal account.

   3. Then, go to your favourite working folder in your computer and
clone your forked repository by typing (replacing ```YOUR_USERNAME``` by
the actual username of your GitHub account):

          $ git clone https://github.com/YOUR_USERNAME/senaite.core

   4. Your forked repository https://github.com/YOUR_USERNAME/senaite.core
will receive the default name of `origin`. You can also add the original
senaite.lims repository, which is usually called `upstream`:

          $ cd senaite.core
          $ git remote add upstream https://github.com/senaite/senaite.core.git

To verify the new upstream repository you have specified for your fork,
type `git remote -v`. You should see the URL for your fork as `origin`,
and the URL for the original repository as `upstream`:

```
$ git remote -v
origin    https://github.com/YOUR_USERNAME/senaite.core.git (fetch)
origin    https://github.com/YOUR_USERNAME/senaite.core.git (push)
upstream  https://github.com/senaite/senaite.core.git (fetch)
upstream  https://github.com/senaite/senaite.core.git (push)
```

### Master and develop branches

The `master` branch will always have the most stable version, and only
bugfixes must be done against this branch. New features, non-trivial
improvements, and refactoring must be done against the `develop` branch.


### Start working on your contribution

Checkout the `develop` branch (or `master` branch if you plan to start
working on a fix for a bug found in the latest stable release) of the
git repository in order to get synchronized with the latest code:

```
$ git checkout develop
$ git pull upstream develop
```

When start working in a new improvement, please **always** branch off
from `develop`. Only branch off from `master` if you are working on a
bugfix. Open a new branch and start working on it:

```
$ git checkout -b my_feature
```

Now you can do changes, add files, do commits (please take a look at
[how to write good commit
messages](https://chris.beams.io/posts/git-commit/)!) and push them to
your repository:

```
$ git push origin my_feature
```

If there have been new pushes to the `develop` branch of the `upstream`
repository since the last time you pulled from it, you might want to put
your commits on top of them (this is mandatory for pull requests):

```
$ git pull --rebase upstream develop
```

### How to submit a pull request

When the contribution is ready, you can [submit a pull
request](https://github.com/senaite/senaite.core/compare/). Head to your
GitHub repository, switch to your `my_feature` branch, and click the
_**Pull Request**_ button, which will do all the work for you. If your
contribution is a fix for a bug encountered in latest stable version,
thus you forked from `master`, comparison must be to `master` branch.
Otherwise, code comparison must be always to `develop` branch.

Once a pull request is sent, the Developer Team can review the set of
changes, discuss potential modifications, and even push follow-up
commits if necessary.

Some things that will increase the chance that your pull request is
accepted:

 * Write tests.
 * Follow [Plone's Python styleguide](https://docs.plone.org/develop/styleguide/python.html).
 * Write a descriptive and detailed summary. Please consider that
reviewing pull requests is hard, so include as much information as
possible to make your pull request's intent clear.
  * Do not address multiple bugfixes or features in the same Pull Request.
  * Include whitespace and formatting changes in discrete commits.
  * Add a changelog entry in [CHANGES.rst](https://github.com/senaite/senaite.core/CHANGES.rst)


For more details about Git usage, please check out Chapters 1 and 2 from
[Pro Git book](https://git-scm.com/book/en/v2).
