# 比较 skill 版本

这里保存固定任务和检查标准。`scripts/eval-skills.py` 冻结版本、运行任务、评分并生成对照页。运行器使用 Python 3.9+ 标准库、Git 和已登录的 Codex CLI，无需单独安装 Python 包。

## 平时编辑，需要时比较

平时直接编辑 `skills/`，用 Git 提交记录值得保留的版本。需要验证改动时，在仓库根目录运行：

```bash
python3 scripts/eval-skills.py compare \
  --skill writing-docs --baseline HEAD \
  --model gpt-6.1-sol --case release-notes-preserve-evidence
```

这会比较最近一次提交中的版本与当前源码。`--baseline` 必须指定，可以是提交 SHA、tag 或分支；`--candidate` 默认是 `working-tree`，表示当前 `skills/` 的实际内容，包括未提交和未跟踪的文件。Git 暂存区不会被单独当作一个版本。

不必在修改前运行命令。旧提交始终可从 Git 读取；如果当前修改已经提交，可以直接比较两个提交：

```bash
python3 scripts/eval-skills.py compare \
  --skill writing-docs --baseline HEAD~1 --candidate HEAD \
  --model gpt-6.1-sol
```

历史基线必须已经存在。仓库没有任何提交时，先用正常 Git 流程记录初版，再编辑和比较；工具不会替你创建提交。也可将 `--baseline` 设为 `none`，与不安装被测 skill 的输出比较。

运行器直接读取指定提交中的整个 `skills/`，不切换当前分支，也不改动源码。执行前将两组源码及依赖保存到本次运行的 `versions/`，记录来源、提交 SHA 和文件校验值，随后冻结任务和附件。后续源码变化不会改变本次输入，恢复运行时也不重新读取当前分支。运行记录不再依赖分支名是否移动。

没有手动 `snapshot` 命令，也不需要单独的 `.eval-snapshots/` 目录。取出的版本副本随运行记录保存，供核对和重跑；Git 仍是开发版本的记录来源。

`--model` 必须显式提供，使用你有权访问的模型名称。示例模型可替换。运行器默认使用 `medium` 推理强度；两组使用相同设置，可通过 `--effort low|medium|high` 指定。

每组任务启动一个新的 `codex exec`，使用单独的工作目录。执行前安装该版本的被测 skill 及 Markdown 相对链接所指向的同仓库依赖。执行者只获得任务、输入文件和相应 skill，不获得评分断言。

当前执行器面向文本生成、文档改写和只读代码分析：使用只读 sandbox，最终答复作为 `response.md` 保存。它不是需要写文件、构建项目或操作外部服务的通用评测器，也不测试自然触发率。

## 重复比较并增加模型评分

```bash
python3 scripts/eval-skills.py compare \
  --skill writing-docs --baseline HEAD \
  --model gpt-6.1-sol --repeat 3 \
  --judge-model gpt-6.1-sol
```

不加 `--case` 会运行该 skill 的全部任务。每个任务的两组执行顺序按固定 seed 打乱，`--seed` 可指定顺序。`--repeat` 默认是 1，范围是 1–20；重复后才能观察波动。一次成功不证明长期可靠。

执行前会显示调用数量。例如，7 个任务、两个版本、重复 3 次，会执行 42 次；开启评分后还会增加最多 42 次独立评分调用。先用单个任务验证流程，再按需要扩大。

评分模型在新会话中得到同一任务、冻结的输入文件、断言及待评输出，不得到版本标签或 skill 内容。每条断言必须返回判断和证据，程序检查索引完整性并自行计算分数。评分不是事实裁判；需要人工核对证据和文风。

模型可分别指定，保持同一比较内各组的执行模型、推理强度、评分模型一致。模型名称是请求名称；Codex 的 JSONL 不一定提供服务端实际模型版本。

## 看结果并记录人工判断

命令结束时输出本次运行目录和 `report.html` 路径。打开对照页：

1. 查看原始任务和同一检查标准。
2. 在隐藏版本标签和模型分数时比较 A / B，记录偏好和原因。
3. 需要时勾选“显示版本与模型评分”，检查具体证据及原始输出。
4. 点击“导出人工评审 JSON”，然后导入下载的文件：

```bash
python3 scripts/eval-skills.py import-review /path/to/run /path/to/feedback.json
```

网页会尝试在本机浏览器中保存未导出的选择。正式运行记录以导入后的 `feedback.json` 为准。对照页只是隐藏标签，不是防止主动查看源代码的保密机制。两个输出都执行完成后才可以记录 A / B 偏好；失败记录应先排查或重跑。

`summary.json` 和 `summary.md` 同时保留执行失败、待执行、已评分数量、断言平均通过率、重复评分的标准差、成功运行的平均耗时及 token。没有数据的指标为 null，不把未评分或执行失败当成通过。人工偏好单独统计，不和模型断言分数混成一个“质量总分”。

## 失败后继续

```bash
# 只重跑失败或尚未完成的执行；已完成的输出保留
python3 scripts/eval-skills.py resume /path/to/run

# 给尚未评分或评分失败的输出评分
python3 scripts/eval-skills.py grade /path/to/run --model gpt-6.1-sol

# 不调用模型，重新生成对照页和统计
python3 scripts/eval-skills.py report /path/to/run
```

`--timeout` 控制单次调用超时，默认 180 秒。每次尝试保存在不同目录；即使进程在写入结果前退出，也保留旧目录并使用新尝试序号。并发启动同一运行会被锁阻止。恢复时复核运行记录中已保存的任务和版本哈希；执行器 CLI 版本发生变化时，应创建新的比较。

先查看失败目录中的 `stderr.txt`、`trace.jsonl`。登录失败时使用正常的 `codex login` 修复登录，再恢复。运行器沿用 CLI 的认证机制，不复制或输出凭据，也不修改实际 HOME、CODEX_HOME 或已安装的 skills。

## 保存什么，提交什么

```text
evals/<skill>/cases.json           # 提交：固定任务和判断标准
evals/<skill>/fixtures/            # 提交：任务需要的原始文件
.eval-runs/<skill>/<comparison>/   # 本机运行记录，默认不提交
  comparison.json                 # Git 来源、版本、依赖、模型参数、顺序和任务集哈希
  cases/                          # 本次冻结的任务与输入文件
  versions/                       # 自动取出的两组完整 skills 源码及校验清单
  jobs/<case>--<repeat>--<variant>/
    result.json                   # 当前尝试状态、耗时、token、评分与证据
    attempt-1/                    # 工作目录、输出、JSONL、错误日志和实际提示词
    grade-1/                      # 独立评分的提示词、输出和轨迹
  report.html                     # 可直接打开的人工对照页
  summary.json
  summary.md
  feedback.json                   # 导入人工反馈后生成
```

需要共享结果时，可以归档整个运行目录；里面包含实际版本和输入。运行结果不能替代 Git 提交。若使用无 skill 基线且当前源码尚无提交，当前版本的来源 commit 为 null，内容仍由文件哈希记录。

## 添加任务

文件结构沿用本仓库已有的 `skill`、`cases`、`id`、`prompt`、`assertions`。可选 `files` 指向相对于用例文件目录的输入文件：

```json
{
  "skill": "explain",
  "cases": [{
    "id": "retry-boundary",
    "prompt": "解释 fixtures/retry.py 的调用次数和失败行为。",
    "files": ["fixtures/retry.py"],
    "assertions": ["区分总调用次数和重试次数。"]
  }]
}
```

每个 id 唯一。断言描述可观察的正确性，避免要求某一句固定措辞。难以量化的文风留给人工偏好。把实际失败追加为任务；新增任务后重新比较两组，避免拿不同任务集的总分作结论。

`writing-docs`、`explain`、`unslop` 各有起始任务。执行器显式指定 skill，这些任务检验应用后的行为，不涵盖是否自动选中 skill。

## 隔离与验证边界

每次调用忽略用户配置和规则，关闭插件、连接应用、记忆及内置技能，禁用用户技能路径，并将项目指令读取上限设为 0。临时工作目录是独立 Git 仓库，避免向上发现开发仓库的指令。只有本次版本副本中的选定 skill 和依赖安装在任务目录中。

这控制的是上下文和输入版本，不是对恶意任务的文件系统安全隔离；Codex 只读 sandbox 仍允许读取本机部分文件。组织强制配置、模型服务更新和运行时负载也可能影响结果。记录并核对实际轨迹，不能仅凭新会话宣称环境完全一致。

本地运行器测试：

```bash
python3 -m unittest discover -s tests -v
```

这些测试在临时 Git 仓库中验证提交读取和当前源码的版本固定，并使用受控的假 CLI 检查调度、失败恢复和报告，不消耗模型配额。项目不配置 GitHub Actions；本地测试和模型评测都由维护者显式启动。

## 参考了哪些实现

- [Matt Pocock 的 skills 仓库](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/scripts)：沿用源码和开发脚本分开的组织方式。所检查版本提供链接、列举和版本同步脚本，未发现可直接采用的版本评测执行器。
- [Anthropic skill-creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)：参考固定任务、新旧快照、独立上下文、评分证据、重复结果及人工审阅的流程。
- [Anthropic 的评测结构](https://github.com/anthropics/skills/blob/main/skills/skill-creator/references/schemas.md)和[查看器实现](https://github.com/anthropics/skills/blob/main/skills/skill-creator/eval-viewer/generate_review.py)：参考将输出、评分和反馈保存在独立工作目录的做法。本项目没有复制其代码或声称兼容其全部 schema。
- [OpenAI 技能评测指南](https://developers.openai.com/blog/eval-skills)与[非交互运行文档](https://learn.chatgpt.com/docs/non-interactive-mode)：使用 `codex exec --json` 保存实际轨迹，并用结构化输出约束评分。

资料核对日期：2026-11-08。固定任务、旧版基线和人工审阅等流程参考上述项目。Git 提交入口、目录布局和 Codex 执行器由本项目自行实现，不是 Matt 的现成评测方案；不修改被测 skills 的规则来迎合评分。
