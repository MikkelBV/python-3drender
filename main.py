from engine import start, draw_world_object, load_model

box = load_model('models/box.json')
box.translate((-4, 0, 0))

def loop(canvas):
    draw_world_object(canvas, box)
    box.translate((1, 0, 0))

if __name__ == '__main__':
    start(loop)