from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Cargo(db.Model):
    __tablename__ = 'cargo'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    length = db.Column(db.Float, nullable=False)
    width = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)

    weight = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=1)

    is_stackable = db.Column(db.Boolean, default=True)
    fragile = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Cargo {self.name}>"

class Transport(db.Model):
    __tablename__ = 'transport'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    max_length = db.Column(db.Float, nullable=False)
    max_width = db.Column(db.Float, nullable=False)
    max_height = db.Column(db.Float, nullable=False)

    max_weight = db.Column(db.Float, nullable=False)

    # связь с задачами
    tasks = db.relationship('LoadingTask', backref='transport', lazy=True)

    @property
    def volume(self):
        return self.max_length * self.max_width * self.max_height

    def __repr__(self):
        return f"<Transport {self.name}>"

#(Задача)
class LoadingTask(db.Model):
    __tablename__ = 'loading_task'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    transport_id = db.Column(db.Integer, db.ForeignKey('transport.id'), nullable=False)

    status = db.Column(db.String(20), default='pending')  # pending / done

   
    cargos = db.relationship('LoadingTaskCargo', backref='task', lazy=True)
    placements = db.relationship('Placement', backref='task', lazy=True)
    result = db.relationship('Result', backref='task', uselist=False)

    def __repr__(self):
        return f"<Task {self.id}>"

#Связь многие-ко-многим
class LoadingTaskCargo(db.Model):
    __tablename__ = 'loading_task_cargo'

    id = db.Column(db.Integer, primary_key=True)

    task_id = db.Column(db.Integer, db.ForeignKey('loading_task.id'), nullable=False)
    cargo_id = db.Column(db.Integer, db.ForeignKey('cargo.id'), nullable=False)

    quantity = db.Column(db.Integer, nullable=False)

    # связь с грузом
    cargo = db.relationship('Cargo')

    def __repr__(self):
        return f"<TaskCargo task={self.task_id} cargo={self.cargo_id}>"

#Размещение
class Placement(db.Model):
    __tablename__ = 'placement'

    id = db.Column(db.Integer, primary_key=True)

    task_id = db.Column(db.Integer, db.ForeignKey('loading_task.id'), nullable=False)
    cargo_id = db.Column(db.Integer, db.ForeignKey('cargo.id'), nullable=False)

    x = db.Column(db.Float, nullable=False)
    y = db.Column(db.Float, nullable=False)
    z = db.Column(db.Float, nullable=False)

    rotated = db.Column(db.Boolean, default=False)

    cargo = db.relationship('Cargo')

    def __repr__(self):
        return f"<Placement cargo={self.cargo_id}>"

#Результат
class Result(db.Model):
    __tablename__ = 'result'

    id = db.Column(db.Integer, primary_key=True)

    task_id = db.Column(db.Integer, db.ForeignKey('loading_task.id'), nullable=False, unique=True)

    used_volume = db.Column(db.Float)
    used_weight = db.Column(db.Float)
    efficiency = db.Column(db.Float)  # %

    comment = db.Column(db.Text)

    def __repr__(self):
        return f"<Result task={self.task_id}>"