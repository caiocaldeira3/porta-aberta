import time
import dataclasses as dc

from typing import Union
from flask_socketio import emit, send
from abc import ABCMeta, ABC, abstractmethod

from app.util.exc import (
    JobResolutionConfigurationError, MissingChatId, NotJobInstance, PriorityRangeError
)

RequestData = dict[str, Union[str, dict[str, str]]]
MAX_RETRIES = 5
MIN_PRIORITY = 0
MAX_PRIORITY = 3

@dc.dataclass(init=True)
class Job (ABC):

    user_id: int = dc.field(init=True, default=None)
    data: RequestData = dc.field(init=True, default=None)
    retries: int = dc.field(init=True, default=0)
    priority: int = dc.field(init=True, default=0)

    @abstractmethod
    def solve (self) -> None:
        pass

    def increment_retries (self) -> int:
        self.retries += 1

        return self.retries

    def identify_job_type (self) -> None:
        print(type(self))

class RefreshJob (Job):
    def solve (self) -> None:
        from app import api

        api.logout()
        time.sleep(0.5)
        api.login()

class CreateChatJob (Job):
    def solve (self) -> None:
        emit("create-chat", self.data)

class ConfirmCreateChatJob (Job):
    def solve (self) -> None:
        emit("confirm-create-chat", self.data)

class SendMessageJob (Job):
    def solve (self) -> None:
        send(self.data)

class ConfirmMessageJob (Job):
    def solve (self) -> None:
        emit("confirm-message", self.data)

Jobs = Union[list[Job], dict[str, list[Job]]]

@dc.dataclass(init=True)
class JobQueue:
    job_dict: dict[int, list[Jobs]] = dc.field(init=False, default_factory=dict)

    def add_job (
        self, user_id: int, priority: int,
        job_class: ABCMeta, data: RequestData = None, chat_id: int = None, retries: int = 0
    ) -> None:
        if not isinstance(job_class(), Job):
            raise NotJobInstance

        job = job_class(user_id, data, priority, retries)

        if self.job_dict.get(user_id, None) is None:
            self.job_dict[user_id] = [ list(), list(), dict() ]

        if MIN_PRIORITY <= priority <= 1:
            self.job_dict[user_id][priority].append(job)

        elif priority == 2:
            if chat_id is None:
                raise MissingChatId

            elif self.job_dict[user_id][priority].get(chat_id, None) is None:
                self.job_dict[user_id][priority][chat_id] = []

            self.job_dict[user_id][priority][chat_id].append(job)

        else:
            raise PriorityRangeError

    def _resolve_jobs (self, jobs: list[Job]) -> list[Job]:
        failed_jobs = []

        for job in jobs:
            try:
                job.solve()

            except ConnectionRefusedError:
                if job.increment_retries() < MAX_RETRIES:
                    failed_jobs.append(job)

            except Exception as exc:
                print(f"Ill formed job of type {type(job)}")
                print(exc)

        return failed_jobs

    def resolve_jobs (self, user_id: int, priority: int = None, chat_id: int = None) -> None:
        if priority is None and chat_id is not None:
            raise JobResolutionConfigurationError

        elif self.job_dict.get(user_id, None) is None:
            return

        elif priority is None:
            for curr_priority in range(MIN_PRIORITY, MAX_PRIORITY):
                self.resolve_jobs(user_id, priority=curr_priority)

            return

        if MIN_PRIORITY <= priority <= 1:
            if priority > MIN_PRIORITY and len(self.job_dict[user_id][priority - 1]) > 0:
                return

            l = self._resolve_jobs(self.job_dict[user_id][priority])
            self.job_dict[user_id][priority] = l

        elif priority == 2 and chat_id is not None:
            if priority > MIN_PRIORITY and len(self.job_dict[user_id][priority - 1]) > 0:
                return

            failed_jobs = self._resolve_jobs(self.job_dict[user_id][priority].get(chat_id, []))

            if len(failed_jobs) > 0:
                self.job_dict[user_id][priority][chat_id] = failed_jobs

        elif priority == 2 and chat_id is None:
            for chat_id in self.job_dict[user_id][priority].keys():
                self.resolve_jobs(user_id, 2, chat_id)

        else:
            raise PriorityRangeError


        for curr_priority in range(MIN_PRIORITY, MAX_PRIORITY):
            if len(self.job_dict[user_id][curr_priority]) > 0:
                return

        self.job_dict.pop(user_id, None)