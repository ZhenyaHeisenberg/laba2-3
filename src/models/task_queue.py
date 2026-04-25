from typing import Iterator
from src.contracts.message import Message
from src.models.task import Task


class TaskQueue:
    
    def __init__(self, source: Iterator[Task]):
        self._source = source
        self._buffer = []
    
    @classmethod
    def create_from(cls, source) -> "TaskQueue":
        """
        Создает очередь из api, json, sdin или generator.
        """
        def convert():
            if hasattr(source, 'fetch'):
                iterator = source.fetch()
            elif hasattr(source, 'generate'):
                iterator = source.generate()
            else:
                raise TypeError(f"Источник {type(source)} не поддерживает итерацию")
            for item in iterator:
                yield Task(
                    id=item.id,
                    description=getattr(item, "description"),
                    priority=getattr(item, "priority"),
                    status=getattr(item, "status")
                )
        return cls(convert())
    
    def __iter__(self) -> Iterator[Task]:
        yield from self._buffer
        
        for task in self._source:
            self._buffer.append(task)
            yield task
    
    def filter_by_status(self, status: str) -> "TaskQueue":
        def filtered():
            for task in self:
                if task.status == status:
                    yield task
        return TaskQueue(filtered())
    
    def filter_by_priority(self, min_priority: int = 1, max_priority: int = 5) -> "TaskQueue":
        def filtered():
            for task in self:
                if min_priority <= task.priority <= max_priority:
                    yield task
        return TaskQueue(filtered())
    
    def take(self, n: int) -> "TaskQueue":
        """
        Берет первые n задач.
        """
        def taked():
            count = 0
            for task in self:
                if count >= n:
                    break
                yield task
                count += 1
        return TaskQueue(taked())
    
    def __len__(self) -> int:
        return sum(1 for _ in self)