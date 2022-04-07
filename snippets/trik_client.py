import sys
import time
import random
import math


if __name__ == '__main__':
  # mailbox.connect("127.0.0.1", 8891)
  mailbox.connect("192.168.4.1", 8889)
#  time.sleep(1)
  print("connected")

  for i in range(10):
    print(f"sending {i}")
    mailbox.send(42, f"hello{i}")

    print(f"receiving {i}")
    message = mailbox.receive()
    print(message)

    i += 1
    time.sleep(.3)

  print("done")
