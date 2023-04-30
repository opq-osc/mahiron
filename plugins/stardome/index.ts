import { IMahiroUse } from 'mahiro'

const keywords = [
  'qp',
  'QP',
  '星奴',
  '星批',
  '⭐️批',
  '⭐️奴',
  '星穹',
  '铁道',
  '星铁',
]
const hasKeywords = (s: string) => keywords.some((k) => s.includes(k))
const countKey = `stardome_count_v3`
const msgKey = `stardome_msg_v3_`

export const Stardome = () => {
  const use: IMahiroUse = async (mahiro) => {
    const logger = mahiro.logger.withTag('stardome') as typeof mahiro.logger

    mahiro.onGroupMessage('stardome', async (ctx) => {
      const content = ctx?.msg?.Content
      if (content?.length) {
        const isMatch = hasKeywords(content)
        if (isMatch) {
          const msg = await randomSingle()
          if (msg?.length) {
            mahiro.sendGroupMessage({
              groupId: ctx?.groupId,
              msg: {
                Content: msg,
              },
            })
          }
          return
        }

        const isAdmin = await mahiro.db.isGroupAdmin({
          groupId: ctx?.groupId,
          userId: ctx?.userId,
        })
        if (isAdmin) {
          if (content?.startsWith('添加攻略')) {
            const msg = content.slice('添加攻略'.length).trim()
            if (msg?.length) {
              const total = await setSingle(msg)
              mahiro.sendGroupMessage({
                groupId: ctx?.groupId,
                msg: {
                  Content: `添加成功，当前攻略总数：${total}`,
                },
              })
            }
          }
        }
      }
    })

    async function setSingle(msg: string) {
      const lines = msg.split('\r').filter(i => i.trim()?.length)
      const count = lines.length
      // set to db
      let startIndex = await mahiro.db.kv.get(countKey)
      if (startIndex != null) {
        startIndex = Number(startIndex)
      } else {
        startIndex = 0
      }
      let nextIndex = startIndex
      for await (const [index, line] of lines.entries()) {
        nextIndex = startIndex + index
        await mahiro.db.kv.set(msgKey + nextIndex, line.trim())
      }
      logger.info(
        `setSingle count: ${count}, startIndex: ${startIndex}, nextIndex: ${nextIndex}`
      )
      await mahiro.db.kv.set(countKey, nextIndex + 1)
      return nextIndex + 1
    }

    async function randomSingle() {
      let count = await mahiro.db.kv.get(countKey)
      if (count != null) {
        count = Number(count)
      } else {
        // not record
        return
      }
      const index = Math.floor(Math.random() * count)
      const msg = await mahiro.db.kv.get(msgKey + index)
      if (msg?.length) {
        return msg
      }
      // not found ?
      logger.warn(`randomSingle not found, index: ${index}, count: ${count}`)
    }
  }

  return use
}
