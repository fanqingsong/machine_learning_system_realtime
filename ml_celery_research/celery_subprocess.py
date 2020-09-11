# task.py

import time
from celery import Celery, Task
import asyncio
import subprocess, pprint

# 实例化一个Celery
broker = 'redis://localhost:6379/1'
backend = 'redis://localhost:6379/2'

# 参数1 自动生成任务名的前缀
# 参数2 broker 是我们的redis的消息中间件
# 参数3 backend 用来存储我们的任务结果的
app = Celery('celery_subprocess', broker=broker, backend=backend)


process = None

# 加入装饰器变成异步的函数
@app.task()
def start_subprocess():
    print('Enter call function ...')
    global process

    cmd = ["sleep", "20s"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    pprint.pprint(process)

    return 0

@app.task()
def stop_subprocess():
    print('Enter call function ...')
    global process

    if process:
        process.stdout.close()
        process.stderr.close()
        process.kill()
        process.wait()
        print("old process killed")

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
    print("before start subprocess")
    r = start_subprocess.delay()
    print("after start subprocess")

    time.sleep(1)
    print("now stop subprocess")
    stop_subprocess.delay()

    #
    # print("----- before sleep 20s -----")
    # time.sleep(20)
    # print("----- after sleep 20s -----")

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
    
