# task.py

import time
from celery import Celery, Task
import asyncio

import gevent.monkey
gevent.monkey.patch_all()

# 实例化一个Celery
broker = 'redis://localhost:6379/1'
backend = 'redis://localhost:6379/2'

# 参数1 自动生成任务名的前缀
# 参数2 broker 是我们的redis的消息中间件
# 参数3 backend 用来存储我们的任务结果的
app = Celery('celery_demo', broker=broker, backend=backend)

#
async def async_function(param1, param2):
    # more async stuff...
    print("enter async_function", param1, param2)
    await asyncio.sleep(1)
    pass

# 加入装饰器变成异步的函数
@app.task()
def add(x, y):
    print('Enter call function ...')

    loop = asyncio.get_event_loop()
    # Blocking call which returns when the hello_world() coroutine is done
    loop.run_until_complete(async_function(x, y))
    loop.close()

    time.sleep(1)
    return x + y


if __name__ == '__main__':
    # 这里生产的任务不可用，导入的模块不能包含task任务。会报错
    print("Start Task ...")
    # result = add.delay(1, 2)
    # #time.sleep(5)
    # print("result:", result)
    # print("result_status:",result.status)
    # #print("result:", result.get())

    # time.sleep(2)
    # time.sleep(2)
    # time.sleep(2)

    def on_result_ready(result):
        print('Received result for id %r: %r' % (result.id, result.result,))

    a, b = 1, 1
    r = add.delay(a, b).then(on_result_ready)

    print("----- before sleep 20s -----")
    time.sleep(20)
    print("----- after sleep 20s -----")

    # actively query
    # for i in range(0,100):
    #     print("---- loop {} -----".format(i))
    #     print(r.status)
    #     if r.status == "SUCCESS":
    #         print(r.get())
    #     time.sleep(1)

    # https://docs.celeryproject.org/en/4.0/whatsnew-4.0.html#asyncresult-then-on-success-on-error
    # https://docs.telethon.dev/en/latest/concepts/asyncio.html
    loop = asyncio.get_event_loop()  # get the default loop for the main thread
    try:
        # run the event loop forever; ctrl+c to stop it
        # we could also run the loop for three seconds:
        #     loop.run_until_complete(asyncio.sleep(3))
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    print("End Task ...")
    
