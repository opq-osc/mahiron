from mahiro import Mahiro

mahiro = Mahiro()

# plugins
from plugins.chinchin_pk_mahiro.main import chinchin_pk
from plugins.opqqq_plugins_mahiro.src.bot_good_morning import bot_good_morning
from plugins.opqqq_plugins_mahiro.src.bot_image_custom import bot_image_custom
from plugins.opqqq_plugins_mahiro.src.bot_sign_in import bot_sign_in
from plugins.opqqq_plugins_mahiro.src.bot_throw_creep import bot_throw_creep
from plugins.opqqq_plugins_mahiro.src.bot_vtuber_fortune import bot_vtuber_fortune
from plugins.opqqq_plugins_mahiro.src.bot_pcr_fortune import bot_pcr_fortune

# load plugins
mahiro.container.add_group(id="牛了个牛", callback=chinchin_pk)
mahiro.container.add_group(id="早晚安", callback=bot_good_morning)
mahiro.container.add_group(id="表情包", callback=bot_image_custom)
mahiro.container.add_group(id="签到", callback=bot_sign_in)
mahiro.container.add_group(id="丢和爬", callback=bot_throw_creep)
mahiro.container.add_group(id="运势holo版", callback=bot_vtuber_fortune)
mahiro.container.add_group(id="运势pcr版", callback=bot_pcr_fortune)

# load firend plugin
# from plugins.friend_simple_mahiro.main import friend_simple_mahiro

# mahiro.container.add_friend(id="friend_simple_mahiro", callback=friend_simple_mahiro)

# run
mahiro.run()
