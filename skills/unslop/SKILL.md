---
name: unslop
description: 去掉任何文字中显露 AI 痕迹的表达。
disable-model-invocation: true
---

# 去掉 AI 味

编辑文本，去掉 AI 常见的表达模式。检查下面这些模式，然后改写。保留原意，并符合预期语气。

## 要识别和修正的模式

### 内容

1. **空泛的 -ing 短语。** 例如 “highlighting...”“ensuring...”“reflecting...”“showcasing...”“fostering...”。删除这些短语，或依据真实来源补充具体内容。
2. **模糊归因。** 例如“专家认为”“行业报告表明”“一些批评者主张”。明确来源，或者删除。

### 用词

3. **AI 惯用词。** Additionally、crucial、delve、enduring、enhance、fostering、garner、interplay、intricate、landscape（抽象用法）、pivotal、showcase、tapestry（抽象用法）、testament、underscore、vibrant。改用普通词语。
4. **把“是”说得花哨。** 例如 “serves as”“stands as”“boasts”“features”。直接用 “is” 或 “has”。
5. **“不仅是 X，更是 Y。”** 直接陈述要点。
6. **强凑三点。** 不要强行把观点分成三组。按内容自然决定数量。
7. **轮换同义词。** 在同一段中交替使用 protagonist、main character、central figure、hero 来称呼同一个主角。选定一个称呼，重复使用。
8. **虚假的范围。** 使用“从 X 到 Y”，但 X 和 Y 并不处于有意义的同一尺度上。直接列出主题。

### 文风

9. **滥用破折号。** 完全避免使用英文长破折号 em dash。只用句号或逗号替代，不用括号、英文短破折号 en dash，也不用连字符冒充破折号。如果一个意思需要分隔，就结束当前句子，或者使用逗号。
10. **滥用冒号。** 列表或示例前可以使用冒号，不要在句子中间把它当连接词。例如，“If you're coming from traditional automation: instead of registering event handlers, you describe conditions” 中的冒号没有增加任何内容。改写时去掉对比式铺垫，让要点独立成立：“Describing when the scheduler should fire works best as plain English.” 意思相同，也不需要借助多余标点。
11. **滥用粗体。** 不要给每个专有名词或缩写都加粗。
12. **带行内标题的列表。** 典型痕迹是加粗标签和冒号重复了后面的内容：“**Performance:** Performance improved...”。改成普通行文。如果加粗的引导语以句号结尾、点明对象，而且后面提供了真正的新信息，例如“**Schema in TypeScript.** Tables live in one file.”，则可以保留，这不属于 AI 痕迹。
13. **标题中每个主要单词都大写。** 改用句首字母大写的形式 sentence case。
14. **装饰性 emoji。** 从标题和列表项中删除。
15. **弯引号。** 使用直引号。

### 聊天式表达痕迹

16. **聊天机器人套话。** 例如 “I hope this helps!”“Let me know if...”“Of course!”“Certainly!”“Found the smoking gun!”。删除。
17. **奉承语气。** 例如“好问题！你完全正确！”。直接回答。

### 填充内容

18. **填充短语。** “In order to” 改成 “To”。“Due to the fact that” 改成 “Because”。删除 “It is important to note that”。
19. **过度犹豫。** “could potentially possibly be argued that it might” 改成 “may”。
20. **泛泛的结论。** 例如“未来一片光明”。改为陈述具体计划或事实。

### 术语

21. **抽象隐喻名词。** Substrate（可改用 base）、wedge、wedge in（可改用 add）、vector（可改用 way 或 method）、locus、vantage、nexus、用作名词的 primitive、隐喻用法的 harness、“API surface” 中的 surface、bedrock、隐喻用法的 scaffolding、modality、paradigm、gold-plating（可改成“超出任务所需”）、隐喻用法的 ratchet（改用机制的真实名称，或“只会收紧的限制”）、用 evacuate 表示移动代码（改用 move out）、endgame（改用“最后阶段”）、north star、flywheel。这些词读起来像技术术语，但通常都有更普通、具体的说法。选择具体的词。

### 直白表达

22. **说明它做什么，而不是描述它给人的感觉。** “the database stays close at hand”“SQL you can read”“types that follow your schema” 描述的是一种感觉。修改后的句子应说明机制或数字，例如“`.toSQL()` 返回实际发送给数据库的完整字符串”“重命名一列会导致构建失败”。先问这句话让读者知道什么，或让读者做什么，再把那个意思写出来。如果无法将它重述为具体指令、事实或数字，就删除。再检查一次：如果这句话可以原封不动地出现在另一个项目的文档里，它就没有说明当前项目的任何特点。删除。
23. **缩短或拆开密集的句子。** 如果读者必须回头重读才能理解句子，就把它拆成两句，或删掉部分分句。每句表达一个意思。
24. **主动语态。** 优先使用主动语态。识别 “is/are/was/were + 过去分词” 的结构，并指出执行者：“queries are validated” 改成 “the compiler validates queries”，“the file is parsed by the loader” 改成 “the loader parses the file”。只有执行者未知或确实无关紧要时，才可以使用被动语态。
25. **删掉副词，或换用更有力的动词。** “runs quickly” 改成 “is fast”，或者给出数字；“significantly improves” 改成实际测得的变化量。如果一个副词只是用来支撑无力的动词，就说明动词选错了。
26. **优先使用普通词。** “utilize” 和 “leverage” 改成 “use”，“facilitate” 改成 “help”，“numerous” 改成 “many”，“in the event that” 改成 “if”。更花哨的同义词很少更清楚。
27. **刻意雕琢的行文。** 明明有直接说法，却使用隐喻或修饰，例如格言式表达（“wire it or delete it”）、为了效果使用的修辞性碎片、把代码拟人化（“the plan holds it”）、比喻性动词（“rides along”“stands on”），以及固定的铺垫句式。“A dial worth turning” 改成 “a parameter worth varying”。直接说出你的意思。隐喻名词见规则 21。
28. **过度压缩。** 省略冠词、使用没有动词的碎片、用符号代替语言，以及使用缩写，都会让读者解码而不是阅读。“Parser rejects bad date → exit 2, no write” 改成 “The parser rejects a bad date, exits with code 2, and writes nothing.” 使用包含冠词和动词的完整句子，把箭头和缩写表达的意思写完整。
