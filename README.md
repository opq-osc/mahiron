# Mahiron

<div align="center">

### ❗️EOL

项目可正常运作，但不再提供维护，如有自定义需求可 fork 使用

</div>

一个 [Mahiro](https://github.com/opq-osc/mahiro) 的实践例子，包含 JavaScript 插件、Python 插件在同一项目里运行。

### Features

支持如下功能：

 - 牛了个牛
 - 早晚安
 - 表情包
 - 签到
 - 丢和爬
 - 运势holo版
 - 运势pcr版
 - meme （喜悲报）

> 所有 Python 源码出处可参考 `python/plugins/*/info.json` 文件。

### Usage

#### 环境

准备好 Nodejs `v18+` 、Python `v3.8+` 。

#### 安装依赖

```bash
  # install mahiro deps
  npm i -g pnpm
  pnpm i
 
  # install bridge deps
  pip install -r requirements.txt
```

#### 填写信息

在根目录创建 `.account.json` 并填写服务信息：

```json
{
  "host": "127.0.0.1",
  "account": 123456789
}
```

如需定制更多启动参数，请修改 [`index.ts`](./index.ts) 。

#### 启动

```bash
  # start mahiro
  pnpm start

  # start bridge
  python ./python/main.py
```

如需进一步定制，更多信息详见 [Mahiro 文档](https://mahiro.opqbot.com/) 。

### License

MIT
