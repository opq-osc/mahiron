import { useMemo } from 'react'
import image1 from './assets/1.jpg'
import image2NOBG from './assets/2.no-bg.png'
import image2 from './assets/2.png'

import styles from './index.module.scss'
import { sample } from 'lodash'


const bgList = [
  image1,
  // image2,
]

export default function Page() {
  // max: 15
  const getData = () => {
    // const cover = `https://lain.bgm.tv/r/400/pic/cover/l/4d/86/347942_34Qor.jpg`
    // return Array(6).fill(cover)
    if (!window.BANGUMI?.length) {
      return []
    }
    if (!Array.isArray(window.BANGUMI)) {
      return []
    }
    return window.BANGUMI
  }
  const data = getData().slice(0, 15) as string[]

  const randomBg = useMemo(() => {
    return sample(bgList)
  }, [])

  const col = data.length <= 8 ? 4 : 5
  const itemWidth = col === 4 ? 150 : 130

  return (
    <div className={styles.box}>
      <div className={styles.left}>
        <img src={randomBg} />
      </div>
      <div className={styles.right}>
        <div className={styles.bgm}>
          <div className={styles.bgm_title}>{`今日番剧`}</div>
          <div
            className={styles.bgm_imgs}
            style={{
              gridTemplateColumns: `repeat(${col}, 1fr)`,
            }}
          >
            {data.map((item, idx) => {
              return (
                <div
                  key={`${item}-${idx}`}
                  className={styles.bgm_img}
                  style={{
                    width: itemWidth,
                  }}
                >
                  <img
                    src={item}
                    onError={(e) => {
                      // @ts-ignore
                      e.target.src = image2
                    }}
                  />
                </div>
              )
            })}
            {!data.length && (
              <div style={{ fontSize: 30, whiteSpace: 'nowrap' }}>暂无数据</div>
            )}
          </div>
          <img
            className={styles.bgm_bg}
            src={image2NOBG}
            style={{
              height:
                data.length <= 3
                  ? '80%'
                  : data.length <= 8
                  ? '45%'
                  : data.length <= 15
                  ? '35%'
                  : undefined,
            }}
          />
        </div>
        <div className={styles.tips}>
          {`·小提示：发送【领养真寻】即可获取真寻~ (〃∀〃)`}
        </div>
      </div>
    </div>
  )
}
