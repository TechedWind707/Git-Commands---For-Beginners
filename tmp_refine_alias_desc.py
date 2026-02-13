# import json
# import re
# from pathlib import Path


# P = Path("src/alias.json")


# def wc(s: str) -> int:
#     return len(re.findall(r"\S+", s))


# def make(does: str, ex: str, pit: str, why: str) -> str:
#     s = f"{does} Example: `{ex}`. Pitfalls: {pit}. Why: {why}."
#     s = re.sub(r"\s+", " ", s).strip()
#     if wc(s) <= 80:
#         return s
#     s = s.replace("Pitfalls:", "Pitfall:")
#     if wc(s) <= 80:
#         return s
#     pit = pit.split(";")[0].strip()
#     s = f"{does} Example: `{ex}`. Pitfall: {pit}. Why: {why}."
#     s = re.sub(r"\s+", " ", s).strip()
#     if wc(s) <= 80:
#         return s
#     why = why.split(" and ")[0].strip()
#     return re.sub(r"\s+", " ", f"{does} Example: `{ex}`. Pitfall: {pit}. Why: {why}.").strip()


# def refine(cmd: str):
#     c = cmd.lower()
#     if c.startswith("git am"):
#         return make(
#             "Applies email-style patch files as commits on your current branch.",
#             "git am 0001-fix-login.patch",
#             "patch context can fail on old code; update base branch or resolve conflicts then continue",
#             "useful when teams share patches by email/export",
#         )
#     if c.startswith("git apply"):
#         return make(
#             "Applies patch changes to files without creating a commit.",
#             "git apply fix.patch",
#             "patch may fail on changed files; try `git apply --3way` or update your branch",
#             "quick way to test external fixes before committing",
#         )
#     if c.startswith("git bisect"):
#         return make(
#             "Helps find the bug-introducing commit with binary search steps.",
#             "git bisect start",
#             "marking commits incorrectly gives wrong results; run a reliable test each step",
#             "find regressions much faster than manual checking",
#         )
#     if c.startswith("git blame"):
#         return make(
#             "Shows who last changed each line in a file and when.",
#             "git blame src/app.ts",
#             "blame lacks full context; open related commits before deciding ownership",
#             "great for tracing code history quickly",
#         )
#     if c.startswith("git cherry-pick"):
#         return make(
#             "Copies a specific commit from another branch onto your current branch.",
#             "git cherry-pick a1b2c3d",
#             "picking commits out of order can break code; include dependency commits too",
#             "move targeted fixes without full branch merges",
#         )
#     if c.startswith("git flow"):
#         return make(
#             "Runs Git Flow helpers for feature, release, and hotfix branches.",
#             "git flow feature start login-form",
#             "Git Flow may not match your team process; confirm workflow before using",
#             "adds structure for release-heavy projects",
#         )
#     if c.startswith("git gui"):
#         return make(
#             "Opens Git GUI tools to stage files and create commits visually.",
#             "git gui citool",
#             "GUI may be unavailable in headless terminals; use CLI commands as fallback",
#             "friendlier for beginners than raw terminal staging",
#         )
#     if c.startswith("git ls-files"):
#         return make(
#             "Lists files tracked by Git, often combined with filters like grep.",
#             "git ls-files | grep config",
#             "grep patterns can miss matches; use `-i` for case-insensitive search",
#             "fast file lookup inside repository index",
#         )
#     if c.startswith("git mergetool"):
#         return make(
#             "Opens your configured merge tool to resolve conflicts file by file.",
#             "git mergetool --no-prompt",
#             "tool must be configured first; set `git config merge.tool <tool>`",
#             "reduces manual conflict mistakes",
#         )
#     if c.startswith("git shortlog"):
#         return make(
#             "Shows commit counts grouped by author names.",
#             "git shortlog -sn",
#             "different emails can split one person into multiple names; use `.mailmap` if needed",
#             "quick contribution summary for a repo",
#         )
#     if c.startswith("git svn"):
#         return make(
#             "Bridges Git work with an SVN upstream repository.",
#             "git svn rebase",
#             "mixed Git/SVN workflows can rewrite unexpectedly; keep branch linear and sync often",
#             "needed for legacy SVN-integrated teams",
#         )
#     if c.startswith("git update-index"):
#         return make(
#             "Toggles low-level tracking behavior for already tracked files.",
#             "git update-index --assume-unchanged .env.local",
#             "easy to forget hidden changes; undo with `--no-assume-unchanged` before sharing work",
#             "useful for local machine-specific file tweaks",
#         )
#     if c.startswith("git describe"):
#         return make(
#             "Finds the nearest tag name for a commit (often latest version label).",
#             "git describe --tags",
#             "fails or looks odd when tags are missing locally; run `git fetch --tags`",
#             "handy for build/version strings",
#         )
#     if c.startswith("git reflog"):
#         return make(
#             "Shows local pointer history for HEAD and branches.",
#             "git reflog",
#             "reflog is local and expires; recover lost commits sooner rather than later",
#             "lifesaver after bad reset/rebase actions",
#         )
#     if c.startswith("git whatchanged"):
#         return make(
#             "Shows commit history with patch details (older style log view).",
#             "git whatchanged -p",
#             "output gets very long; limit by path or commit range",
#             "deep-dive debugging of historical changes",
#         )
#     if c.startswith("\\gitk") or c.startswith("gitk"):
#         return make(
#             "Opens GitK graphical history viewer for branches and commits.",
#             "gitk --all --branches",
#             "GitK may not be installed by default; use `git log --graph` if unavailable",
#             "visual branch graph helps new Git users",
#         )
#     if c.startswith("grep "):
#         return make(
#             "Searches text patterns in files while skipping common VCS/build folders.",
#             "grep --color=auto -R \"TODO\" src",
#             "broad searches can be noisy; limit to specific folders like `src/`",
#             "quickly find strings, errors, or TODOs",
#         )
#     if c.startswith("cd "):
#         return make(
#             "Moves your shell to the repository root directory.",
#             "cd \"$(git rev-parse --show-toplevel)\"",
#             "outside a Git repo this can fail; check current directory first",
#             "saves time when you are deep in subfolders",
#         )
#     if c.startswith("_git_log_prettily"):
#         return make(
#             "Shows log output using a custom pretty format function.",
#             "git log --oneline --decorate --graph",
#             "custom shell helpers may not exist everywhere; fall back to plain `git log`",
#             "cleaner history view for quick reviews",
#         )
#     if c.startswith("gtl(){"):
#         return make(
#             "Lists tags matching a prefix, sorted by newest version first.",
#             "git tag --sort=-v:refname -n --list \"v1.*\"",
#             "broad patterns can flood output; use a tighter prefix",
#             "quick way to find release tags",
#         )
#     return None


# data = json.loads(P.read_text(encoding="utf-8"))
# for e in data:
#     d = e["description"]
#     if d.startswith("Runs this alias command") or d.startswith("Runs multiple Git commands"):
#         new = refine(e["command"])
#         if new:
#             e["description"] = new
#     if wc(e["description"]) > 80:
#         raise SystemExit(f"too long: {e['name']} {wc(e['description'])}")
# P.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
