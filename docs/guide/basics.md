# Basic tsrc usage



## Cloning a set of repositories

`tsrc` is driven by a manifest file that contains the names and paths of repositories to clone.

It uses the YAML syntax and looks like:

```yaml
repos:
  - src: foo
    url: git@gitlab.local:acme/foo

  - src: bar
    url: git@gitlab.local:acme/bar
```

!!! note
    The full manifest file format is described in the [reference](../ref/formats.md).

The manifest must be put in a git repository too. You can then use the following commands to create a new workspace:

```console
$ mkdir ~/work
$ cd work
$ tsrc init git@gitlab.local:acme/manifest.git
```

In this example:

* A clone of the manifest repository will be created in a hidden `.tsrc/manifest` folder.
* `foo` will be cloned in `<work>/foo` using `git@gitlab.local/acme/foo.git` origin url.
* Similarly, `bar` will be cloned in `<work>/bar` using `git@gitlab.local:acme/bar.git`.

!!! note
    For any command that requires a workspace to exist (`foreach`, `log`, etc.),
    you can run `tsrc` from anywhere in the workspace, not just at the top:
    tsrc will walk up the filesystem looking for a workspace root.

## Making sure all the repositories are up to date

You can update all the repositories by using `tsrc sync`.

* The manifest itself is updated first.
* If a new repository has been added to the manifest, it is cloned.
* If a repository has been cloned in the workspace but *removed* from the manifest, it simply
  gets ignored.
* Lastly, the other repositories are updated.

Note that `tsrc sync` only updates the repositories if the changes are trivial. tsrc will not touch any repository if:

* The repository is dirty
* The local branch has diverged from upstream
* There is no remote tracking branch


