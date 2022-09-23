async def friend_add(event, bot):
    if event.post_type != 'request':
        return
    if event.request_type != 'friend':
        return
    print('[!] 加好友请求 uid={}, 验证消息: {}'.format(str(event.user_id), event.comment))
    await bot.set_friend_add_request(flag = event.flag)