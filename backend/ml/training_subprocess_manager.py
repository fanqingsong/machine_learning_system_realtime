# task.py

import time
from celery import shared_task
import asyncio
import subprocess, pprint


process = None


def _print_subprocess():
    print("enter _print_subprocess function")

    global process
    p = process
    if not p:
        print("process is not set")
        return

    while p.poll() is None:
        line = p.stdout.readline()
        line = line.strip()
        if line:
            print('Subprogram output: [{}]'.format(line))

    if p.returncode == 0:
        print('Subprogram success')
    else:
        print(p.returncode)
        print(p.pid)
        print('Subprogram failed')

        while True:
            line = p.stderr.readline()
            line = line.strip()
            if line:
                print('Subprogram output: [{}]'.format(line))


def _stop_subprocess():
    print('Enter _stop_subprocess function ...')
    global process

    if process:
        process.stdout.close()
        process.stderr.close()
        process.kill()
        process.wait()
        process = None
        print("old process killed")


def _start_subprocess(k):
    print('Enter _start_subprocess function ...')
    global process

    _stop_subprocess()

    cmd = ["python", "ml/training_subprocess.py", "CN-00015440.ericsson.se:2181", "1", "oneIrisData", "1", str(k)]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("process is created OK")
    pprint.pprint(process)

    _print_subprocess()

    return process.id



@shared_task
def start_subprocess(k):
    print('Enter start_subprocess function ...')

    _stop_subprocess()

    pid = _start_subprocess(k)

    _print_subprocess()

    return pid

@shared_task
def print_subprocess():
    print("enter print_subprocess function")

    _print_subprocess()

@shared_task
def stop_subprocess():
    print('Enter stop_subprocess function ...')

    _stop_subprocess()

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
    r = start_subprocess.delay(k)
    print("after start subprocess")

    # time.sleep(1)
    # print("now stop subprocess")
    # stop_subprocess.delay()

    time.sleep(10)
    print("print subprocess")
    print_subprocess.delay()

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
    
