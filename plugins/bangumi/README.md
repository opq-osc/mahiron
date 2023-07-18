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

### Troubleshooting

若 puppeteer 运行报错，可以一步一步安装基础库排查，缺啥装啥。

#### `libatk-1.0.so.0` 错误

```bash
apt-get install -yq gconf-service libasound2 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libnss3 lsb-release xdg-utils wget
```

#### `libgbm.so.1` 错误

```bash
apt-get install -yq libgbm1
```
