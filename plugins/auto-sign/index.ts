import { IMahiroUse } from 'mahiro'

interface IAutoSignOptions {
  group: number
}

export const AutoSign = (opts: IAutoSignOptions) => {
  const { group } = opts

  const use: IMahiroUse = async (mahiro) => {
    const logger = mahiro.logger.withTag('auto-sign') as typeof mahiro.logger

    if (!group) {
      logger.error('auto sign group is required')
      throw new Error('auto sign group is required')
    }

    // register cron job, send message every day at 00:30
    const CRON = '30 0 * * *'
    mahiro.cron.registerCronJob(CRON, async () => {
      logger.info(`Auto sign cron job triggered`)
      try {
        await mahiro.sendGroupMessage({
          groupId: group,
          msg: {
            Content: `签到`,
          },
        })
      } catch (e) {
        logger.error(`Auto sign failed`, e)
      }
    })
    
    logger.info(`Auto sign plugin loaded, group: ${group}`)
  }

  return use
}
