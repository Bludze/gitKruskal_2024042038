# 贡献指南

感谢你对 Kruskal MST Visualizer 的关注！本文档说明如何参与本项目的开发与讨论。

## 行为准则

参与本项目即表示你同意遵守 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。

## 如何提问

- 提交 Issue 前，请先搜索是否已有相同问题
- 缺陷类问题请使用「Bug report」模板，附上复现步骤、期望结果、实际结果与运行环境
- 功能建议请使用「Feature request」模板，说明使用场景与预期收益

## 如何提交代码

1. 从 `main` 分支创建功能分支，命名建议：
   - 新功能：`feature/简短描述`
   - 缺陷修复：`fix/简短描述`
   - 文档改进：`docs/简短描述`
2. 保持提交信息清晰，推荐使用 `feat:`、`fix:`、`docs:`、`test:` 前缀
3. 提交前在本地运行测试：

   ```bash
   pip install -r requirements.txt
   pytest -q
   ```

4. 向 `main` 发起 Pull Request，填写 PR 模板，说明改动内容与验证方式
5. 至少一位维护者 Review 通过后合并

## 代码风格

- Python：遵循 PEP 8，保持现有代码的命名与注释风格
- C：保持现有代码的缩进（Tab）、注释与函数命名风格
- 注释使用中文，与现有代码保持一致

## 分支保护

`main` 分支受保护：禁止直接推送，所有改动必须通过 Pull Request 合并。

## 报告安全问题

如发现安全相关问题，请勿公开提交 Issue，直接联系维护者。