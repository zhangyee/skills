# Skills

我的个人 Agent Skills，采用 MIT 许可。

## Skills

- [explain](skills/explain/SKILL.md)：用自然中文解释概念、代码职责、执行过程、架构和行为。
- [writing-docs](skills/writing-docs/SKILL.md)：编写和修订技术文档、README、RFC、PR 描述，整理结构并去掉套话。
- [unslop](skills/unslop/SKILL.md)：去掉文字中的 AI 表达痕迹，保留原意和预期语气。

`explain` 和 `writing-docs` 使用 `unslop` 技能，请一并安装。

## 安装

安装前需要 Node.js 22.20 或更高版本。使用 [Vercel Skills CLI](https://github.com/vercel-labs/skills) 安装本仓库的技能：

```bash
npx skills add zhangyee/skills -g --skill explain writing-docs unslop
```

按提示选择要安装到的 agent。`-g` 表示安装到用户目录，供不同项目使用；去掉 `-g` 则安装到当前项目。

只安装 `explain` 或 `writing-docs` 时，也需要同时安装 `unslop`，例如：

```bash
npx skills add zhangyee/skills -g --skill writing-docs unslop
```

可以追加 `-a codex` 等参数指定 agent，也可以先列出仓库中的技能：

```bash
npx skills add zhangyee/skills --list
```

## 本地开发

克隆本仓库后，在仓库根目录运行：

```bash
bash scripts/list-skills.sh
bash scripts/link-skills.sh
```

`list-skills.sh` 列出仓库中的 `SKILL.md`。
`link-skills.sh` 将每个 skill 文件夹链接到 `~/.agents/skills/<name>`。
例如，`~/.agents/skills/explain` 指向本仓库的 `skills/explain/`。
修改源码后无需再次复制；新建 skill 后重新运行链接脚本。在独立 agent 会话中测试实际任务。

链接脚本沿用 Matt Pocock 的开发用实现：已有的同名真实目录会被删除并替换为链接，已有同名链接也会被替换。首次使用前请确认安装目录中的同名内容已经迁移或备份。仓库需要保留在链接指向的位置。

## 比较 skill 版本

平时直接编辑并用 Git 记录。需要验证某次改动时，选择旧提交与当前源码运行相同任务：

```bash
python3 scripts/eval-skills.py compare --skill writing-docs --baseline HEAD --model gpt-6.1-sol
```

这里 `HEAD` 指最近一次提交，默认候选版本为当前 `skills/` 源码，包括尚未提交的修改；也可以把 `--baseline` 换成提交 SHA、tag 或分支。无需在编辑前运行脚本或手动创建快照。

工具会自行取出两组源码及依赖，在独立会话中执行任务并生成 A / B 对照页。任务、版本、输出和评分保存在本次 `.eval-runs/` 运行记录中，默认不提交到 Git。评测使用 Codex CLI 配额，由你显式运行。重复运行、模型评分、人工反馈及失败恢复见 [评测说明](evals/README.md)。

## 添加 skill

在 `skills/<name>/` 下创建 `SKILL.md`，并按需要加入 `scripts/`、`references/` 或 `assets/`。随后运行 `bash scripts/link-skills.sh`。

## 许可与来源

本项目采用 [MIT 许可](LICENSE)。根目录 LICENSE 保留 Yee Zhang 和 Matt Pocock 的版权声明及共同的 MIT 许可正文。

`scripts/link-skills.sh` 和 `scripts/list-skills.sh` 来自 [Matt Pocock 的 skills 仓库](https://github.com/mattpocock/skills/tree/8666e05d641f6922993616e92c0cf54a85080bd7/scripts)。链接脚本调整为只安装到 `~/.agents/skills/`，列举脚本保留上游行为。Matt Pocock 的版权及 MIT 许可保存在根目录 LICENSE。

`explain`、`writing-docs` 和 `unslop` 包含改编自 Lauren Tan（poteto）的 [pstack skills](https://github.com/cursor/plugins/tree/2776ddd2355d6d6c8747d3964600f28daf62f049/pstack) 的内容。具体来源、改编说明及 Lauren Tan 的版权和 MIT 许可分别保存在 [explain 来源声明](skills/explain/NOTICE)、[writing-docs 来源声明](skills/writing-docs/NOTICE)和 [unslop 来源声明](skills/unslop/NOTICE)中，随各 skill 一起分发。
