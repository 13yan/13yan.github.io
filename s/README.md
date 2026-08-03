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

## 不允许的字段

- `salesChannel.live.orders` / `salesChannel.self.orders` ❌ CSV 没有此维度
- `session.product.orders` ❌ 同上，已废弃
- salesChannel 不需要拆 `live` 块（与 product.sales 重复）

## 当前数据快照

来源：`E:\抖店数据_2026-07-02~2026-08-02.csv`（合并 CSV）
- 32 天数据（7/02~8/02）
- 总GMV：¥257,220（直播 ¥114,470 + 自营 ¥142,750）
- 直播GMV：¥114,470
- 自营GMV：¥142,750
- 订单 344 / 付费用户 192 / 安卓占比 49.6%（健康）

## 写入流程（推荐）

1. 复制 CSV 到 `E:\抖店数据_YYYY-MM-DD~YYYY-MM-DD.csv`
2. 跑导入脚本（或手动写入 data.json）
3. 跑 `python3 s/validate.py` 校验
4. **先看本地数据**（不推），用户确认后说"推"
5. 走 Windows gh CLI 推 GitHub Pages
