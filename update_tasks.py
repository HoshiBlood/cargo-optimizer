from run import app, db
from models import LoadingTask, LoadingTaskCargo, Placement, Result

with app.app_context():
    print("LoadingTask count:", LoadingTask.query.count())
    print("LoadingTaskCargo count:", LoadingTaskCargo.query.count())
    print("Placement count:", Placement.query.count())
    print("Result count:", Result.query.count())