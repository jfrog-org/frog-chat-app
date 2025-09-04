from flask import render_template, redirect, url_for, session, request
from flask_socketio import join_room, leave_room, send, emit
from . import chat_blueprint, rooms
from project import socketio
import random
from string import ascii_uppercase
import base64
from PIL import Image, ImageMath
from io import BytesIO


def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        if code not in rooms:
            break
    return code


def make_alpha(data, color):
    try:
        dec_img = base64.b64decode(data)

        image = Image.open(BytesIO(dec_img)).convert('RGBA')
        img_bands = [band.convert('F') for band in image.split()]

        alpha = ImageMath.eval(
            f'''float(
                max(
                    max(
                        max(
                            difference1(red_band, {color[0]}),
                            difference1(green_band, {color[1]})
                        ),
                        difference1(blue_band, {color[2]})
                    ),
                    max(
                        max(
                            difference2(red_band, {color[0]}),
                            difference2(green_band, {color[1]})
                        ),
                        difference2(blue_band, {color[2]})
                    )
                )
            )''',
            difference1=lambda source, color: (source - color) / (255.0 - color),
            difference2=lambda source, color: (color - source) / color,
            red_band=img_bands[0],
            green_band=img_bands[1],
            blue_band=img_bands[2]
        )

        new_bands = [
            ImageMath.eval(
                'convert((image - color) / alpha + color, "L")',
                image=img_bands[i],
                color=color[i],
                alpha=alpha
            )
            for i in range(3)
        ]

        new_bands.append(ImageMath.eval(
            'convert(alpha_band * alpha, "L")',
            alpha=alpha,
            alpha_band=img_bands[3]
        ))

        new_image = Image.merge('RGBA', new_bands)
        background = Image.new('RGBA', new_image.size, (0, 0, 0, 0))
        background.paste(new_image, mask=new_image)

        buffer = BytesIO()
        background.save(buffer, format='PNG')

        return {
            'image': f'data:image/png;base64, {base64.b64encode(buffer.getvalue()).decode()}'
        }, 200
    except Exception as e:
        print(e)
        return '', 400


@chat_blueprint.route("/", methods=["GET", "POST"])
def home():
    print("Entered HOME")
    if 'username' in session:
        if request.method == "POST":
            code = request.form.get("code")
            join = request.form.get("join", False)
            create = request.form.get("create", False)
            print(f"code: {code}, join: {join}, create: {create}")
            if join != False and not code:
                return render_template("home.html", error="Please enter a room code.", code=code)
            room = code
            if create != False:
                room = generate_unique_code(4)
                rooms[room] = {"members": 0, "messages": []}
            elif code not in rooms:
                return render_template("home.html", error="Room doesn't exist.", code=code)
            session['room'] = room
            return redirect(url_for('chat.room'))

        return render_template("home.html")
    else:
        return redirect(url_for('auth.login'))


@chat_blueprint.route("/room", methods=["GET"])
def room():
    room = session.get("room")
    if room is None or session.get("username") is None or room not in rooms:
        return redirect(url_for("chat.home"))
    return render_template("room.html", code=room, messages=rooms[room]["messages"], is_admin=session.get('is_admin', False))


@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return
    content = {
        "username": session.get("username"),
        "message": data["data"]
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('username')} said: {data['data']}")


@socketio.on('file_upload')
def handle_file(data):
    file_data = data['file']
    filename = data['filename']
    color = data['color']  # Get the selected color in RGB format

    data_url = file_data.split(";")
    media_type = data_url[0].split('/')
    file_extension = media_type[1]

    # Determine file extension based on content type
    if not file_extension:
        file_extension = '.bin'  # Default to binary if content type is unknown

    b64_encoded_img = data_url[1].split(',')

    # Process the image with the selected color
    processed_image, status_code = make_alpha(b64_encoded_img[1], color)

    if status_code == 200:
        # Emit the processed image to the client
        emit('file_message', {'filename': filename, 'file': processed_image['image']}, broadcast=True)
    else:
        # Handle error
        emit('file_message', {'filename': filename, 'file': 'Error processing image'}, broadcast=True)


@socketio.on("connect")
def connect(auth):
    username = session['username']
    print(username)
    room = session['room']
    if not room or not username:
        return
    if room not in rooms:
        leave_room(room)
        return
    join_room(room)
    send({"username": username, "message": "has entered the room"}, to=room)
    rooms[room]["members"] += 1
    print(f"{username} joined room {room}")


@socketio.on("disconnect")
def disconnect():
    username = session['username']
    room = session['room']
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]

    send({"username": username, "message": "has entered the room"}, to=room)
    print(f"{username} has left room {room}")
