from run import app, db
from models import Transport, Cargo

with app.app_context():
   
    gaz = Transport(
        name="ГАЗель",
        max_length=3.0,
        max_width=1.8,
        max_height=1.8,
        max_weight=1500
    )
    db.session.add(gaz)
    
    cargo1 = Cargo(
        name="Коробка с книгами",
        length=0.5, width=0.4, height=0.3,
        weight=20, quantity=10, is_stackable=True, fragile=False
    )
    cargo2 = Cargo(
        name="Монитор",
        length=0.6, width=0.5, height=0.1,
        weight=5, quantity=5, is_stackable=True, fragile=True
    )
    cargo3 = Cargo(
        name="Ящик с деталями",
        length=1.0, width=0.8, height=0.6,
        weight=100, quantity=3, is_stackable=True, fragile=False
    )
    cargo4 = Cargo(
        name="Стеклянная панель",
        length=1.2, width=0.8, height=0.05,
        weight=30, quantity=2, is_stackable=False, fragile=True
    )
    cargo5 = Cargo(
        name="Паллета",
        length=1.2, width=1.0, height=1.2,
        weight=200, quantity=1, is_stackable=False, fragile=False
    )
    db.session.add_all([cargo1, cargo2, cargo3, cargo4, cargo5])
    db.session.commit()
    print("Данные добавлены")