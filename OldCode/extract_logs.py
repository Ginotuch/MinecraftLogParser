import os
import datetime
import gzip
import shutil

def extract(log_dir):
    print("Extracting logs", end="")
    c = 0
    for file in os.listdir(log_dir):
        if c == 0:
            print(".", end="")
        c = (c + 1) % ((datetime.datetime.now() - datetime.datetime.fromisoformat("2019-12-05")).days // 10)
        if os.path.isfile(os.path.join(log_dir, file)) and file[-2:].lower() == "gz" and not os.path.exists(os.path.join(log_dir, file[:-3])):
            with gzip.open(os.path.join(log_dir, file), 'rb') as f_in:
                with open(os.path.join(log_dir, file[:-3]), 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
    print("DONE")