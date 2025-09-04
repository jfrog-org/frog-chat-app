var socketio = io();

const messages = document.getElementById("messages");

// XSS
const createMessage = (username, msg) => {
  const messageDiv = document.createElement("div");
  messageDiv.className = "message";
  messageDiv.innerHTML = `
    <span class="username"><strong>${username}</strong>:</span>
    <span class="text">${msg}</span>
    <span class="timestamp">${new Date().toLocaleString()}</span>
  `;
  messages.appendChild(messageDiv);
  // Scroll to the bottom
  messages.scrollTop = messages.scrollHeight;
};

socketio.on("message", (data) => {
  createMessage(data.username, data.message);
});

const sendMessage = () => {
  const message = document.getElementById("message");
  if (message.value == "") return;
  socketio.emit("message", { data: message.value });
  message.value = "";
};


function uploadFile() {
  var isAdmin = document.getElementById('isAdmin').value === 'True';
  if (!isAdmin) {
    alert('You are not authorized to upload images.'); // Display alert if user is not an admin
    return;
  }
  
  var fileInput = document.getElementById('file-upload');
  var file = fileInput.files[0];
  var reader = new FileReader();

  reader.onload = function(e) {
      var filename = file.name;
      var fileContent = e.target.result;
      var colorPicker = document.getElementById('colorPicker');
      console.log(colorPicker.value)
      var color = hexToRgb(colorPicker.value); // Convert hex color to RGB

      // Emit a SocketIO event with the filename, file content, and selected color
      socketio.emit('file_upload', {'filename': filename, 'file': fileContent, 'color': color});
  };

  reader.readAsDataURL(file);
}

// Function to convert hexadecimal color to RGB
function hexToRgb(hex) {
    // Remove the leading # if it exists
    hex = hex.replace(/^#/, '');

    // Parse the hexadecimal string into three integer values for R, G, and B
    var bigint = parseInt(hex, 16);
    var r = (bigint >> 16) & 255;
    var g = (bigint >> 8) & 255;
    var b = bigint & 255;

    return [r, g, b];
}

socketio.on('file_message', function(data) {
    var messages = document.getElementById('messages');
    messages.innerHTML += '<p><img src="' + data.file + '" alt="Uploaded Image" style="max-width: 400px;"></p>';
});