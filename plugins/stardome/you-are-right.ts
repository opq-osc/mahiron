import { IMahiroUse } from 'mahiro'

const data: string[] = [
  '🦋随蝴蝶一起消散吧，🔪👩🏻​旧日的幻​影（次元斩）',
  '纠缠不清',
  '🌊就让你看看，​这葫芦里卖的是什么​药🌊⛄💦',
  '生存还是毁灭⚫️，你别无选择😎🎆​',
  '规则，就是原来打破的🏏✊',
  '煌煌威灵🗡🧝‍♂️，尊吾敕令👌🧖，斩⚡无⚡赦⚡​',
  '洞天幻化💫长梦一觉🍁🍂🗡️⚔️',
  '枪尖已经点​燃🗡🔥，炎枪，冲锋🤺🔥🔥🔥',
  '星星呀⭐️🌹向开拓者们赐予你真挚的祝福吧🥰',
  '冰雪筑成此志🥾永不终结！💪🧊',
  '略施小计😆试探就到此为止了❄️万剑天来🗡🗡🗡',
  '自摸加杠开，好牌不嫌晚🀄🀄🀄🀄，让我摸个鱼吧👧🏻👋🏻🐟，😖拜托拜托拜托!😆这不就，胡啦!🎆🎆🎆​',
  '我也想保护大家🥺帮帮我！史瓦罗先生！💪🤖😖，离开克拉拉🤖✋',
  `我想💺你可能还不明白🦵人类从不掩饰掌控星空的欲望🎉🎆当然，也包括我在内☕👌🏻👩🏻🛰️☄️🌍​`,
  '就让你看看😊这葫芦里买的是什么药😄🍐🌧',
  '星星啊🌟向开拓者们献上真挚的祝福吧🔨😀💫',
  '此番美景😏吾虽求而不得🌅却能，邀诸位共赏💥💥💥',
  '随蝴蝶一起消散吧🦋旧日的幻影🗡',
  '帮帮我😭史瓦罗先生💪🤖💪',
  '👨‍👨‍👦‍👦为了守护和捍卫👢击溃他们😡🏑',
  '生存还是毁灭🌑你别无选择😎💥💥💥​',
]

const match = ['?', '？', '吗', '吧', '对', '是的', '嗯']
const minLength = 10

const key = `stardome-you-are-right-v1`

export const StardomeYouAreRight = () => {
  const use: IMahiroUse = async (mahiro) => {
    const logger = mahiro.logger.withTag(
      'stardome-you-are-right'
    ) as typeof mahiro.logger

    const init = async () => {
      const values = await mahiro.db.kv.get(key)
      if (!values?.length) {
        logger.info('init all data')
        await mahiro.db.kv.set(key, data)
      } else {
        // diff
        const needPushData = data.filter((v) => !values.includes(v))
        if (needPushData.length) {
          const newData = [...values, ...needPushData]
          logger.info('add diff data ', newData?.length)
          await mahiro.db.kv.set(key, newData)
        }
      }
    }
    await init()

    let pending = false

    mahiro.onGroupMessage('你说的对', async (ctx) => {
      if (pending) {
        return
      }
      const msg = ctx?.msg?.Content?.trim()
      if (msg?.length < minLength) {
        return
      }
      const isMatch = match.some((v) => msg.endsWith(v))
      if (!isMatch) {
        return
      }
      const values = await mahiro.db.kv.get(key)
      const random = Math.floor(Math.random() * values.length)
      const reply = values[random]
      await mahiro.sendGroupMessage({
        groupId: ctx.groupId,
        msg: {
          Content: reply,
        },
      })
      // pending 5s
      pending = true
      setTimeout(() => {
        pending = false
      }, 5000)
    })
  }
  return use
}
