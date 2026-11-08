# Skills

[中文](README.md) | English

My personal Agent Skills, released under the MIT license.

## Skills

- [explain](skills/explain/SKILL.md): Explain concepts, code responsibilities, execution flows, architecture, and behavior in natural Chinese.
- [writing-docs](skills/writing-docs/SKILL.md): Write and revise technical documentation, READMEs, RFCs, and PR descriptions. Organize the content and remove filler.
- [unslop](skills/unslop/SKILL.md): Remove AI writing patterns while preserving the meaning and intended tone.

`explain` and `writing-docs` use `unslop`. Install them together.

## Install

Requires Node.js 22.20 or later. Install the skills with the [Vercel Skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add zhangyee/skills -g --skill explain writing-docs unslop
```

Follow the prompts to choose the agents to install to. The `-g` flag installs to your user directory for use across projects. Omit `-g` to install to the current project.

If you install only `explain` or `writing-docs`, also install `unslop`. For example:

```bash
npx skills add zhangyee/skills -g --skill writing-docs unslop
```

Add a flag such as `-a codex` to choose an agent. To list the skills in this repository before installing:

```bash
npx skills add zhangyee/skills --list
```

## Local development

Clone this repository, then run these commands from its root:

```bash
bash scripts/list-skills.sh
bash scripts/link-skills.sh
```

`list-skills.sh` lists the `SKILL.md` files in the repository.
`link-skills.sh` links each skill directory to `~/.agents/skills/<name>`.
For example, `~/.agents/skills/explain` points to `skills/explain/` in this repository.
Source changes take effect without copying the files again. Test real tasks in a separate agent session.

To add a skill, create `SKILL.md` under `skills/<name>/`. Add `scripts/`, `references/`, or `assets/` as needed, then rerun the linking script.

The linking script follows Matt Pocock's development implementation: it deletes existing real directories with matching names and replaces them with links. It also replaces existing links with matching names. Before the first run, make sure you have moved or backed up any existing content with those names in the installation directory. Keep this repository at the path the links point to.

## Compare skill versions

Edit the skills and record versions with Git. When you need to evaluate a change, run the same tasks against an earlier commit and your current source:

```bash
python3 scripts/eval-skills.py compare --skill writing-docs --baseline HEAD --model gpt-6.1-sol
```

`HEAD` is the latest commit. By default, the candidate is the current `skills/` source, including uncommitted changes. You can also set `--baseline` to a commit SHA, tag, or branch. You do not need to run a script before editing or create snapshots manually.

The tool retrieves both versions and their dependencies, runs tasks in separate sessions, and generates a page for comparing the two sets of outputs. It saves the tasks, versions, outputs, and grades in the run's `.eval-runs/` directory, which Git ignores by default. Evaluations use your Codex CLI quota and run only when you start them. See the [evaluation guide (Chinese)](evals/README.md) for repeated runs, model grading, human feedback, and recovery after failures.

## License and sources

This project uses the [MIT license](LICENSE). The root LICENSE contains the copyright notices for Yee Zhang and Matt Pocock, followed by the shared MIT license text.

`scripts/link-skills.sh` and `scripts/list-skills.sh` come from [Matt Pocock's skills repository](https://github.com/mattpocock/skills/tree/8666e05d641f6922993616e92c0cf54a85080bd7/scripts). The linking script is adapted to install only to `~/.agents/skills/`. The listing script retains the upstream behavior. Matt Pocock's copyright notice and MIT license are included in the root LICENSE.

`explain`, `writing-docs`, and `unslop` contain material adapted from Lauren Tan's (poteto) [pstack skills](https://github.com/cursor/plugins/tree/2776ddd2355d6d6c8747d3964600f28daf62f049/pstack). The sources, adaptation notes, and Lauren Tan's copyright notice and MIT license are preserved in the [explain notice](skills/explain/NOTICE), [writing-docs notice](skills/writing-docs/NOTICE), and [unslop notice](skills/unslop/NOTICE). Each notice is distributed with its skill.
