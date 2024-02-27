const lightModeToggle = document.getElementById("light-mode-toggle");
let isDarkMode = false;

lightModeToggle.addEventListener("click", () => {
  isDarkMode = !isDarkMode;

  if (isDarkMode) {
    document.body.style.backgroundColor = "#0c001f";
  } else {
    document.body.style.backgroundColor = "#e4d9f5";
  }
});
// Function to display modal when OpenAI Key link is clicked
document.getElementById("openAIKeyLink").addEventListener("click", function () {
  $("#openAIKeyModal").modal("show");
});

// Function to save OpenAI Key to localStorage
function sendAndSaveOpenAIKey() {
  var openAIKey = document.getElementById("openAIKeyInput").value;

  fetch("/api/openAIKeyInput", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      key: openAIKey,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      var status = data.status;
      if (status === true) {
        localStorage.setItem("openAIKey", openAIKey);
        document.getElementById("keyStatus").className = "d-none";
        document.getElementById("keyStatus").innerHTML = "Ok";
        $("#openAIKeyModal").modal("hide");
      } else {
        document.getElementById("keyStatus").className = "d-inline";
        document.getElementById("keyStatus").innerHTML =
          "Invalid OpenAI API Key";
      }
    });
}

// Dictionary to store thread ids and their respective chat history
var threadChatHistory = {};
var activeThread = "";
var msg = "";
// Retrieve stored chat history from local storage
function loadChatHistory() {
  var storedData = localStorage.getItem("threadChatHistory");
  if (storedData) {
    threadChatHistory = JSON.parse(storedData);
  }
}

// Save chat history to local storage
function saveChatHistory() {
  localStorage.setItem("threadChatHistory", JSON.stringify(threadChatHistory));
}
// function getChatHistory() {
//   fetch("/api/chat_history", {
//     method: "GET",
//     headers: {
//       "Content-Type": "application/json",
//     },
//   })
//     .then((response) => response.json())
//     .then((data) => {

//       if (data.status === "Ok") {
//         msg = "";
//         streamResponse();
//       } else {
//         //Display Error, but it's will never false :D
//       }
//     });
// }

function switchThread(threadId) {
  // Load chat messages for the selected thread
  displayChatHistory(threadId);

  // Update the activeThread
  activeThread = threadId;
  fetch("/api/getUuid", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      uuid: activeThread,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      var uuid = data.uuid;
      history.pushState({}, "", "/thread/" + uuid);
    });
}

// Function to display chat history
function displayChatHistory(threadId) {
  var messages = threadChatHistory[threadId] || [];
  var messageContainer = document.getElementById("messageContainer");
  messageContainer.innerHTML = ""; // Clear existing messages

  messages.forEach(function (message) {
    var messageElement = document.createElement("div");
    messageElement.className =
      message.role === "user" ? "user-message" : "response-message";
    messageElement.innerText = message.content;

    messageContainer.appendChild(messageElement);
  });
}

function sendMessage() {
  // var status = document.getElementById("keyStatus").innerHTML;
  // if (status !== "Ok") {
  //   $("#openAIKeyModal").modal("show");
  //   return;
  // }

  var userMessage = document.getElementById("messageInput").value;
  if (userMessage === "") {
    return;
  }

  // Create a user message element
  var userMessageElement = document.createElement("div");
  userMessageElement.className = "user-message";
  userMessageElement.innerText = userMessage;

  // Append the user message to the message container
  document.getElementById("messageContainer").appendChild(userMessageElement);

  // Make a POST request to the server
  fetch("/api/completion", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message: userMessage,
      thread_id: activeThread,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      var responseMessageElement = document.createElement("div");
      responseMessageElement.className = "response-message";
      responseMessageElement.innerText = data.message;

      document
        .getElementById("messageContainer")
        .appendChild(responseMessageElement);

      // Update the chat history for the active thread
      threadChatHistory[activeThread] = data.chat_history;

      // Save chat history to local storage
      saveChatHistory();
    });

  document.getElementById("messageInput").value = "";
}
function sendMessageToBot() {
  // var status = document.getElementById("keyStatus").innerHTML;
  // if (status !== "Ok") {
  //   $("#openAIKeyModal").modal("show");
  //   return;
  // }

  var userMessage = document.getElementById("messageInput").value;
  if (userMessage === "") {
    return;
  }

  // Create a user message element
  var userMessageElement = document.createElement("div");
  userMessageElement.className = "user-message";
  userMessageElement.innerText = userMessage;

  // Append the user message to the message container
  document.getElementById("messageContainer").appendChild(userMessageElement);

  // Make a POST request to the server
  fetch("/api/interview-bot", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message: userMessage,
      thread_id: activeThread,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      var responseMessageElement = document.createElement("div");
      responseMessageElement.className = "response-message";
      responseMessageElement.innerText = data.message;

      document
        .getElementById("messageContainer")
        .appendChild(responseMessageElement);

      // Update the chat history for the active thread
      threadChatHistory[activeThread] = data.chat_history;

      // Save chat history to local storage
      saveChatHistory();
    });

  document.getElementById("messageInput").value = "";
}
function generateImage() {
  // var status = document.getElementById("keyStatus").innerHTML;
  // if (status !== "Ok") {
  //   $("#openAIKeyModal").modal("show");
  //   return;
  // }

  var userMessage = document.getElementById("messageInput").value;
  if (userMessage === "") {
    return;
  }

  // Create a user message element
  var userMessageElement = document.createElement("div");
  userMessageElement.className = "user-message";
  userMessageElement.innerText = userMessage;

  // Append the user message to the message container
  document.getElementById("messageContainer").appendChild(userMessageElement);

  // Make a POST request to the server
  fetch("/api/image-generator", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message: userMessage,
      thread_id: activeThread,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      var responseMessageElement = document.createElement("div");
      responseMessageElement.className = "response-message";
      //responseMessageElement.innerText = "Click to Open image: ";
      var linkText = document.createTextNode("Click to Open image: ");
      responseMessageElement.appendChild(linkText);

      var imageLink = document.createElement("a");
      imageLink.href = data.message;
      imageLink.target = "_blank";
      imageLink.innerText = "Open in new tab";
      //var linkText = document.createTextNode("Open in new tab");
      responseMessageElement.appendChild(imageLink);

      var image = document.createElement("img");
      image.src = data.message;
      image.alt = "OpenAI dall-e";
      image.height = 600;
      image.width = 600;

      responseMessageElement.appendChild(image);

      document
        .getElementById("messageContainer")
        .appendChild(responseMessageElement);

      // Update the chat history for the active thread
      threadChatHistory[activeThread] = data.chat_history;

      // Save chat history to local storage
      saveChatHistory();
    });

  document.getElementById("messageInput").value = "";
}

function sendMessageTTS() {
  // var status = document.getElementById("keyStatus").innerHTML;
  // if (status !== "Ok") {
  //   $("#openAIKeyModal").modal("show");
  //   return;
  // }

  var userMessage = document.getElementById("messageInput").value;
  if (userMessage === "") {
    return;
  }

  // Create a user message element
  var userMessageElement = document.createElement("div");
  userMessageElement.className = "user-message";
  userMessageElement.innerText = userMessage;

  // Append the user message to the message container
  document.getElementById("messageContainer").appendChild(userMessageElement);

  // Make a POST request to the server
  fetch("/api/speech", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message: userMessage,
      thread_id: activeThread,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      var responseMessageElement = document.createElement("div");
      responseMessageElement.className = "response-message";

      var audioElement = document.createElement("audio");
      audioElement.controls = true;

      var sourceElement = document.createElement("source");
      sourceElement.src = "/static/" + data.message;
      sourceElement.type = "audio/mpeg";
      audioElement.appendChild(sourceElement);

      responseMessageElement.appendChild(audioElement);

      document
        .getElementById("messageContainer")
        .appendChild(responseMessageElement);

      // Update the chat history for the active thread
      threadChatHistory[activeThread] = data.chat_history;

      // Save chat history to local storage
      saveChatHistory();
    });

  document.getElementById("messageInput").value = "";
}

function sendMedia() {
  // var status = document.getElementById("keyStatus").innerHTML;
  // if (status !== "Ok") {
  //   $("#openAIKeyModal").modal("show");
  //   return;
  // }

  var fileInput = document.getElementById("fileInput");
  var submitFile = fileInput.files[0];
  if (!submitFile) {
    return;
  }

  // Create a user message element
  var userMessageElement = document.createElement("div");
  userMessageElement.className = "user-message";

  var fileLink = document.createElement("a");
  fileLink.href = URL.createObjectURL(submitFile);
  fileLink.download = submitFile.name;
  fileLink.innerText = submitFile.name;

  userMessageElement.appendChild(fileLink);
  // Append the user message to the message container
  document.getElementById("messageContainer").appendChild(userMessageElement);

  var formData = new FormData();
  formData.append("fileInput", submitFile);
  formData.append("thread_id", activeThread);
  // Make a POST request to the server
  fetch("/api/audio-to-text", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      var responseMessageElement = document.createElement("div");
      responseMessageElement.className = "response-message";

      responseMessageElement.innerText = data.message;
      document
        .getElementById("messageContainer")
        .appendChild(responseMessageElement);

      // Update the chat history for the active thread
      threadChatHistory[activeThread] = data.chat_history;

      // Save chat history to local storage
      saveChatHistory();
    });

  document.getElementById("messageInput").value = "";
}

function streamResponse() {
  source = new EventSource("/api/stream");
  source.addEventListener("message", function (e) {
    if (e.data === "finisheddd") {
      console.log("closing cnt");
      source.close();
      //saveChatHistory();
    } else {
      msg += e.data;
      console.log("Received a message: ", msg);
      var messageContainer = document.getElementById("messageContainer");
      var responseMessageElement = document.createElement("div");

      responseMessageElement.className = "response-message";
      var length = messageContainer.children.length;
      //Check if there are any existing elements
      if (
        length > 0 &&
        messageContainer.children[length - 1].className === "response-message"
      ) {
        // Remove the last element
        messageContainer.removeChild(messageContainer.lastChild);
      }

      responseMessageElement.innerText = msg;
      document
        .getElementById("messageContainer")
        .appendChild(responseMessageElement);
    }
  });
}
function sendMessageStream() {
  // var status = document.getElementById("keyStatus").innerHTML;
  // if (status !== "Ok") {
  //   $("#openAIKeyModal").modal("show");
  //   return;
  // }

  var userMessage = document.getElementById("messageInput").value;
  if (userMessage === "") {
    return;
  }

  // Create a user message element
  var userMessageElement = document.createElement("div");
  userMessageElement.className = "user-message";
  userMessageElement.innerText = userMessage;

  // Append the user message to the message container
  document.getElementById("messageContainer").appendChild(userMessageElement);

  // Make a POST request to the server
  fetch("/api/stream", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message: userMessage,
      thread_id: activeThread,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "Ok") {
        msg = "";
        streamResponse();
      } else {
        //Display Error, but it's will never false :D
      }
    });

  document.getElementById("messageInput").value = "";
}
// Function to create a new thread
function createNewThread() {
  var newThreadId = "thread" + (Object.keys(threadChatHistory).length + 1);

  // Create a new entry in the threadChatHistory dictionary
  threadChatHistory[newThreadId] = [];

  var listItem = document.createElement("li");
  listItem.className = "list-group-item p-3";
  listItem.innerText = "New Thread " + Object.keys(threadChatHistory).length;
  listItem.onclick = function () {
    switchThread(newThreadId);
  };

  document.getElementById("threadList").appendChild(listItem);

  // Switch to the new thread
  switchThread(newThreadId);
}

loadChatHistory();
