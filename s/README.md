# 抖店工作台 data.json 字段口径

## ⚠️ 必读：销售额字段不要填错

`data.json` 里的 `product.sales` 字段是 **CSV 直播间销售额**（**仅直播部分**），
**不是** CSV 销售额(元) 列。CSV 销售额(元) 列是直播+自营的预合并值，
**填进去会导致 totalGMV 多算一遍自营**（重复计算 75,582 左右）。

| CSV 列 | 含义 | 写入 data.json 的位置 |
|---|---|---|
| 销售额(元) | 直播+自营合并值 | ❌ **不要直接写入 product.sales** |
| 直播间销售额(元) | 仅直播 | ✅ `session.product.sales` |
| 店铺自营(元) | 仅自营 | ✅ `salesChannel.self.sales` |
| 支付订单数 | 支付订单 | ✅ `session.product.paymentOrders` |

## totalGMV 公式

```
totalGMV = Σ session.product.sales + Σ salesChannel.self.sales
        = 直播总销售 + 自营总销售
```

⚠️ **不是** 直播+自营+销售额(元)，**不是** 销售额(元) 累加。
CSV 销售额(元) 列是参考值，**不能进入 totalGMV**。

> ⚠️ 2026-08-14 实测注意：历史部分场次 `product.sales` 口径不一致（个别日曾填合并值），
> 因此 **totalGMV 应以 `salesChannels`（live+self）累加为准**，脚本里不要用
> `Σ product.sales` 当 totalGMV 来源。写入脚本正确写法：
> ```python
> totalGMV = Σ (salesChannels[].live.sales + salesChannels[].self.sales)
> # 校验：totalGMV == Σ (payment.android.amount + payment.ios.amount)
> ```

## 校验方法

每次写入后**必须**跑：

```bash
python3 s/validate.py
```

校验脚本会：
1. 检查 Σ product.sales 是否等于 CSV 直播间销售额累加
2. 检查 Σ self.sales 是否等于 CSV 店铺自营累加
3. 检查 totalGMV 是否等于 直播+自营
4. 输出 PASS / FAIL

> ⚠️ validate.py 的 CSV_CANDIDATES 是旧合并 CSV（7/02~7/28 等），
> 8 月手动贴入的数据不在其内——报「差额」= **8 月累计新增增量**（预期行为），
> 用「差额=新增行累加」对账即可，不是数据错误。

## 不允许的字段

- `salesChannel.live.orders` / `salesChannel.self.orders` ❌ CSV 没有此维度
- `session.product.orders` ❌ 同上，已废弃
- salesChannel 不需要拆 `live` 块（与 product.sales 重复）

## 当前数据快照（2026-08-28 更新）

来源：`E:\抖店数据_2026-07-02~2026-08-02.csv` + 8 月逐日 CSV/手动贴入
- **57 天数据（7/02~8/27）**
- 总GMV：¥859,186（直播 ¥509,988 + 自营 ¥349,198）
- 直播GMV：¥509,988
- 自营GMV：¥349,198
- 订单 1,260 / 付费用户 718 / 安卓占比 57.6%（健康，回落至临界线下方）
- 预估利润：¥656,418.10（利润率 76.4%）

### 更新记录

| 日期 | 内容 | 结果 |
|---|---|---|
| 2026-08-28 | 追加 8/27 巨兽战场直播日（直播25,840 + 自营23,362 = ¥49,202；安卓18,926/27人 + iOS30,276/13人（iOS主导）；订单65） | 57场，GMV 809,984→859,186，订单 1,195→1,260 |
| 2026-08-17 | 追加 8/14~8/16 三天（直播3322+1200+17582 + 自营2094+10048+7116=¥41,362；安卓3058+4260+19912 / iOS2358+6988+4786；订单70） | 46场，GMV 364,786→406,148，订单 512→582 |
| 2026-08-14 | 追加 8/13 巨兽战场直播日（直播2,588 + 自营1,066 = 3,654；安卓934/4人 + iOS2,720/6人；订单11） | 43场，GMV 361,132→364,786，订单 501→512 |
| 2026-08-11 | 8/12 巨兽战场直播日等（历史累计） | 42场，GMV 361,132 |
| 2026-08-11 | 实施反爬：data.json 加密为 data.enc（XOR+base64），明文 gitignore 不进仓库 | 线上仅密文 |
| 2026-07-28 | 7/02~7/28 CSV 全量导入（32天，GMV ¥257,220） | 32场 |

## 反爬加密（2026-08-11 实施）

- 线上文件：`s/data.enc`（XOR 流 + base64，密钥 `ENC_KEY` 与前端 index.html 一致）
- 明文 `s/data.json` 仅本地开发/更新脚本使用，已 `.gitignore` 不入仓库
- **改完 data.json 必须跑加密再推**：
  ```bash
  cd /mnt/c/temp/13yan.github.io   # 脚本在仓库根目录，不在 s/ 下！
  python3 encrypt_data.py          # 默认读 s/data.json 写 s/data.enc
  ```
- 推送时**只 add `s/data.enc`**，不要 `git add s/data.json`（会被 gitignore 拒绝，属预期）

## 写入流程（推荐）

1. 读 CSV（GBK/GB18030 编码，注意列名可能带全角括号/前导空格）
2. **先按行内「日期」列确认归属日期**（文件名日期常误导，如 抖店数据_0716.csv 实为 8/13 数据）
3. 构造 session + salesChannel 双写（product.sales=直播间销售额，self.sales=自营）
4. 重算 storeSummary（totalGMV 从 salesChannels 累加，勿用 product.sales）
5. 跑 `python3 s/validate.py` + 逐字段 CSV 对比脚本双校验
6. **先看本地数据**（不推），用户确认后说"推"
7. `python3 encrypt_data.py` → `git add s/data.enc` → 推 GitHub Pages
