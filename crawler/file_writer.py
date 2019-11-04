from contextlib import contextmanager
import multiprocessing


END_TOKEN = "*"


def file_writer(write_queue, file_path, end_token):
    """Opens a file for writing and reads content to write from a queue until a token signifiying
    the end of the process is retrieved."""

    with open(file_path, "w") as out_file:
        while True:
            line = write_queue.get()
            if line == end_token:
                break
            out_file.write(line)
            out_file.write("\n")


@contextmanager
def create_file_writer(file_path):
    """A context manager that creates a process for writing to a file in the given path. Yields
    a function that enqueues a string to be written to file by the process."""

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
