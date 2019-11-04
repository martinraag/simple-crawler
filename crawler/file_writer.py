from contextlib import contextmanager
import multiprocessing


END_TOKEN = "*"


def file_writer(write_queue, file_path, end_token):
    with open(file_path, "w") as out_file:
        while True:
            line = write_queue.get()
            if line == end_token:
                break
            out_file.write(line)
            out_file.write("\n")


@contextmanager
def create_file_writer(file_path):
    write_queue = multiprocessing.Queue()
    write_process = multiprocessing.Process(
        target=file_writer, args=(write_queue, file_path, END_TOKEN)
    )
    write_process.start()
    try:
        yield write_queue.put_nowait
    finally:
        write_queue.put_nowait(END_TOKEN)
        write_process.join()
