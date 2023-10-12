from queue import Queue 

def queue_from_list(list_:list[str]) -> Queue:
    """
    Description: Converts a list into a queue

    Args:
        list_ (list[str]): List to convert

    Returns:
        Queue: Queue
    """
    queue_ = Queue()
    for element in list_:
        queue_.put(element)
    return queue_

def list_from_queue(queue_:Queue) -> list[str]:
    """
    Description: Converts a queue into a list

    Args:
        queue_ (Queue): Queue to convert

    Returns:
        list[str]: List
    """
    list_ = []
    while queue_ and not queue_.empty():
        list_.append(queue_.get())
    return list_

def new_empty_queue() -> Queue:
    """
    Description: Returns a new empty queue

    Returns:
        Queue: New empty queue
    """
    return Queue()