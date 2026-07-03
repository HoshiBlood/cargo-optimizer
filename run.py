from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from forms import CargoForm, TransportForm, TaskForm
from models import db, Cargo, Transport, LoadingTask, LoadingTaskCargo, Placement, Result
from datetime import datetime
from algorithm import calculate_loading, calculate_loading_preview
from dotenv import load_dotenv
import os

load_dotenv()  

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///instance/newflask.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    try:
        db.create_all()
        print("База данных успешно создана/подключена")
    except Exception as e:
        print(f"Ошибка создания БД: {e}")


@app.route("/")
@app.route("/index")
def index():
    tasks = LoadingTask.query.order_by(LoadingTask.created_at.desc()).limit(5).all()
    return render_template('index.html', tasks=tasks)


@app.route("/cargo", methods=['GET', 'POST'])
def cargo():
    form = CargoForm()
    if form.validate_on_submit():
        cargo = Cargo(
            name=form.name.data,
            length=form.length.data,
            width=form.width.data,
            height=form.height.data,
            weight=form.weight.data,
            quantity=form.quantity.data,
            is_stackable=form.is_stackable.data,
            fragile=form.fragile.data
        )
        db.session.add(cargo)
        db.session.commit()
        flash('Груз добавлен', 'success')
        return redirect(url_for('cargo'))
    cargos = Cargo.query.all()
    return render_template('cargo.html', form=form, cargos=cargos)

@app.route("/cargo/edit/<int:id>", methods=['GET', 'POST'])
def edit_cargo(id):
    cargo = Cargo.query.get_or_404(id)
    form = CargoForm(obj=cargo)
    if form.validate_on_submit():
        cargo.name = form.name.data
        cargo.length = form.length.data
        cargo.width = form.width.data
        cargo.height = form.height.data
        cargo.weight = form.weight.data
        cargo.quantity = form.quantity.data
        cargo.is_stackable = form.is_stackable.data
        cargo.fragile = form.fragile.data
        db.session.commit()
        flash('Груз обновлён', 'success')
        return redirect(url_for('cargo'))
    return render_template('cargo_edit.html', form=form, cargo=cargo)

@app.route("/cargo/delete/<int:id>")
def delete_cargo(id):
    cargo = Cargo.query.get_or_404(id)
    db.session.delete(cargo)
    db.session.commit()
    flash('Груз удалён', 'success')
    return redirect(url_for('cargo'))


@app.route("/transport", methods=['GET', 'POST'])
def transport():
    form = TransportForm()
    if form.validate_on_submit():
        transport = Transport(
            name=form.name.data,
            max_length=form.max_length.data,
            max_width=form.max_width.data,
            max_height=form.max_height.data,
            max_weight=form.max_weight.data
        )
        db.session.add(transport)
        db.session.commit()
        flash('Транспорт добавлен', 'success')
        return redirect(url_for('transport'))
    transports = Transport.query.all()
    return render_template('transport.html', form=form, transports=transports)

@app.route("/transport/edit/<int:id>", methods=['GET', 'POST'])
def edit_transport(id):
    transport = Transport.query.get_or_404(id)
    form = TransportForm(obj=transport)
    if form.validate_on_submit():
        transport.name = form.name.data
        transport.max_length = form.max_length.data
        transport.max_width = form.max_width.data
        transport.max_height = form.max_height.data
        transport.max_weight = form.max_weight.data
        db.session.commit()
        flash('Транспорт обновлён', 'success')
        return redirect(url_for('transport'))
    return render_template('transport_edit.html', form=form, transport=transport)

@app.route("/transport/delete/<int:id>")
def delete_transport(id):
    transport = Transport.query.get_or_404(id)
    db.session.delete(transport)
    db.session.commit()
    flash('Транспорт удалён', 'success')
    return redirect(url_for('transport'))

@app.route("/CreateTasks", methods=['GET', 'POST'])
def CreateTasks():
    form = TaskForm()
    form.transport.choices = [(t.id, t.name) for t in Transport.query.all()]
    
    if form.validate_on_submit():
        import json
        cargo_items = json.loads(request.form.get('cargo_items', '[]'))
        
        
        for item in cargo_items:
            cargo = Cargo.query.get(item['cargo_id'])
            if not cargo:
                flash(f'Груз с ID {item["cargo_id"]} не найден', 'danger')
                return redirect(url_for('CreateTasks'))
            
            if cargo.quantity < item['quantity']:
                flash(f'Недостаточно груза "{cargo.name}". Доступно: {cargo.quantity}, нужно: {item["quantity"]}', 'danger')
                return redirect(url_for('CreateTasks'))

        
        task = LoadingTask(
            transport_id=form.transport.data,
            status='pending'
        )
        db.session.add(task)
        db.session.commit()

        
        for item in cargo_items:
            task_cargo = LoadingTaskCargo(
                task_id=task.id,
                cargo_id=item['cargo_id'],
                quantity=item['quantity']
            )
            db.session.add(task_cargo)

        db.session.commit()

        
        calculate_loading(task.id)

        flash('Задача успешно создана и расчёт выполнен!', 'success')
        return redirect(url_for('LoadingTasks'))

    
    cargos = Cargo.query.all()
    return render_template('CreateTasks.html', form=form, cargos=cargos)


@app.route("/LoadingTasks")
def LoadingTasks():
    tasks = LoadingTask.query.order_by(LoadingTask.created_at.desc()).all()
    return render_template('LoadingTasks.html', tasks=tasks)

@app.route("/Details/<int:task_id>")
def Details(task_id):
    task = LoadingTask.query.get_or_404(task_id)
    placements = Placement.query.filter_by(task_id=task_id).all()
    result = Result.query.filter_by(task_id=task_id).first()
    return render_template('Details.html', task=task, placements=placements, result=result)

@app.route("/Result/<int:task_id>")
def result_page(task_id):
    return redirect(url_for('Details', task_id=task_id))


@app.route("/get_cargos")
def get_cargos():
    cargos = Cargo.query.all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'length': c.length,
        'width': c.width,
        'height': c.height,
        'weight': c.weight,
        'quantity': c.quantity,
        'is_stackable': c.is_stackable,
        'fragile': c.fragile
    } for c in cargos])

@app.route("/preview", methods=['POST'])
def preview():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Нет данных'}), 400
    transport_id = data.get('transport_id')
    cargo_items = data.get('cargo_items', [])
    if not transport_id:
        return jsonify({'error': 'Не выбран транспорт'}), 400
    try:
        efficiency, comment = calculate_loading_preview(transport_id, cargo_items)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify({'efficiency': round(efficiency, 2), 'comment': comment})

if __name__ == '__main__':
    app.run(debug=True)
