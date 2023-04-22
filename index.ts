import { Mahiro } from 'mahiro'
import { join } from 'path'

const account = require(join(__dirname, './.account.json'))

const run = async () => {
  const mahiro = await Mahiro.start({
    host: account.host,
    qq: account.qq,
  })

  // use mahiro
  mahiro
}

run()
