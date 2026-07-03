from models import db, LoadingTask, Transport, Placement, Result, Cargo
import math

def can_place(box, container, placed_boxes, x, y, z, rotated=False):
    """Проверка пересечений"""
    dims = box['dimensions']
    l, w, h = (dims[1], dims[0], dims[2]) if rotated else dims
    
    if x + l > container['length'] or y + w > container['width'] or z + h > container['height']:
        return False
    
    for pb in placed_boxes:
        if not (x + l <= pb['x'] or pb['x'] + pb['l'] <= x or
                y + w <= pb['y'] or pb['y'] + pb['w'] <= y or
                z + h <= pb['z'] or pb['z'] + pb['h'] <= z):
            return False
    return True


def is_stable(x, y, z, l, w, h, placed_boxes):
    """Проверка стабильности груза"""
    if abs(z) < 0.01:  # на полу
        return True
    for pb in placed_boxes:
        if (abs(z - (pb['z'] + pb['h'])) < 0.02 and
            x + l > pb['x'] and x < pb['x'] + pb['l'] and
            y + w > pb['y'] and y < pb['y'] + pb['w']):
            return True
    return False


def find_position(box, container, placed_boxes, step=0.25):
    """Улучшенный поиск позиции"""
    dims = box['dimensions']
    
    for rotated in [False, True]:
        l, w, h = (dims[1], dims[0], dims[2]) if rotated else dims
        
        # Начинаем с нижних уровней
        for z in [i * step for i in range(int(container['height'] / step) + 1)]:
            if z + h > container['height']:
                continue
            for y in [i * step for i in range(int(container['width'] / step) + 1)]:
                for x in [i * step for i in range(int(container['length'] / step) + 1)]:
                    if can_place(box, container, placed_boxes, x, y, z, rotated):
                        if is_stable(x, y, z, l, w, h, placed_boxes):
                            return (x, y, z, rotated)
    return None


def calculate_loading(task_id):
    task = LoadingTask.query.get(task_id)
    if not task:
        return

    transport = Transport.query.get(task.transport_id)
    container = {
        'length': transport.max_length,
        'width': transport.max_width,
        'height': transport.max_height,
        'max_weight': transport.max_weight
    }

    items = []
    for tc in task.cargos:
        cargo = tc.cargo
        for _ in range(tc.quantity):
            items.append({
                'id': cargo.id,
                'dimensions': (cargo.length, cargo.width, cargo.height),
                'weight': cargo.weight,
                'fragile': cargo.fragile,
                'stackable': cargo.is_stackable
            })

    items.sort(key=lambda x: x['dimensions'][0] * x['dimensions'][1] * x['dimensions'][2], reverse=True)

    placed_boxes = []
    used_weight = 0.0

    for item in items:
        if used_weight + item['weight'] > container['max_weight']:
            continue

        box = {
            'dimensions': item['dimensions'],
            'weight': item['weight'],
            'fragile': item['fragile'],
            'stackable': item['stackable']
        }

        pos = find_position(box, container, placed_boxes, step=0.25)
        if pos:
            x, y, z, rotated = pos
            l, w, h = (box['dimensions'][1], box['dimensions'][0], box['dimensions'][2]) if rotated else box['dimensions']
            
            placed_boxes.append({
                'cargo_id': item['id'],
                'x': round(x, 3), 'y': round(y, 3), 'z': round(z, 3),
                'l': l, 'w': w, 'h': h,
                'rotated': rotated,
                'weight': item['weight']
            })
            used_weight += item['weight']

    Placement.query.filter_by(task_id=task.id).delete()
    for pb in placed_boxes:
        placement = Placement(
            task_id=task.id,
            cargo_id=pb['cargo_id'],
            x=pb['x'], y=pb['y'], z=pb['z'],
            rotated=pb['rotated']
        )
        db.session.add(placement)

    used_volume = sum(pb['l'] * pb['w'] * pb['h'] for pb in placed_boxes)
    total_volume = container['length'] * container['width'] * container['height']
    efficiency = min((used_volume / total_volume) * 100, 100) if total_volume > 0 else 0

    result = Result.query.filter_by(task_id=task.id).first()
    if result:
        result.used_volume = used_volume
        result.used_weight = used_weight
        result.efficiency = efficiency
        result.comment = f"Загружено {len(placed_boxes)} из {len(items)} единиц."
    else:
        result = Result(
            task_id=task.id,
            used_volume=used_volume,
            used_weight=used_weight,
            efficiency=efficiency,
            comment=f"Загружено {len(placed_boxes)} из {len(items)} единиц."
        )
        db.session.add(result)

    task.status = 'done'
    db.session.commit()


def calculate_loading_preview(transport_id, cargo_items):
    """Preview версии"""
    transport = Transport.query.get(transport_id)
    if not transport:
        return 0, "Транспорт не найден"

    container = {
        'length': transport.max_length,
        'width': transport.max_width,
        'height': transport.max_height,
        'max_weight': transport.max_weight
    }

    items = []
    for ci in cargo_items:
        cargo = Cargo.query.get(ci['cargo_id'])
        if cargo:
            for _ in range(ci['quantity']):
                items.append({
                    'dimensions': (cargo.length, cargo.width, cargo.height),
                    'weight': cargo.weight,
                    'fragile': cargo.fragile,
                    'stackable': cargo.is_stackable
                })

    items.sort(key=lambda x: x['dimensions'][0] * x['dimensions'][1] * x['dimensions'][2], reverse=True)
    placed_boxes = []
    used_weight = 0.0

    for item in items:
        if used_weight + item['weight'] > container['max_weight']:
            continue
        pos = find_position(item, container, placed_boxes, step=0.25)
        if pos:
            x, y, z, rotated = pos
            l, w, h = (item['dimensions'][1], item['dimensions'][0], item['dimensions'][2]) if rotated else item['dimensions']
            placed_boxes.append({'l': l, 'w': w, 'h': h, 'weight': item['weight']})
            used_weight += item['weight']

    used_volume = sum(pb['l'] * pb['w'] * pb['h'] for pb in placed_boxes)
    total_volume = container['length'] * container['width'] * container['height']
    efficiency = min((used_volume / total_volume) * 100, 100) if total_volume > 0 else 0
    comment = f"Загружено {len(placed_boxes)} из {len(items)} единиц."

    return efficiency, comment