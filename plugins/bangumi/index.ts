import { IMahiroUse } from 'mahiro'
import { join } from 'path'
import nodeHtmlToImage from 'node-html-to-image'
import { existsSync, readFileSync, statSync } from 'fs'

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))
const avaliableGroups = new Set<number>()
let pending = false

export const Bangumi = () => {
  const mark2cron = {
    sun: '0 12 * * 0',
    mon: '0 12 * * 1',
    tue: '0 12 * * 2',
    wed: '0 12 * * 3',
    thu: '0 12 * * 4',
    fri: '0 12 * * 5',
    sat: '0 12 * * 6',
  }
  const bangumiPath = join(__dirname, './bangumi.json')
  const bangumi = JSON.parse(readFileSync(bangumiPath, 'utf-8')) as Record<string, string[]>
  const outputPath = join(__dirname, './output.png')
  
  const use: IMahiroUse = async (mahiro) => {
    const logger = mahiro.logger.withTag('bangumi') as typeof mahiro.logger
    logger.info('load bangumi plugin ...')

    const dayjs = mahiro.utils.dayjs
    const render = async (day: string) => {
      // if create time is today, use cache
      if (existsSync(outputPath)) {
        const stats = statSync(outputPath)
        const createTime = dayjs(stats.ctime)
        const today = dayjs()
        if (createTime.isSame(today, 'day')) {
          logger.info(`bangumi: use output cache for ${day}`)
          return true
        }
      }
  
      logger.info(`bangumi: render for ${day}`)
      const htmlPath = join(
        __dirname,
        './html/dist/index.html'
      )
      const value = bangumi[day].map((i: any) => `https://${i.url}`)
      const buffer = await nodeHtmlToImage({
        html: readFileSync(htmlPath, 'utf-8').replace('{{bangumi}}', JSON.stringify(value)),
        output: outputPath,
        puppeteerArgs: {
          args: ['--no-sandbox', '--disable-setuid-sandbox'],
        }
      })
      logger.info(`bangumi: render over for ${day}`)
      return buffer
    }

    const task = async (day: string, specifiedGroup?: number) => {
      // check group
      const willSendGroups = specifiedGroup ? [specifiedGroup] : Array.from(avaliableGroups)
      if (!willSendGroups.length) {
        logger.info(`bangumi: no group avaliable for ${day}`)
        return
      }

      try {
        logger.info(`bangumi: render for ${day}`)
        const buffer = await render(day)
        if (!buffer || !existsSync(outputPath)) {
          logger.error(`bangumi: render failed for ${day}`)
          throw new Error('render failed')
        }

        // render success, send to groups
        logger.success(`bangumi: render success for ${day}`)
        // waterfull call
        for await (const groupId of willSendGroups) {
          // sleep 1s
          await sleep(1000)
          logger.info(`bangumi: send to ${groupId}`)
          await mahiro.sendGroupMessage({
            groupId,
            fastImage: outputPath,
          })
          logger.success(`bangumi: send success to ${groupId}`)
        }
      } catch (e) {
        logger.error(`bangumi: render failed for ${day}`, e)
      }
    }

    const pluginKey = 'bangumi'
    mahiro.onGroupMessage(pluginKey, async ({ groupId, userId, msg }) => {
      avaliableGroups.add(groupId)

      // trigger immediately
      if (msg?.Content === '今日番剧') {
        if (pending) {
          logger.info(`bangumi: set cd for ${groupId}`)
          return
        }
        pending = true
        // 10 minutes later, reset pending
        setTimeout(() => {
          logger.info(`bangumi: reset cd for ${groupId}`)
          pending = false
        }, 10 * 60 * 1000)
        logger.info(`bangumi: trigger for ${groupId}`)
        const mark = dayjs().format('ddd').toLowerCase()
        task(mark, groupId)
      }
    })

    Object.keys(mark2cron).forEach((day) => {
      // register cron
      logger.info(`bangumi: register cron job for ${day}`)
      const cron = (mark2cron as any)[day]
      mahiro.cron.registerCronJob(cron, () => {
        logger.info(`bangumi: trigger cron job for ${day}`)
        task(day)
      })
    })
  }

  return use
}
