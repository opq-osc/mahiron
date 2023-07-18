# bangumi

mahiro bangumi 插件。

### 启用步骤

构建 html 模板：

```bash
  cd ./html
  pnpm i
  pnpm build
```

收集最新的 bangumi 数据：

```bash
  pnpm mahiro ./sync.ts
```

得到 `./html/dist/index.html` 和 `./bangumi.json` 即可启用：

```ts
import { Bangumi } from './plugins/bangumi'

// ...

mahiro.use(Bangumi())
```

### 配置方法

在 mahiro 管理面板中添加需要使用的群组即可，每日 `12:00` 自动播报，或通过 `今日番剧` 手动触发，CD 为 `10` 分钟。
