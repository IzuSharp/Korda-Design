# Database lifecycle 研究独立审查

**结论：通过本轮有限研究代码、D15 变更与来源审查。独立 Linux 复跑 6/6 个具名测试通过，37/37 项输入与来源核查通过，无当前阻断缺陷。** 本报告不接受 C-TX-001 或任何产品 Delivery。

## 身份与精确范围

审查者 `/root/migration_evidence` 与作者 `/root/design_source_review` 为本会话不同子代理；审查者未修改本 DB 补丁。D15 的版本号由整合者 `/root` 调整。本次独立性是本会话子代理的作者/审查者分离，不是另一 GitHub 账号的 approval，也不能替代服务端 required review/checks。

范围为 the historical research fixture、`docs/database/sqlx-retirement-study.md` 和 D15 `docs/database/transactions-and-pooling.md` 的变更部分。逐文件清单保存在同名 JSON，59 个文件清单 SHA256 为 `8a0dcd3821bea1fdd541c9ed88a347a36e4cea89c0e2379d333c9195f860372e`；其算法是对 files 数组按 JSON key 排序、紧凑分隔符序列化后取 UTF-8 SHA256。当前观察到的工作区 HEAD 为 `b6c3a7c9161edc4949b2d05c3c2443f074f3f0e5`；后续 CI 的真实来源身份另行核查，不用该本地 HEAD 替代。

## 逐项测试与设计判断

1. **Transaction Drop → 返池。** 使用连接本地 TEMP marker 证明重新取得的是同一物理连接；同时确认未提交行缺失。不能用意外新建的干净 SQLite 连接蒙混通过。
2. **提前丢弃 row stream。** SeaQuery 实际构造 SELECT，经 SQLx 在容量 1 的 row channel 中获取第一行后丢弃 stream，随后同连接 count 和 marker 查询成功。此测试验证有限普通查询的清理与复用；没有声称每轮已观测 worker 停在某一条阻塞指令，也没有证明任意 `sqlite3_step` 可立即被中断。
3. **取消 acquire waiter。** 明确先 poll 到 Pending，再丢弃 waiter、释放唯一借出连接，随后可重新取得同一连接且池大小仍为 1。
4. **已 dispatch 的 COMMIT 丢失确认。** 真实 SQLite commit hook 向测试发出 entered 信号后阻塞；测试此时丢弃应用等待 Future，再释放 hook。后续实际 SELECT 看到已提交行，之后普通 rollback 也没有撤销它。该反例足以反驳“drop/取消等待就等于 RolledBack”，没有冒充 PostgreSQL 线协议故障注入。阻塞 hook 有明确 TEST-ONLY 标记，错误路径丢弃 sender 也能释放 worker。
5. **progress callback 状态替换。** 旧操作被实际 progress handler 中断，移除 handler 后检查捕获引用释放；新操作使用新状态，旧 flag 的迟到变化不影响它。此为顺序替换的真实证据，文档没有将其升级为全部 callback/managed cancellation race 的证明。
6. **pool close。** 观察 close 先 Pending、拒绝新 acquire，待借出 owner 释放后池大小归零。文档正确保留“pool/Shutdown response 不等于 OS JoinHandle”边界。

D15 从 0.2.0-draft 增为 0.2.1-draft，保留 proposed 与新内容 hash 需要重新 review 的要求。变更把 SeaORM trait 限制在明确选择的 profile，并让 benchmark 比较同一选定 native 栈；普通 SeaQuery+SQLx 路径不被强制经过 SeaORM。新增有限 SQLite 证据没有替代 PostgreSQL、跨语言资源退休、NativeAOT 或正式验收义务。

## 上游源码与 registry 包的独立核对

独立读取并重新通过 GitHub GET 取得 SQLx 固定 commit `75bc0487eb661da811bb7a3c5d158f1bd463fef4` 的六个选定文件；重新计算 Git blob SHA1 与 SHA256，和本地 registry 实际编译文件逐字比对，均一致。实时 GET 原文保存在 `database-live-upstream.json`，其 SHA256 为 `de0732c2156bef4967615580cabeed1fdd8e04256118a151d6cefbdcea4aba99`。

还独立对 sqlx、sqlx-core、sqlx-sqlite、sea-query、tokio 五个实际 `.crate` archive 计算 SHA256，均与 Cargo.lock checksum 相等。新 lock 与旧迁移 fixture 的依赖闭包一致，除 root package 名由 `nw-database-boundary-probe` 改为 `nw-database-retirement-probe` 外，没有升级依赖。

源码明确支持文档中的关键区分：COMMIT 成功但 rendezvous ack 丢失时，worker 会忽略随后 Drop 触发的 rollback；row receiver 结束通过 send 失败停止后续迭代；`start_rollback` 和 `shutdown` 存在同步 bounded-channel send；Shutdown 在 drop 连接引用后发送响应、随后才从线程闭包返回。因而 cooperative timeout 不是任意同步阻塞的硬抢占，shutdown acknowledgment 也不是独立 OS thread-join 证明。

registry 包声明 packaging commit `003b698e99e024f3621b8043a2426fde5b741171`，不同于所选源码 Git pin。作者文档和本报告都仅断言六个文件的字节一致；没有 whole-package Git 等同、签名验证或完整上游审计声称。

## 独立执行证据与保留失败

作者的 attempt 1 保留了 unused-dependencies lint 导致的真实失败；attempt 2 将 test-only 依赖正确移到 dev-dependencies 后通过；attempt 3 加强旧 flag 迟到与六个具名结果的验证后通过。三次源输入副本及其 hash、日志和成功/失败状态均已逐项核对，未覆盖失败证据。

后续四 job GitHub CI 的 archive digest、源 commit 和 Windows checkout 行尾关系另记 `SOURCE-LIFECYCLE-CI-REVIEW.json`，不把本次 Linux 本地结果冒充 GitHub 或 Windows 结果。未执行的 PostgreSQL、C# AOT DB adapter、硬取消时限、线程 join、弱内存及产品验收仍保持未证明。
