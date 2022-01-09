import time

from sqlalchemy.sql.expression import func

from app.models.user import User
from app.models.device import Device

from app import job_queue

def job_handler () -> None:
    while True:
        users = User.query.\
            join(User.devices)\
            .group_by(User.id)\
            .having(func.count(Device.id) > 0)\
        .all()

        for user in users:
            job_queue.resolve_jobs(user.id)

        job_queue.resolve_jobs(-1, priority=0)

        time.sleep(3)