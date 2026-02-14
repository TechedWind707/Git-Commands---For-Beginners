import json
import re
from pathlib import Path


P = Path("src/alias.json")


def fmt_desc(plain: str, example: str, pit1: str, pit2: str, why: str) -> str:
    return (
        f"{plain}\n\n"
        f"**Example:** `{example}`\n\n"
        f"**Pitfalls:**\n"
        f"- {pit1}\n"
        f"- {pit2}\n\n"
        f"**Why?** {why}"
    )


def add_keywords(base: set, extra):
    for k in extra:
        if k:
            base.add(k)


def kw_clean(items):
    out = []
    seen = set()
    for k in items:
        if not k:
            continue
        k = k.strip().lower()
        if not k or k in seen:
            continue
        seen.add(k)
        out.append(k)
    return out


def example_for(cmd: str, name: str) -> str:
    c = cmd.lower()
    if name == "gwip":
        return "git add -A && git commit -m \"--wip-- [skip ci]\""
    if name == "gpoat":
        return "git push origin --all && git push origin --tags"
    if name == "gpristine":
        return "git reset --hard && git clean -dffx"
    if name == "groh":
        return "git reset --hard origin/main"
    if name == "gwipe":
        return "git reset --hard && git clean -df"
    if name == "ggpnp":
        return "git pull origin feature/login && git push origin feature/login"
    if name == "git-svn-dcommit-push":
        return "git svn dcommit && git push github main:svntrunk"
    if name == "gccd":
        return "git clone https://github.com/org/repo.git && cd repo"
    if name == "gtl":
        return "git tag --sort=-v:refname -n --list \"v1.*\""
    if name in {"gk", "gke"}:
        return "gitk --all --branches"
    if name == "grep":
        return "grep --color=auto -R \"TODO\" src"
    if name == "grt":
        return "cd \"$(git rev-parse --show-toplevel)\""
    if c.startswith("git clone"):
        if "--recurse-submodules" in c:
            return "git clone --recurse-submodules https://github.com/org/repo.git"
        return "git clone https://github.com/org/repo.git"

    if c.startswith("git commit"):
        if "--amend" in c and "--no-edit" in c:
            return "git commit --amend --no-edit"
        if "--amend" in c:
            return "git commit --amend -m \"Fix bug\""
        if " -a " in f" {c} " and " -m" in c:
            return "git commit -a -m \"Fix bug\""
        if " -m" in c:
            return "git commit -m \"Fix bug\""
        if " -s" in c and " -m" in c:
            return "git commit -s -m \"Fix bug\""
        if " -S" in cmd:
            return "git commit -S -m \"Fix bug\""
        return "git commit"

    if c.startswith("git add"):
        if "--patch" in c:
            return "git add --patch src/app.ts"
        if "--all" in c or " -a" in f" {c} ":
            return "git add --all"
        if "--update" in c:
            return "git add --update"
        if "--verbose" in c:
            return "git add --verbose src/app.ts"
        return "git add src/app.ts"

    if c.startswith("git push"):
        if "--dry-run" in c:
            return "git push --dry-run origin main"
        if "--delete" in c:
            return "git push origin --delete feature/old-branch"
        if "--set-upstream" in c or " -u " in f" {c} ":
            return "git push -u origin feature/login"
        if "--force-with-lease" in c:
            return "git push --force-with-lease origin feature/login"
        if "--force" in c:
            return "git push --force origin feature/login"
        return "git push origin feature/login"

    if c.startswith("git pull"):
        if "--rebase=interactive" in c:
            return "git pull --rebase=interactive origin main"
        if "--rebase" in c:
            return "git pull --rebase"
        return "git pull origin main"

    if c.startswith("git status"):
        if " -sb" in f" {c} ":
            return "git status -sb"
        if " -s" in f" {c} ":
            return "git status -s"
        return "git status"

    if c.startswith("git diff"):
        if "--cached" in c or "--staged" in c:
            return "git diff --staged"
        if "--word-diff" in c:
            return "git diff --word-diff"
        return "git diff"

    if c.startswith("git log"):
        return "git log --oneline --decorate --graph"

    if c.startswith("git branch"):
        if " --remote" in c:
            return "git branch --remote"
        if " --no-merged" in c:
            return "git branch --no-merged"
        if "--set-upstream-to" in c:
            return "git branch --set-upstream-to=origin/feature/login"
        if " -d" in f" {cmd} ":
            return "git branch -d feature/old"
        if " -D" in f" {cmd} ":
            return "git branch -D feature/old"
        if " --move" in c:
            return "git branch --move old-name new-name"
        return "git branch -a"

    if c.startswith("git checkout"):
        if " -b" in f" {cmd} ":
            return "git checkout -b feature/login"
        if " -B" in f" {cmd} ":
            return "git checkout -B feature/login main"
        return "git checkout main"

    if c.startswith("git switch"):
        if " -c" in f" {cmd} ":
            return "git switch -c feature/login"
        return "git switch main"

    if c.startswith("git mergetool"):
        return "git mergetool --no-prompt"
    if c == "git merge" or c.startswith("git merge "):
        if "--squash" in c:
            return "git merge --squash feature/login"
        return "git merge feature/login"

    if c.startswith("git rebase"):
        if " -i" in f" {cmd} ":
            return "git rebase -i HEAD~3"
        if "--onto" in c:
            return "git rebase --onto main old-base feature/login"
        return "git rebase main"

    if c.startswith("git reset"):
        if "--hard" in c:
            return "git reset --hard HEAD~1"
        if "--soft" in c:
            return "git reset --soft HEAD~1"
        if "--keep" in c:
            return "git reset --keep HEAD~1"
        if c.strip() == "git reset --":
            return "git reset -- src/app.ts"
        return "git reset --mixed HEAD~1"

    if c.startswith("git restore"):
        if "--staged" in c:
            return "git restore --staged src/app.ts"
        if "--source" in c:
            return "git restore --source=HEAD~1 src/app.ts"
        return "git restore src/app.ts"

    if c.startswith("git revert"):
        return "git revert a1b2c3d"

    if c.startswith("git rm"):
        if "--cached" in c:
            return "git rm --cached .env"
        return "git rm src/old-file.ts"

    if c.startswith("git clean"):
        return "git clean -id"

    if c.startswith("git stash"):
        if " apply" in f" {c} ":
            return "git stash apply stash@{0}"
        if " pop" in f" {c} ":
            return "git stash pop"
        if " list" in f" {c} ":
            return "git stash list"
        if " drop" in f" {c} ":
            return "git stash drop stash@{0}"
        if " clear" in f" {c} ":
            return "git stash clear"
        if "--all" in c:
            return "git stash --all"
        if "--include-untracked" in c:
            return "git stash --include-untracked"
        if " push" in f" {c} ":
            return "git stash push -m \"WIP\""
        return "git stash"

    if c.startswith("git fetch"):
        if " --all" in c:
            return "git fetch --all --prune"
        return "git fetch origin"

    if c.startswith("git remote"):
        if " -v" in f" {c} ":
            return "git remote -v"
        if " add" in f" {c} ":
            return "git remote add upstream https://github.com/org/repo.git"
        if " remove" in f" {c} ":
            return "git remote remove upstream"
        if " rename" in f" {c} ":
            return "git remote rename origin old-origin"
        if " set-url" in f" {c} ":
            return "git remote set-url origin git@github.com:me/repo.git"
        if " update" in f" {c} ":
            return "git remote update"
        return "git remote -v"

    if c.startswith("git tag"):
        if " -s" in f" {c} ":
            return "git tag -s v1.2.0 -m \"Release 1.2.0\""
        if "--annotate" in c:
            return "git tag -a v1.2.0 -m \"Release 1.2.0\""
        if "sort -v" in c:
            return "git tag | sort -V"
        return "git tag v1.2.0"

    if c.startswith("git submodule"):
        return "git submodule update --init --recursive"

    if c.startswith("git svn"):
        if " dcommit" in c:
            return "git svn dcommit"
        return "git svn rebase"

    if c.startswith("git worktree"):
        if " add" in f" {c} ":
            return "git worktree add ../repo-hotfix hotfix/login"
        if " list" in f" {c} ":
            return "git worktree list"
        if " move" in f" {c} ":
            return "git worktree move ../old-path ../new-path"
        if " remove" in f" {c} ":
            return "git worktree remove ../repo-hotfix"
        return "git worktree list"

    if c.startswith("git am"):
        return "git am 0001-fix-login.patch"

    if c.startswith("git apply"):
        if "--3way" in c:
            return "git apply --3way fix.patch"
        return "git apply fix.patch"

    if c.startswith("git bisect"):
        return "git bisect start"

    if c.startswith("git blame"):
        return "git blame src/app.ts"

    if c.startswith("git cherry-pick"):
        return "git cherry-pick a1b2c3d"

    if c.startswith("git help"):
        return "git help commit"

    if c.startswith("git show"):
        return "git show HEAD"

    if c.startswith("git describe"):
        return "git describe --tags"

    if c.startswith("git reflog"):
        return "git reflog"

    if c.startswith("git whatchanged"):
        return "git whatchanged -p"

    if c.startswith("git gui"):
        return "git gui citool"

    if c.startswith("gitk") or c.startswith("\\gitk"):
        return "gitk --all --branches"

    if c.startswith("git"):
        return cmd

    return cmd

def desc_for(entry: dict) -> str:
    cmd = entry["command"]
    c = cmd.lower()
    name = entry["name"]

    # Composite / special aliases first.
    if name == "gwip":
        return fmt_desc(
            "Creates a quick WIP commit from all current changes.",
            example_for(cmd, name),
            "This can include unwanted files; check `git status` first.",
            "WIP commits can be pushed by mistake; avoid pushing them to shared branches.",
            "capture progress before context switching",
        )
    if name in {"gpristine", "gwipe"}:
        return fmt_desc(
            "Wipes local changes and untracked files to a clean state.",
            example_for(cmd, name),
            "This permanently deletes uncommitted work; stash or commit first.",
            "Running on the wrong repo can be disastrous; confirm repo root.",
            "recover from a broken or messy working tree",
        )
    if name == "gpoat":
        return fmt_desc(
            "Pushes all branches and tags to the remote.",
            example_for(cmd, name),
            "You might push tags you did not intend; review tags first.",
            "Pushing all branches can leak local work; push specific branches instead.",
            "bulk publish when you intentionally want everything pushed",
        )
    if name == "ggpnp":
        return fmt_desc(
            "Pulls remote changes, then pushes your branch.",
            example_for(cmd, name),
            "Pull may stop on conflicts; resolve and commit before pushing.",
            "Push can be rejected if upstream moved; pull again after resolving.",
            "keep your branch in sync with minimal typing",
        )
    if name == "git-svn-dcommit-push":
        return fmt_desc(
            "Sends commits to SVN, then mirrors to GitHub.",
            example_for(cmd, name),
            "Wrong branch mapping can publish bad history; verify branch names.",
            "SVN replays can rewrite commits; keep branch linear.",
            "bridge Git work into SVN workflows",
        )
    if name == "gccd":
        return fmt_desc(
            "Clones a repo and changes into the new folder.",
            example_for(cmd, name),
            "Repo folder name may differ; check directory name after clone.",
            "Auth failures stop the clone; use the correct HTTPS/SSH URL.",
            "start working in a repo immediately after cloning",
        )
    if name == "gtl":
        return fmt_desc(
            "Lists tags by version, filtered by a prefix.",
            example_for(cmd, name),
            "Broad prefixes can dump too many tags; narrow the prefix.",
            "If tags are missing, run `git fetch --tags` first.",
            "quickly find the latest release tag",
        )
    if name == "gk" or name == "gke":
        return fmt_desc(
            "Opens GitK, a graphical history viewer.",
            example_for(cmd, name),
            "GitK may not be installed; use `git log --graph` instead.",
            "Large repos can make GitK slow; limit history if needed.",
            "visualize branches and merges easily",
        )
    if name == "grep":
        return fmt_desc(
            "Searches for text in files while skipping common VCS/build folders.",
            example_for(cmd, name),
            "Broad searches can be noisy; limit to a folder like `src/`.",
            "Pattern quoting differs by shell; wrap patterns in quotes.",
            "find TODOs or errors quickly",
        )
    if name == "grt":
        return fmt_desc(
            "Jumps your shell to the Git repository root.",
            example_for(cmd, name),
            "Outside a repo this will fail; confirm you are in a repo.",
            "If it returns '.', you are already at the repo root.",
            "avoid long relative paths in deep folders",
        )
    if name == "gunwip":
        return fmt_desc(
            "Removes the most recent WIP commit if it is labeled --wip--.",
            "git log -n 1 | grep -q -c \"--wip--\" && git reset HEAD~1",
            "If the last commit is not WIP, nothing happens; verify with `git log`.",
            "Undoing a pushed WIP rewrites history; avoid on shared branches.",
            "clean up temporary commits safely",
        )
    if name == "gignored":
        return fmt_desc(
            "Lists tracked files marked as assume-unchanged.",
            "git ls-files -v | grep \"^[[:lower:]]\"",
            "These flags are local only; teammates will still see changes.",
            "Clear with `git update-index --no-assume-unchanged <file>` when done.",
            "find files you hid from local status",
        )
    if name == "gfg":
        return fmt_desc(
            "Finds tracked files whose paths match a pattern.",
            "git ls-files | grep \"\\.test\\.\"",
            "Search is case-sensitive; add `-i` if needed.",
            "Untracked files will not appear; add them or search with `rg`.",
            "quickly locate files by name",
        )
    if name == "glp":
        return fmt_desc(
            "Shows git log using a helper's pretty format.",
            "glp",
            "The helper may not exist outside your shell setup; use `git log` then.",
            "Custom formats can hide details; switch to `git log -p` when debugging.",
            "read history in a cleaner format",
        )
    if name == "gbda":
        return fmt_desc(
            "Deletes merged local branches (excluding main/develop).",
            "git branch --merged | grep -v \"main\" | xargs git branch -d",
            "If your main/develop names differ, review the branch list first.",
            "Only merged branches are removed; unmerged work remains.",
            "bulk cleanup after merging feature branches",
        )
    if name == "gbg":
        return fmt_desc(
            "Lists local branches whose upstream is gone on the remote.",
            "git branch -vv | grep \": gone]\"",
            "This only lists branches; it does not delete anything.",
            "Upstream may be gone due to a rename; verify before cleanup.",
            "find branches that can be cleaned up",
        )
    if name == "gbgd":
        return fmt_desc(
            "Deletes local branches whose upstream is gone (safe delete).",
            "git branch -vv | grep \": gone]\" | awk '{print $1}' | xargs git branch -d",
            "If a branch has unmerged commits, `-d` will refuse; inspect first.",
            "Upstream might be renamed; confirm the correct replacement branch.",
            "clean up stale branches safely",
        )
    if name == "gbgD":
        return fmt_desc(
            "Force-deletes local branches whose upstream is gone.",
            "git branch -vv | grep \": gone]\" | awk '{print $1}' | xargs git branch -D",
            "Force delete can lose unmerged commits; verify with `git log`.",
            "If upstream was renamed, you may delete the wrong branch; double-check.",
            "remove stale branches quickly",
        )
    if name == "gcd":
        return fmt_desc(
            "Switches to the Git Flow develop branch from your config.",
            "git checkout develop",
            "If Git Flow is not configured, this will fail; run `git flow init`.",
            "The develop branch may not exist locally; run `git branch -a`.",
            "jump to your integration branch quickly",
        )
    if name == "gch":
        return fmt_desc(
            "Switches to a Git Flow hotfix branch name from your config.",
            "git checkout hotfix/1.2.1",
            "If the branch does not exist, create it with `git checkout -b`.",
            "Git Flow config must be set; run `git flow init` if needed.",
            "move to hotfix work quickly",
        )
    if name == "gcr":
        return fmt_desc(
            "Switches to a Git Flow release branch name from your config.",
            "git checkout release/1.2.0",
            "If the branch does not exist, create it with `git checkout -b`.",
            "Git Flow config must be set; run `git flow init` if needed.",
            "jump to release work quickly",
        )

    # Git command families.
    if c == "git":
        return fmt_desc(
            "Runs Git so you can execute repository commands.",
            "git status",
            "Running outside a repo fails; cd into a repo first.",
            "Typos in subcommands are common; use `git help` when unsure.",
            "entry point for all version control work",
        )

    if c.startswith("git add"):
        if "--patch" in c:
            return fmt_desc(
                "Stages only selected chunks of changes interactively.",
                example_for(cmd, name),
                "Picking wrong hunks mixes unrelated changes; review with `git diff --cached`.",
                "Skipping needed hunks can break builds; ensure all required changes are staged.",
                "create small, reviewable commits",
            )
        if "--all" in c or " -a" in f" {c} ":
            return fmt_desc(
                "Stages all changes, including deletions and new files.",
                example_for(cmd, name),
                "You may stage generated or binary files; check `git status` first.",
                "It will stage deletions you may not want; unstage with `git restore --staged <file>`.",
                "fast when you want everything in one commit",
            )
        if "--update" in c:
            return fmt_desc(
                "Stages only changes to already tracked files.",
                example_for(cmd, name),
                "New files remain unstaged; add them explicitly.",
                "Deleted tracked files are staged too; confirm before commit.",
                "update tracked files without grabbing new ones",
            )
        if "--verbose" in c:
            return fmt_desc(
                "Stages files and prints what Git is adding.",
                example_for(cmd, name),
                "Verbose output can hide mistakes; still review with `git status`.",
                "Staging the wrong file is easy; double-check paths.",
                "extra visibility while staging",
            )
        return fmt_desc(
            "Stages selected files so they are included in the next commit.",
            example_for(cmd, name),
            "Using `git add .` can stage unwanted files; review `git status`.",
            "Large binaries should not be staged; add to `.gitignore` if needed.",
            "build clean, intentional commits",
        )

    if c.startswith("git commit"):
        if "--amend" in c:
            return fmt_desc(
                "Rewrites the most recent commit with new staged changes.",
                example_for(cmd, name),
                "Amending a pushed commit rewrites history; avoid on shared branches.",
                "If nothing is staged, amend changes only the message; stage files first.",
                "fix the last commit before sharing",
            )
        return fmt_desc(
            "Creates a commit from staged changes.",
            example_for(cmd, name),
            "Apostrophes can break the message; use `\\'` or open the editor instead.",
            "Forgot `git add`? You will create an empty commit or omit files.",
            "save progress with a clear message",
        )

    if c.startswith("git push"):
        if "--dry-run" in c:
            return fmt_desc(
                "Shows what would be pushed without changing the remote.",
                example_for(cmd, name),
                "Dry-run can go stale quickly if the remote changes; push soon after.",
                "Dry-run does not test permissions fully; real push can still fail.",
                "safe preview before an important push",
            )
        if "--delete" in c:
            return fmt_desc(
                "Deletes a branch on the remote.",
                example_for(cmd, name),
                "Deleting the wrong branch affects teammates; verify branch name.",
                "You may lose unmerged work if the branch is not backed up.",
                "clean up remote branches after merges",
            )
        if "--force" in c:
            return fmt_desc(
                "Force-pushes local history to the remote branch.",
                example_for(cmd, name),
                "This can overwrite others' work; prefer `--force-with-lease`.",
                "Force pushes on shared branches can break CI and reviews.",
                "update remote after rewriting history",
            )
        if "--set-upstream" in c or " -u " in f" {c} ":
            return fmt_desc(
                "Pushes a branch and sets its upstream tracking branch.",
                example_for(cmd, name),
                "Wrong upstream links future pulls to the wrong branch; verify names.",
                "If the remote branch already exists, this may not set tracking as expected.",
                "one-time setup for simpler future pushes",
            )
        return fmt_desc(
            "Uploads your local commits to the remote branch.",
            example_for(cmd, name),
            "Pushing from the wrong branch is common; check `git status` first.",
            "First push may require `-u` to set upstream tracking.",
            "share work with teammates and CI",
        )

    if c.startswith("git pull"):
        if "--rebase" in c:
            return fmt_desc(
                "Fetches and rebases your local commits on top of remote changes.",
                example_for(cmd, name),
                "Conflicts are common; resolve, `git add`, then `git rebase --continue`.",
                "Rebasing shared commits rewrites history; avoid on public branches.",
                "keep history linear while syncing",
            )
        return fmt_desc(
            "Fetches and merges remote changes into your current branch.",
            example_for(cmd, name),
            "Pulling on the wrong branch causes messy merges; check branch first.",
            "If you have local changes, pull may fail; stash or commit first.",
            "quickly sync with teammates",
        )

    if c.startswith("git status"):
        return fmt_desc(
            "Shows what is staged, unstaged, and untracked.",
            example_for(cmd, name),
            "Skipping status leads to wrong commits; run it often.",
            "Short format can be cryptic; use full `git status` when unsure.",
            "best daily safety check",
        )

    if c.startswith("git diff"):
        return fmt_desc(
            "Shows changes between files, staged data, and commits.",
            example_for(cmd, name),
            "Empty output may mean changes are staged; try `git diff --staged`.",
            "Large diffs can hide issues; limit to specific files when reviewing.",
            "review changes before committing",
        )

    if c.startswith("git log"):
        return fmt_desc(
            "Shows commit history and branch graph.",
            example_for(cmd, name),
            "Large output can be noisy; limit with `--max-count`.",
            "You may miss other branches; add `--all` if needed.",
            "understand history quickly",
        )

    if c.startswith("git branch"):
        if "--set-upstream-to" in c:
            return fmt_desc(
                "Sets the upstream tracking branch for your current branch.",
                example_for(cmd, name),
                "Setting the wrong upstream breaks pull/push defaults; verify names.",
                "The remote branch must exist; run `git fetch` first.",
                "enable simple `git pull` and `git push`",
            )
        if " -d" in f" {cmd} ":
            return fmt_desc(
                "Deletes a local branch if it is fully merged.",
                example_for(cmd, name),
                "If not merged, Git will refuse; use `-D` only after checking.",
                "Deleting the wrong branch can lose work; verify the name.",
                "clean up local branches after merging",
            )
        if " -D" in f" {cmd} ":
            return fmt_desc(
                "Force-deletes a local branch even if unmerged.",
                example_for(cmd, name),
                "You can lose unmerged commits; back them up first.",
                "Double-check the branch name to avoid deleting the wrong one.",
                "remove abandoned branches quickly",
            )
        if " --move" in c:
            return fmt_desc(
                "Renames a local branch.",
                example_for(cmd, name),
                "If the branch was pushed, update the remote name and upstream.",
                "Teammates will still have the old name until they prune.",
                "fix branch naming mistakes cleanly",
            )
        if " --no-merged" in c:
            return fmt_desc(
                "Lists branches not yet merged into the current branch.",
                example_for(cmd, name),
                "Results depend on your current branch; check out the right base first.",
                "Remote branch info can be stale; run `git fetch --prune`.",
                "spot branches that still need merging",
            )
        if " --remote" in c:
            return fmt_desc(
                "Lists remote-tracking branches only.",
                example_for(cmd, name),
                "You cannot commit to these directly; create a local branch first.",
                "Run `git fetch` to update the list of remote branches.",
                "see what exists on the server",
            )
        if " -a" in f" {cmd} " or " --all" in c:
            return fmt_desc(
                "Lists local and remote-tracking branches.",
                example_for(cmd, name),
                "Remote names are pointers; they are not local branches.",
                "Stale remotes remain until `git fetch --prune`.",
                "find branches on the server without switching",
            )
        return fmt_desc(
            "Lists local branches and shows the current branch.",
            "git branch",
            "It does not show remote branches; use `git branch -a`.",
            "If the list looks stale, run `git fetch --prune`.",
            "see your branch landscape at a glance",
        )

    if c.startswith("git checkout"):
        if "--recurse-submodules" in c:
            return fmt_desc(
                "Switches branches and updates submodules to match.",
                "git checkout --recurse-submodules main",
                "Uncommitted changes can block switching; stash or commit first.",
                "Submodule updates can be slow; ensure you have access.",
                "keep submodules aligned when switching branches",
            )
        if " -B" in f" {cmd} ":
            return fmt_desc(
                "Creates or resets a branch to a start point, then switches to it.",
                example_for(cmd, name),
                "This can move an existing branch and drop commits; verify first.",
                "Use `-b` if you do not want to overwrite an existing branch.",
                "recreate a branch from a clean base",
            )
        if " -b" in f" {cmd} ":
            return fmt_desc(
                "Creates a new branch and switches to it.",
                example_for(cmd, name),
                "Uncommitted changes can block switching; stash or commit first.",
                "Branch names should be descriptive; avoid spaces.",
                "start new work without affecting main",
            )
        return fmt_desc(
            "Switches to another branch.",
            example_for(cmd, name),
            "Uncommitted changes can block switching; stash or commit first.",
            "Switching to the wrong branch can misplace work; verify the name.",
            "move between tasks safely",
        )

    if c.startswith("git switch"):
        if " -c" in f" {cmd} ":
            return fmt_desc(
                "Creates a new branch and switches to it.",
                example_for(cmd, name),
                "Uncommitted changes can block switching; stash or commit first.",
                "Branch names should be descriptive; avoid spaces.",
                "start new work without affecting main",
            )
        return fmt_desc(
            "Switches to another branch.",
            example_for(cmd, name),
            "Uncommitted changes can block switching; stash or commit first.",
            "Switching to the wrong branch can misplace work; verify the name.",
            "move between tasks safely",
        )

    if c == "git merge" or c.startswith("git merge "):
        if "--abort" in c:
            return fmt_desc(
                "Aborts a merge and returns to the pre-merge state.",
                "git merge --abort",
                "Any manual conflict edits are discarded; save changes elsewhere first.",
                "If you are not in a merge, this will fail; check `git status`.",
                "safely exit a bad merge",
            )
        if "--continue" in c:
            return fmt_desc(
                "Continues a merge after resolving conflicts.",
                "git merge --continue",
                "You must stage resolved files before continuing.",
                "Unresolved conflicts will block the merge; resolve all files first.",
                "finish the merge cleanly",
            )
        if "--squash" in c:
            return fmt_desc(
                "Brings changes from another branch without creating a merge commit.",
                "git merge --squash feature/login",
                "Squash merges lose individual commit history; keep original branch if needed.",
                "You must commit after squashing; it does not auto-commit.",
                "keep history simpler for small features",
            )
        return fmt_desc(
            "Combines another branch into your current branch.",
            example_for(cmd, name),
            "Merging the wrong branch causes confusion; verify branch names.",
            "Conflicts need careful resolution; use a mergetool if available.",
            "integrate completed work",
        )

    if c.startswith("git mergetool"):
        return fmt_desc(
            "Opens your merge tool to resolve conflicts.",
            example_for(cmd, name),
            "Mergetool must be configured; set `git config merge.tool <tool>`.",
            "Incorrect conflict resolution can break builds; run tests after.",
            "resolve conflicts with fewer mistakes",
        )

    if c.startswith("git rebase"):
        if "--abort" in c:
            return fmt_desc(
                "Aborts a rebase and returns to the pre-rebase state.",
                "git rebase --abort",
                "Any manual conflict edits are discarded; save changes elsewhere first.",
                "If no rebase is in progress, this will fail; check `git status`.",
                "safely exit a bad rebase",
            )
        if "--continue" in c:
            return fmt_desc(
                "Continues a rebase after resolving conflicts.",
                "git rebase --continue",
                "You must stage resolved files before continuing.",
                "Unresolved conflicts will block the rebase; resolve all files first.",
                "complete the rebase cleanly",
            )
        if "--skip" in c:
            return fmt_desc(
                "Skips the current patch during a rebase.",
                "git rebase --skip",
                "Skipping can drop important changes; review skipped commits later.",
                "Repeated skips may hide deeper conflicts; consider resolving instead.",
                "move past a broken commit during rebase",
            )
        if " -i" in f" {c} ":
            return fmt_desc(
                "Starts an interactive rebase to edit, reorder, or squash commits.",
                "git rebase -i HEAD~3",
                "Editing pushed commits rewrites history; avoid on shared branches.",
                "Mistakes in the rebase todo can drop commits; read the instructions carefully.",
                "polish history before sharing",
            )
        if "--onto" in c:
            return fmt_desc(
                "Moves a commit range onto a new base commit.",
                "git rebase --onto main old-base feature/login",
                "Picking the wrong range can lose work; verify commit list first.",
                "Advanced command; consider standard rebase if unsure.",
                "surgically move commits to a new base",
            )
        return fmt_desc(
            "Reapplies your commits on top of another base commit.",
            example_for(cmd, name),
            "Rebasing shared commits rewrites history; avoid on public branches.",
            "Conflicts must be resolved and staged before continuing.",
            "keep history clean and linear",
        )

    if c.startswith("git reset"):
        if "--hard" in c:
            return fmt_desc(
                "Resets and discards local changes to match a commit.",
                example_for(cmd, name),
                "This permanently deletes uncommitted work; stash first.",
                "Running in the wrong repo can destroy work; confirm root.",
                "recover from a broken working tree",
            )
        return fmt_desc(
            "Moves HEAD and/or the index without deleting working files.",
            example_for(cmd, name),
            "Using `--hard` by mistake is destructive; double-check flags.",
            "Resetting can unstage work; verify with `git status` afterward.",
            "fix staging or recent commit mistakes",
        )

    if c.startswith("git restore"):
        return fmt_desc(
            "Restores files from a commit or unstages them.",
            example_for(cmd, name),
            "Restoring discards local edits; check `git diff` first.",
            "Using `--staged` only unstages; it does not change file content.",
            "undo safely with modern commands",
        )

    if c.startswith("git revert"):
        if "--abort" in c:
            return fmt_desc(
                "Aborts an in-progress revert and restores the previous state.",
                "git revert --abort",
                "Manual conflict edits will be discarded; save changes if needed.",
                "If no revert is in progress, this will fail.",
                "safely exit a bad revert",
            )
        if "--continue" in c:
            return fmt_desc(
                "Continues a revert after resolving conflicts.",
                "git revert --continue",
                "You must stage resolved files before continuing.",
                "Unresolved conflicts will block progress; resolve all files first.",
                "finish the revert cleanly",
            )
        return fmt_desc(
            "Creates a new commit that undoes a previous commit.",
            example_for(cmd, name),
            "Reverting merge commits requires extra flags; read `git help revert`.",
            "Revert conflicts must be resolved and staged before continuing.",
            "undo safely without rewriting history",
        )

    if c.startswith("git rm"):
        return fmt_desc(
            "Removes files from Git tracking (and optionally disk).",
            example_for(cmd, name),
            "Use `--cached` if you want to keep the file locally.",
            "Remove secrets and add to `.gitignore` to prevent re-adding.",
            "keep repo clean and secure",
        )

    if c.startswith("git clean"):
        return fmt_desc(
            "Deletes untracked files and folders.",
            example_for(cmd, name),
            "This can remove important local files; preview with `git clean -nd`.",
            "It does not remove tracked files; use `git reset` for those.",
            "reset cluttered working directories",
        )

    if c.startswith("git clone"):
        if "--recurse-submodules" in c:
            return fmt_desc(
                "Clones a repo and initializes its submodules.",
                example_for(cmd, name),
                "Submodules can still be outdated; run `git submodule update --init --recursive` if needed.",
                "Auth failures stop the clone; use the correct HTTPS/SSH URL.",
                "get all nested dependencies in one step",
            )
        return fmt_desc(
            "Creates a local copy of a remote repository.",
            example_for(cmd, name),
            "Auth failures stop the clone; use the correct HTTPS/SSH URL.",
            "Large repos can take time; be patient or use a shallow clone.",
            "get a repo locally so you can work on it",
        )

    if c.startswith("git stash"):
        if " apply" in f" {c} ":
            return fmt_desc(
                "Applies a stash without removing it from the stash list.",
                "git stash apply stash@{0}",
                "Applying can cause conflicts; resolve and commit afterward.",
                "You might apply the wrong stash; check `git stash list` first.",
                "reuse a stash safely",
            )
        if " pop" in f" {c} ":
            return fmt_desc(
                "Applies the latest stash and removes it from the list.",
                "git stash pop",
                "Conflicts can occur; resolve them and commit.",
                "If conflicts happen, the stash may still be dropped; use `apply` for safety.",
                "quickly resume stashed work",
            )
        if " list" in f" {c} ":
            return fmt_desc(
                "Lists all stash entries.",
                "git stash list",
                "Stash indexes change when dropping entries; copy the exact id.",
                "Long lists get confusing; use meaningful stash messages.",
                "find the right stash to apply",
            )
        if " drop" in f" {c} ":
            return fmt_desc(
                "Deletes a specific stash entry.",
                "git stash drop stash@{0}",
                "Dropping the wrong stash loses work; verify the id first.",
                "Dropped stashes are hard to recover; be careful.",
                "clean up old stashes",
            )
        if " clear" in f" {c} ":
            return fmt_desc(
                "Deletes all stash entries.",
                "git stash clear",
                "This permanently removes all stashes; consider dropping selectively.",
                "Make sure no stash contains needed work.",
                "reset stash list when it is no longer needed",
            )
        if " show" in f" {c} ":
            return fmt_desc(
                "Shows the changes stored in a stash.",
                "git stash show --text stash@{0}",
                "Output can be brief; add `-p` or `--text` for full patch.",
                "Review before applying to avoid surprises.",
                "inspect stashed changes safely",
            )
        if "--all" in c:
            return fmt_desc(
                "Stashes tracked, untracked, and ignored files.",
                example_for(cmd, name),
                "Ignored files will be stashed too; be careful with large build output.",
                "Restoring can bring back lots of files; apply selectively if needed.",
                "pause all local work before switching tasks",
            )
        if "--include-untracked" in c or " -u" in f" {c} ":
            return fmt_desc(
                "Stashes tracked and untracked files (not ignored).",
                example_for(cmd, name),
                "Ignored files are not saved; use `--all` if you need them.",
                "Restoring can cause conflicts; resolve and commit afterward.",
                "save new files without committing",
            )
        return fmt_desc(
            "Temporarily saves local work without committing.",
            example_for(cmd, name),
            "Untracked files are skipped unless you use `-u`.",
            "Stashes are easy to forget; name them and list regularly.",
            "switch tasks without messy WIP commits",
        )

    if c.startswith("git fetch"):
        return fmt_desc(
            "Downloads updates from remotes without merging.",
            example_for(cmd, name),
            "Fetch does not update your working branch; merge or rebase after.",
            "Stale remote branches can mislead; use `--prune` if needed.",
            "inspect remote changes safely",
        )

    if c.startswith("git remote"):
        return fmt_desc(
            "Shows or edits remote repository connections.",
            example_for(cmd, name),
            "Wrong URLs cause auth errors; verify with `git remote -v`.",
            "Removing the wrong remote breaks workflows; double-check names.",
            "manage origin/upstream cleanly",
        )

    if c.startswith("git tag"):
        return fmt_desc(
            "Creates or lists tags for releases.",
            example_for(cmd, name),
            "Tagging the wrong commit confuses releases; verify with `git show <tag>`.",
            "Signed tags require GPG setup; configure before tagging.",
            "mark release points clearly",
        )

    if c.startswith("git submodule"):
        return fmt_desc(
            "Initializes or updates nested repositories.",
            example_for(cmd, name),
            "Forget `--recursive` and nested submodules stay empty.",
            "Submodules require separate commits; remember to update the parent pointer.",
            "keep dependency repos aligned",
        )

    if c.startswith("git svn"):
        return fmt_desc(
            "Bridges Git work with an SVN repository.",
            example_for(cmd, name),
            "SVN replays can rewrite commits; keep branch linear.",
            "Wrong SVN mappings can publish bad history; verify config.",
            "support legacy SVN workflows",
        )

    if c.startswith("git worktree"):
        return fmt_desc(
            "Manages multiple working directories for one repo.",
            example_for(cmd, name),
            "You cannot check out the same branch in two worktrees.",
            "Remove worktrees only after saving work; uncommitted changes can be lost.",
            "work on multiple branches in parallel",
        )

    if c.startswith("git am"):
        if "--abort" in c:
            return fmt_desc(
                "Aborts an in-progress patch apply and restores the previous state.",
                "git am --abort",
                "Manual conflict edits will be discarded; save changes if needed.",
                "If no `git am` is in progress, this will fail.",
                "safely exit a broken patch apply",
            )
        if "--continue" in c:
            return fmt_desc(
                "Continues applying patches after resolving conflicts.",
                "git am --continue",
                "You must stage resolved files before continuing.",
                "Unresolved conflicts will block progress; resolve all files first.",
                "finish applying a patch series",
            )
        if "--skip" in c:
            return fmt_desc(
                "Skips the current patch and continues with the rest.",
                "git am --skip",
                "Skipping can drop important changes; review skipped patches later.",
                "Skipping too much can leave the series incomplete.",
                "move past a failing patch quickly",
            )
        if "--show-current-patch" in c:
            return fmt_desc(
                "Shows the patch currently being applied.",
                "git am --show-current-patch",
                "Large patches can be noisy; pipe to a pager if needed.",
                "If no patch is active, output may be empty.",
                "inspect the failing patch quickly",
            )
        return fmt_desc(
            "Applies email-style patch files as commits.",
            example_for(cmd, name),
            "Patch context can fail; update your branch or resolve conflicts.",
            "Skipping patches can drop changes; review skipped commits later.",
            "apply patch series cleanly",
        )

    if c.startswith("git apply"):
        if "--3way" in c:
            return fmt_desc(
                "Applies a patch and tries a three-way merge if needed.",
                example_for(cmd, name),
                "It can still conflict; resolve, stage, and commit afterward.",
                "Three-way merge needs base info; some patches won't support it.",
                "apply patches more safely when files changed",
            )
        return fmt_desc(
            "Applies a patch without creating a commit.",
            example_for(cmd, name),
            "Patch may fail if files changed; try `--3way`.",
            "Applied changes are not committed; remember to commit later.",
            "test patch changes before committing",
        )

    if c.startswith("git bisect"):
        if " reset" in f" {c} ":
            return fmt_desc(
                "Ends the bisect session and returns to your original branch.",
                "git bisect reset",
                "Save or stash any edits made during bisect before resetting.",
                "If you skip reset, you stay in detached HEAD mode.",
                "exit bisect cleanly",
            )
        if " start" in f" {c} ":
            return fmt_desc(
                "Starts a new bisect session.",
                "git bisect start",
                "You must mark at least one good and one bad commit to proceed.",
                "Remember to run `git bisect reset` when finished.",
                "begin finding the first bad commit",
            )
        if " good" in f" {c} ":
            return fmt_desc(
                "Marks the current commit as good during bisect.",
                "git bisect good",
                "Make sure you tested this commit; wrong marks give wrong results.",
                "You must be on the commit you tested; do not mark from another branch.",
                "drive the bisect search correctly",
            )
        if " bad" in f" {c} ":
            return fmt_desc(
                "Marks the current commit as bad during bisect.",
                "git bisect bad",
                "Make sure you tested this commit; wrong marks give wrong results.",
                "You must be on the commit you tested; do not mark from another branch.",
                "drive the bisect search correctly",
            )
        if " new" in f" {c} ":
            return fmt_desc(
                "Marks the current commit as new (bad) during bisect.",
                "git bisect new",
                "Make sure you tested this commit; wrong marks give wrong results.",
                "Use `old` for the known-good commit.",
                "label tested commits consistently",
            )
        if " old" in f" {c} ":
            return fmt_desc(
                "Marks the current commit as old (good) during bisect.",
                "git bisect old",
                "Make sure you tested this commit; wrong marks give wrong results.",
                "Use `new` for the known-bad commit.",
                "label tested commits consistently",
            )
        return fmt_desc(
            "Starts and manages a bisect session to find a bad commit.",
            example_for(cmd, name),
            "You must mark one good and one bad commit to proceed.",
            "Stop bisect with `git bisect reset` to return to normal.",
            "pinpoint regressions quickly",
        )

    if c.startswith("git blame"):
        return fmt_desc(
            "Shows who last changed each line in a file.",
            example_for(cmd, name),
            "Blame lacks context; review related commits before deciding.",
            "Large files can be slow; limit to specific files.",
            "trace code history per line",
        )

    if c.startswith("git cherry-pick"):
        if "--abort" in c:
            return fmt_desc(
                "Aborts an in-progress cherry-pick and restores the previous state.",
                "git cherry-pick --abort",
                "Manual conflict edits will be discarded; save changes if needed.",
                "If no cherry-pick is in progress, this will fail.",
                "safely exit a bad cherry-pick",
            )
        if "--continue" in c:
            return fmt_desc(
                "Continues a cherry-pick after resolving conflicts.",
                "git cherry-pick --continue",
                "You must stage resolved files before continuing.",
                "Unresolved conflicts will block progress; resolve all files first.",
                "complete the cherry-pick cleanly",
            )
        return fmt_desc(
            "Copies a specific commit onto your current branch.",
            example_for(cmd, name),
            "Picking commits out of order can break builds; include dependencies.",
            "Conflicts need resolution and staging before continue.",
            "move targeted fixes without merging branches",
        )

    if c.startswith("git help"):
        return fmt_desc(
            "Opens Git documentation for commands and options.",
            example_for(cmd, name),
            "Man pages are long; use search to find flags.",
            "Different Git versions vary slightly; check your local docs.",
            "most reliable source of Git behavior",
        )

    if c.startswith("git show"):
        return fmt_desc(
            "Displays details for a commit, tag, or object.",
            example_for(cmd, name),
            "Output can be large; limit to a file path when needed.",
            "Binary diffs can be noisy; use `--stat` to summarize.",
            "inspect exact changes quickly",
        )

    if c.startswith("git describe"):
        return fmt_desc(
            "Finds the nearest tag name for a commit.",
            example_for(cmd, name),
            "Missing tags give poor results; run `git fetch --tags`.",
            "Describe output can be confusing on shallow clones.",
            "useful for build/version strings",
        )

    if c.startswith("git reflog"):
        return fmt_desc(
            "Shows local history of where HEAD and branches pointed.",
            example_for(cmd, name),
            "Reflog is local only; it will not show on other machines.",
            "Reflog expires; recover lost commits sooner rather than later.",
            "recover from bad resets or rebases",
        )

    if c.startswith("git whatchanged"):
        return fmt_desc(
            "Shows commit history with patch details.",
            example_for(cmd, name),
            "Output gets very long; limit by path or range.",
            "Older command style; `git log -p` is similar.",
            "deep debugging of history changes",
        )

    if c.startswith("git gui"):
        return fmt_desc(
            "Opens a graphical commit tool.",
            example_for(cmd, name),
            "GUI tools may not be installed; use CLI instead.",
            "Amending commits in GUI can still rewrite history; be careful.",
            "visual staging for beginners",
        )

    if c.startswith("gitk") or c.startswith("\\gitk"):
        return fmt_desc(
            "Opens GitK to visualize commit history.",
            example_for(cmd, name),
            "GitK may not be installed; use `git log --graph`.",
            "Large histories can be slow; limit view if needed.",
            "see branches and merges visually",
        )

    if c.startswith("git ls-files"):
        return fmt_desc(
            "Lists files tracked by Git.",
            example_for(cmd, name),
            "Grep patterns may miss case variations; use `-i` if needed.",
            "It only lists tracked files; untracked files are not shown.",
            "quickly locate tracked files",
        )

    if c.startswith("git flow"):
        return fmt_desc(
            "Runs Git Flow helpers for feature/release/hotfix branches.",
            example_for(cmd, name),
            "Git Flow may not match your team workflow; confirm first.",
            "Missing config can break flow commands; run `git flow init`.",
            "structured branching for release-driven teams",
        )

    if c.startswith("git shortlog"):
        return fmt_desc(
            "Shows commit counts grouped by author.",
            example_for(cmd, name),
            "Different emails can split one author; use `.mailmap` to fix.",
            "Counts may be misleading in rebased histories.",
            "quick contributor summary",
        )

    if c.startswith("git config"):
        return fmt_desc(
            "Shows Git configuration values and their sources.",
            example_for(cmd, name),
            "Local and global configs can conflict; check `--show-origin`.",
            "Typos in config keys silently do nothing; verify spelling.",
            "debug identity, editor, and signing issues",
        )

    if c.startswith("git update-index"):
        return fmt_desc(
            "Adjusts low-level tracking for already tracked files.",
            example_for(cmd, name),
            "Easy to forget hidden changes; undo with `--no-assume-unchanged`.",
            "Only affects local repo; teammates still track changes normally.",
            "reduce noise from machine-specific files",
        )

    # Default fallback
    return fmt_desc(
        "Runs a Git command shortcut.",
        example_for(cmd, name),
        "Aliases can hide details; check the full command when unsure.",
        "Running on the wrong branch can cause mistakes; check `git status`.",
        "speed up common Git workflows",
    )

def keywords_for(entry: dict) -> list:
    cmd = entry["command"]
    name = entry["name"]
    c = cmd.lower()
    tokens = re.split(r"\s+", c)
    sub = tokens[1] if len(tokens) > 1 else ""

    kw = set()
    add_keywords(kw, [name])

    # Special aliases
    if name == "gwip":
        add_keywords(kw, ["wip", "commit", "snapshot", "quick", "save", "add", "all"])
        return kw_clean(sorted(kw))
    if name in {"gpristine", "gwipe"}:
        add_keywords(kw, ["reset", "clean", "wipe", "discard", "hard", "untracked"])
        return kw_clean(sorted(kw))
    if name == "gpoat":
        add_keywords(kw, ["push", "all", "tags", "publish", "remote"])
        return kw_clean(sorted(kw))
    if name == "ggpnp":
        add_keywords(kw, ["pull", "push", "sync", "update", "publish"])
        return kw_clean(sorted(kw))
    if name == "git-svn-dcommit-push":
        add_keywords(kw, ["svn", "dcommit", "push", "mirror"])
        return kw_clean(sorted(kw))
    if name == "gccd":
        add_keywords(kw, ["clone", "cd", "repo", "repository", "download"])
        return kw_clean(sorted(kw))
    if name == "gtl":
        add_keywords(kw, ["tag", "tags", "version", "release", "list"])
        return kw_clean(sorted(kw))
    if name in {"gk", "gke"}:
        add_keywords(kw, ["gitk", "gui", "graph", "history", "visual"])
        return kw_clean(sorted(kw))
    if name == "gunwip":
        add_keywords(kw, ["wip", "unwip", "undo", "reset", "commit", "remove"])
        return kw_clean(sorted(kw))
    if name == "gignored":
        add_keywords(kw, ["assume-unchanged", "ignored", "hidden", "ls-files", "tracked"])
        return kw_clean(sorted(kw))
    if name == "gfg":
        add_keywords(kw, ["find", "files", "filter", "grep", "search"])
        return kw_clean(sorted(kw))
    if name == "glp":
        add_keywords(kw, ["log", "pretty", "history", "format"])
        return kw_clean(sorted(kw))
    if name in {"gbda", "gbg", "gbgd", "gbgD"}:
        add_keywords(kw, ["branch", "branches", "cleanup", "delete", "gone", "upstream"])
        return kw_clean(sorted(kw))
    if name == "grep":
        add_keywords(kw, ["grep", "search", "find", "pattern", "text"])
        return kw_clean(sorted(kw))
    if name == "grt":
        add_keywords(kw, ["root", "cd", "repo", "toplevel"])
        return kw_clean(sorted(kw))

    if c == "git":
        add_keywords(kw, ["git", "commands", "help"])
        return kw_clean(sorted(kw))

    if not c.startswith("git "):
        add_keywords(kw, ["alias", "command"])
        return kw_clean(sorted(kw))

    if sub:
        add_keywords(kw, [sub])

    # Subcommand keyword expansions
    if "add" in tokens:
        add_keywords(kw, ["stage", "staging", "index", "files"])
        if "--all" in tokens or "-a" in tokens:
            add_keywords(kw, ["all", "everything"])
        if "--patch" in tokens:
            add_keywords(kw, ["patch", "interactive", "hunks"])
        if "--update" in tokens:
            add_keywords(kw, ["update", "tracked"])
    if "commit" in tokens:
        add_keywords(kw, ["commit", "commits", "save", "snapshot"])
        if "-m" in tokens:
            add_keywords(kw, ["message", "msg", "cmsg"])
        if "-a" in tokens:
            add_keywords(kw, ["all", "tracked"])
        if "-s" in tokens:
            add_keywords(kw, ["signoff", "dco"])
        if "-S" in cmd:
            add_keywords(kw, ["sign", "gpg", "signed"])
        if "--amend" in tokens:
            add_keywords(kw, ["amend", "edit", "rewrite"])
    if "push" in tokens:
        add_keywords(kw, ["push", "upload", "publish", "remote"])
        if "--force" in tokens:
            add_keywords(kw, ["force", "rewrite"])
        if "--force-with-lease" in tokens:
            add_keywords(kw, ["force-with-lease", "lease", "rewrite"])
        if "--dry-run" in tokens:
            add_keywords(kw, ["dry-run", "preview"])
        if "--delete" in tokens:
            add_keywords(kw, ["delete", "remove"])
        if "--set-upstream" in tokens or "-u" in tokens:
            add_keywords(kw, ["upstream", "track", "set-upstream"])
    if "pull" in tokens:
        add_keywords(kw, ["pull", "fetch", "update", "sync"])
        if "--rebase" in tokens or "--rebase=interactive" in tokens:
            add_keywords(kw, ["rebase", "linear"])
    if "status" in tokens:
        add_keywords(kw, ["status", "state", "changes"])
    if "diff" in tokens or "diff-tree" in tokens:
        add_keywords(kw, ["diff", "compare", "changes", "patch"])
        if "--cached" in tokens or "--staged" in tokens:
            add_keywords(kw, ["staged", "cached"])
        if "--word-diff" in tokens:
            add_keywords(kw, ["word", "text"])
    if "log" in tokens:
        add_keywords(kw, ["log", "history", "commits", "graph"])
    if "branch" in tokens:
        add_keywords(kw, ["branch", "branches", "list", "create", "delete"])
        if "--remote" in tokens:
            add_keywords(kw, ["remote"])
        if "--no-merged" in tokens:
            add_keywords(kw, ["unmerged"])
        if "--move" in tokens:
            add_keywords(kw, ["rename", "move"])
        if any(t.startswith("--set-upstream-to") for t in tokens):
            add_keywords(kw, ["upstream", "track", "set-upstream"])
    if "checkout" in tokens or "switch" in tokens:
        add_keywords(kw, ["checkout", "switch", "branch"])
        if "-b" in tokens or "-c" in tokens or "-B" in tokens:
            add_keywords(kw, ["new", "create"])
    if "merge" in tokens:
        add_keywords(kw, ["merge", "combine", "integrate"])
        if "--squash" in tokens:
            add_keywords(kw, ["squash"])
    if "rebase" in tokens:
        add_keywords(kw, ["rebase", "rewrite", "history"])
        if "-i" in tokens:
            add_keywords(kw, ["interactive", "squash", "edit"])
    if sub == "reset":
        add_keywords(kw, ["reset", "undo", "unstage", "rollback"])
        if "--hard" in tokens:
            add_keywords(kw, ["hard", "discard"])
        if "--soft" in tokens:
            add_keywords(kw, ["soft"])
        if "--keep" in tokens:
            add_keywords(kw, ["keep"])
    if "restore" in tokens:
        add_keywords(kw, ["restore", "undo", "unstage", "discard"])
        if "--staged" in tokens:
            add_keywords(kw, ["unstage"])
    if "revert" in tokens:
        add_keywords(kw, ["revert", "undo", "commit", "reverse"])
    if "rm" in tokens:
        add_keywords(kw, ["remove", "delete", "untrack", "rm"])
    if "clean" in tokens:
        add_keywords(kw, ["clean", "untracked", "remove", "wipe"])
    if "clone" in tokens:
        add_keywords(kw, ["clone", "repo", "repository", "download"])
        if "--recurse-submodules" in tokens:
            add_keywords(kw, ["submodule", "submodules", "recursive"])
    if "stash" in tokens:
        add_keywords(kw, ["stash", "save", "shelve", "wip", "temporary"])
        if "apply" in tokens:
            add_keywords(kw, ["apply"])
        if "pop" in tokens:
            add_keywords(kw, ["pop"])
        if "list" in tokens:
            add_keywords(kw, ["list"])
        if "drop" in tokens:
            add_keywords(kw, ["drop"])
        if "clear" in tokens:
            add_keywords(kw, ["clear"])
    if "fetch" in tokens:
        add_keywords(kw, ["fetch", "download", "update"])
    if "remote" in tokens:
        add_keywords(kw, ["remote", "origin", "upstream", "url"])
        if "add" in tokens:
            add_keywords(kw, ["add"])
        if "remove" in tokens:
            add_keywords(kw, ["remove", "delete"])
        if "rename" in tokens:
            add_keywords(kw, ["rename"])
        if "set-url" in tokens:
            add_keywords(kw, ["set-url", "url"])
        if "update" in tokens:
            add_keywords(kw, ["update"])
    if "tag" in tokens:
        add_keywords(kw, ["tag", "tags", "release", "version"])
        if "-s" in tokens or "-S" in tokens:
            add_keywords(kw, ["signed", "sign", "gpg"])
        if "--annotate" in tokens:
            add_keywords(kw, ["annotate"])
    if "submodule" in tokens:
        add_keywords(kw, ["submodule", "submodules", "dependencies"])
    if "svn" in tokens:
        add_keywords(kw, ["svn", "subversion", "legacy"])
    if "worktree" in tokens:
        add_keywords(kw, ["worktree", "worktrees", "multiple"])
        if "add" in tokens:
            add_keywords(kw, ["add", "create"])
        if "list" in tokens:
            add_keywords(kw, ["list"])
        if "move" in tokens:
            add_keywords(kw, ["move"])
        if "remove" in tokens:
            add_keywords(kw, ["remove", "delete"])
    if "describe" in tokens:
        add_keywords(kw, ["describe", "tags", "version"])
    if "reflog" in tokens:
        add_keywords(kw, ["reflog", "recover", "history"])
    if "whatchanged" in tokens:
        add_keywords(kw, ["whatchanged", "history", "patch"])
    if "help" in tokens:
        add_keywords(kw, ["help", "docs", "manual"])
    if "show" in tokens:
        add_keywords(kw, ["show", "inspect", "details"])
    if "blame" in tokens:
        add_keywords(kw, ["blame", "annotate", "author", "line"])
    if "bisect" in tokens:
        add_keywords(kw, ["bisect", "bug", "regression", "search"])
        if "good" in tokens:
            add_keywords(kw, ["good"])
        if "bad" in tokens:
            add_keywords(kw, ["bad"])
        if "start" in tokens:
            add_keywords(kw, ["start"])
        if "reset" in tokens:
            add_keywords(kw, ["reset", "stop", "end"])
        if "new" in tokens:
            add_keywords(kw, ["new"])
        if "old" in tokens:
            add_keywords(kw, ["old"])
    if "am" in tokens:
        add_keywords(kw, ["am", "patch", "email"])
    if "apply" in tokens:
        add_keywords(kw, ["apply", "patch"])
        if "--3way" in tokens:
            add_keywords(kw, ["3way", "three-way", "merge"])
    if "cherry-pick" in tokens:
        add_keywords(kw, ["cherry-pick", "pick", "commit"])
    if "flow" in tokens:
        add_keywords(kw, ["flow", "gitflow", "feature", "release", "hotfix"])
    if "gui" in tokens:
        add_keywords(kw, ["gui", "visual"])
    if "config" in tokens:
        add_keywords(kw, ["config", "settings", "configure"])
    if "update-index" in tokens:
        add_keywords(kw, ["update-index", "assume-unchanged", "ignore"])
    if "ls-files" in tokens:
        add_keywords(kw, ["list", "files", "tracked"])
    if "shortlog" in tokens:
        add_keywords(kw, ["shortlog", "authors", "contributors", "stats"])

    return kw_clean(sorted(kw))


def main():
    data = json.loads(P.read_text(encoding="utf-8"))
    for entry in data:
        entry["description"] = desc_for(entry)
        entry["keywords"] = keywords_for(entry)
    P.write_text(json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
